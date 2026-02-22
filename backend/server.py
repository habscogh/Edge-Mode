from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr, ConfigDict, validator
from typing import List, Optional
import uuid
from datetime import datetime, timezone, timedelta
import bcrypt
import jwt
from dateutil import parser as date_parser

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

app = FastAPI()
api_router = APIRouter(prefix="/api")
security = HTTPBearer()

JWT_SECRET = os.environ.get('JWT_SECRET', 'forge-secret-key-change-in-production')
JWT_ALGORITHM = 'HS256'

PILLARS = [
    "Fitness/Training",
    "Sports Practice",
    "Study/Academics",
    "Skill Development",
    "Reading/Learning",
    "Personal Project",
    "Discipline Habits"
]

# Models
class UserRegister(BaseModel):
    email: EmailStr
    username: str
    password: str
    age: int

    @validator('age')
    def validate_age(cls, v):
        if v < 12 or v > 19:
            raise ValueError('Age must be between 12 and 19')
        return v

    @validator('username')
    def validate_username(cls, v):
        if len(v) < 3:
            raise ValueError('Username must be at least 3 characters')
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    email: str
    username: str
    age: int
    join_date: str
    current_streak: int = 0
    longest_streak: int = 0
    subscription_active: bool = False
    last_log_date: Optional[str] = None
    leaderboard_opt_in: bool = False

class UserPillar(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    user_id: str
    pillar_name: str
    weekly_target_minutes: int

class PillarSetup(BaseModel):
    pillar_name: str
    weekly_target_minutes: int

class OnboardingComplete(BaseModel):
    pillars: List[PillarSetup]

    @validator('pillars')
    def validate_pillars(cls, v):
        if len(v) < 3 or len(v) > 5:
            raise ValueError('Must select between 3 and 5 pillars')
        for pillar in v:
            if pillar.pillar_name not in PILLARS:
                raise ValueError(f'Invalid pillar: {pillar.pillar_name}')
        return v

class DailyLog(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    user_id: str
    pillar: str
    date: str
    minutes_logged: int

class LogEntry(BaseModel):
    pillar: str
    minutes_logged: int

class WeeklyStats(BaseModel):
    consistency_pct: float
    target_completion_pct: float
    performance_index: float
    total_minutes: int
    days_logged: int
    pillars_data: List[dict]

class Group(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    name: str
    type: str
    created_by: str
    members: List[str]
    created_at: str

class GroupCreate(BaseModel):
    name: str
    type: str = "private"

class LeaderboardEntry(BaseModel):
    username: str
    consistency_pct: float
    performance_index: float
    age_group: str

# Auth helpers
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_token(user_id: str) -> str:
    payload = {
        'user_id': user_id,
        'exp': datetime.now(timezone.utc) + timedelta(days=30)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get('user_id')
        user = await db.users.find_one({'id': user_id}, {'_id': 0, 'password': 0})
        if not user:
            raise HTTPException(status_code=401, detail='User not found')
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail='Token expired')
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail='Invalid token')

# Streak calculation helper
async def update_streak(user_id: str, log_date: str):
    user = await db.users.find_one({'id': user_id}, {'_id': 0})
    if not user:
        return
    
    log_dt = datetime.fromisoformat(log_date).replace(tzinfo=timezone.utc)
    today = datetime.now(timezone.utc).date()
    
    if user.get('last_log_date'):
        last_log_dt = datetime.fromisoformat(user['last_log_date']).replace(tzinfo=timezone.utc)
        hours_diff = (log_dt - last_log_dt).total_seconds() / 3600
        
        if hours_diff > 48:
            current_streak = 1
        elif log_dt.date() > last_log_dt.date():
            current_streak = user.get('current_streak', 0) + 1
        else:
            current_streak = user.get('current_streak', 1)
    else:
        current_streak = 1
    
    longest_streak = max(current_streak, user.get('longest_streak', 0))
    
    await db.users.update_one(
        {'id': user_id},
        {'$set': {
            'current_streak': current_streak,
            'longest_streak': longest_streak,
            'last_log_date': log_date
        }}
    )

# Routes
@api_router.post("/auth/register")
async def register(user_data: UserRegister):
    existing = await db.users.find_one({'email': user_data.email}, {'_id': 0})
    if existing:
        raise HTTPException(status_code=400, detail='Email already registered')
    
    user_id = str(uuid.uuid4())
    user_doc = {
        'id': user_id,
        'email': user_data.email,
        'username': user_data.username,
        'password': hash_password(user_data.password),
        'age': user_data.age,
        'join_date': datetime.now(timezone.utc).isoformat(),
        'current_streak': 0,
        'longest_streak': 0,
        'subscription_active': False,
        'last_log_date': None,
        'leaderboard_opt_in': False
    }
    
    await db.users.insert_one(user_doc)
    token = create_token(user_id)
    
    return {'token': token, 'user_id': user_id}

@api_router.post("/auth/login")
async def login(credentials: UserLogin):
    user = await db.users.find_one({'email': credentials.email}, {'_id': 0})
    if not user or not verify_password(credentials.password, user['password']):
        raise HTTPException(status_code=401, detail='Invalid credentials')
    
    token = create_token(user['id'])
    return {'token': token, 'user_id': user['id']}

@api_router.get("/users/me", response_model=User)
async def get_me(current_user: dict = Depends(get_current_user)):
    return User(**current_user)

@api_router.get("/pillars")
async def get_available_pillars():
    return {'pillars': PILLARS}

@api_router.post("/onboarding/complete")
async def complete_onboarding(data: OnboardingComplete, current_user: dict = Depends(get_current_user)):
    user_id = current_user['id']
    
    existing = await db.user_pillars.find({'user_id': user_id}, {'_id': 0}).to_list(100)
    if existing:
        raise HTTPException(status_code=400, detail='Onboarding already completed')
    
    for pillar_setup in data.pillars:
        pillar_doc = {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'pillar_name': pillar_setup.pillar_name,
            'weekly_target_minutes': pillar_setup.weekly_target_minutes
        }
        await db.user_pillars.insert_one(pillar_doc)
    
    return {'message': 'Onboarding complete'}

@api_router.get("/users/pillars", response_model=List[UserPillar])
async def get_user_pillars(current_user: dict = Depends(get_current_user)):
    pillars = await db.user_pillars.find({'user_id': current_user['id']}, {'_id': 0}).to_list(100)
    return [UserPillar(**p) for p in pillars]

@api_router.post("/logs", response_model=DailyLog)
async def create_log(log_data: LogEntry, current_user: dict = Depends(get_current_user)):
    user_id = current_user['id']
    today = datetime.now(timezone.utc).date().isoformat()
    
    user_pillars = await db.user_pillars.find({'user_id': user_id}, {'_id': 0}).to_list(100)
    pillar_names = [p['pillar_name'] for p in user_pillars]
    
    if log_data.pillar not in pillar_names:
        raise HTTPException(status_code=400, detail='Invalid pillar for this user')
    
    existing_log = await db.daily_logs.find_one({
        'user_id': user_id,
        'pillar': log_data.pillar,
        'date': today
    }, {'_id': 0})
    
    if existing_log:
        new_minutes = existing_log['minutes_logged'] + log_data.minutes_logged
        await db.daily_logs.update_one(
            {'id': existing_log['id']},
            {'$set': {'minutes_logged': new_minutes}}
        )
        log_doc = {**existing_log, 'minutes_logged': new_minutes}
    else:
        log_doc = {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'pillar': log_data.pillar,
            'date': today,
            'minutes_logged': log_data.minutes_logged
        }
        await db.daily_logs.insert_one(log_doc)
    
    await update_streak(user_id, datetime.now(timezone.utc).isoformat())
    
    return DailyLog(**log_doc)

@api_router.get("/logs/today")
async def get_today_logs(current_user: dict = Depends(get_current_user)):
    today = datetime.now(timezone.utc).date().isoformat()
    logs = await db.daily_logs.find({
        'user_id': current_user['id'],
        'date': today
    }, {'_id': 0}).to_list(100)
    return logs

@api_router.get("/stats/weekly", response_model=WeeklyStats)
async def get_weekly_stats(current_user: dict = Depends(get_current_user)):
    user_id = current_user['id']
    today = datetime.now(timezone.utc).date()
    week_start = today - timedelta(days=today.weekday())
    
    logs = await db.daily_logs.find({
        'user_id': user_id,
        'date': {'$gte': week_start.isoformat()}
    }, {'_id': 0}).to_list(1000)
    
    user_pillars = await db.user_pillars.find({'user_id': user_id}, {'_id': 0}).to_list(100)
    
    unique_days = set(log['date'] for log in logs)
    days_logged = len(unique_days)
    consistency_pct = (days_logged / 7) * 100
    
    total_minutes = sum(log['minutes_logged'] for log in logs)
    total_target = sum(p['weekly_target_minutes'] for p in user_pillars)
    target_completion_pct = min((total_minutes / total_target * 100) if total_target > 0 else 0, 100)
    
    performance_index = min((consistency_pct * 0.7) + (target_completion_pct * 0.3), 100)
    
    pillars_data = []
    for pillar in user_pillars:
        pillar_logs = [l for l in logs if l['pillar'] == pillar['pillar_name']]
        pillar_minutes = sum(l['minutes_logged'] for l in pillar_logs)
        pillars_data.append({
            'pillar_name': pillar['pillar_name'],
            'minutes_logged': pillar_minutes,
            'target_minutes': pillar['weekly_target_minutes'],
            'completion_pct': min((pillar_minutes / pillar['weekly_target_minutes'] * 100) if pillar['weekly_target_minutes'] > 0 else 0, 100)
        })
    
    return WeeklyStats(
        consistency_pct=round(consistency_pct, 1),
        target_completion_pct=round(target_completion_pct, 1),
        performance_index=round(performance_index, 1),
        total_minutes=total_minutes,
        days_logged=days_logged,
        pillars_data=pillars_data
    )

@api_router.get("/groups", response_model=List[Group])
async def get_user_groups(current_user: dict = Depends(get_current_user)):
    groups = await db.groups.find(
        {'members': current_user['id']},
        {'_id': 0}
    ).to_list(100)
    return [Group(**g) for g in groups]

@api_router.post("/groups", response_model=Group)
async def create_group(group_data: GroupCreate, current_user: dict = Depends(get_current_user)):
    group_doc = {
        'id': str(uuid.uuid4()),
        'name': group_data.name,
        'type': group_data.type,
        'created_by': current_user['id'],
        'members': [current_user['id']],
        'created_at': datetime.now(timezone.utc).isoformat()
    }
    await db.groups.insert_one(group_doc)
    return Group(**group_doc)

@api_router.get("/groups/{group_id}/leaderboard")
async def get_group_leaderboard(group_id: str, current_user: dict = Depends(get_current_user)):
    group = await db.groups.find_one({'id': group_id}, {'_id': 0})
    if not group or current_user['id'] not in group['members']:
        raise HTTPException(status_code=404, detail='Group not found')
    
    leaderboard = []
    for member_id in group['members']:
        user = await db.users.find_one({'id': member_id}, {'_id': 0, 'password': 0})
        if not user:
            continue
        
        today = datetime.now(timezone.utc).date()
        week_start = today - timedelta(days=today.weekday())
        
        logs = await db.daily_logs.find({
            'user_id': member_id,
            'date': {'$gte': week_start.isoformat()}
        }, {'_id': 0}).to_list(1000)
        
        user_pillars = await db.user_pillars.find({'user_id': member_id}, {'_id': 0}).to_list(100)
        
        unique_days = set(log['date'] for log in logs)
        days_logged = len(unique_days)
        consistency_pct = (days_logged / 7) * 100
        
        total_minutes = sum(log['minutes_logged'] for log in logs)
        total_target = sum(p['weekly_target_minutes'] for p in user_pillars)
        target_completion_pct = min((total_minutes / total_target * 100) if total_target > 0 else 0, 100)
        
        performance_index = min((consistency_pct * 0.7) + (target_completion_pct * 0.3), 100)
        
        leaderboard.append({
            'username': user['username'],
            'consistency_pct': round(consistency_pct, 1),
            'performance_index': round(performance_index, 1),
            'current_streak': user.get('current_streak', 0)
        })
    
    leaderboard.sort(key=lambda x: x['performance_index'], reverse=True)
    return leaderboard

@api_router.get("/leaderboard/global")
async def get_global_leaderboard(age_group: Optional[str] = None, category: Optional[str] = None):
    query = {'leaderboard_opt_in': True}
    
    if age_group:
        age_ranges = {
            '12-14': (12, 14),
            '15-17': (15, 17),
            '18-19': (18, 19)
        }
        if age_group in age_ranges:
            min_age, max_age = age_ranges[age_group]
            query['age'] = {'$gte': min_age, '$lte': max_age}
    
    users = await db.users.find(query, {'_id': 0, 'password': 0}).to_list(1000)
    
    leaderboard = []
    today = datetime.now(timezone.utc).date()
    week_start = today - timedelta(days=today.weekday())
    
    for user in users:
        logs = await db.daily_logs.find({
            'user_id': user['id'],
            'date': {'$gte': week_start.isoformat()}
        }, {'_id': 0}).to_list(1000)
        
        user_pillars = await db.user_pillars.find({'user_id': user['id']}, {'_id': 0}).to_list(100)
        
        unique_days = set(log['date'] for log in logs)
        days_logged = len(unique_days)
        consistency_pct = (days_logged / 7) * 100
        
        total_minutes = sum(log['minutes_logged'] for log in logs)
        total_target = sum(p['weekly_target_minutes'] for p in user_pillars)
        target_completion_pct = min((total_minutes / total_target * 100) if total_target > 0 else 0, 100)
        
        performance_index = min((consistency_pct * 0.7) + (target_completion_pct * 0.3), 100)
        
        age = user['age']
        if age <= 14:
            user_age_group = '12-14'
        elif age <= 17:
            user_age_group = '15-17'
        else:
            user_age_group = '18-19'
        
        leaderboard.append({
            'username': user['username'],
            'consistency_pct': round(consistency_pct, 1),
            'performance_index': round(performance_index, 1),
            'age_group': user_age_group
        })
    
    leaderboard.sort(key=lambda x: x['performance_index'], reverse=True)
    return leaderboard[:100]

@api_router.post("/users/leaderboard-opt-in")
async def toggle_leaderboard_opt_in(current_user: dict = Depends(get_current_user)):
    user = await db.users.find_one({'id': current_user['id']}, {'_id': 0})
    new_status = not user.get('leaderboard_opt_in', False)
    await db.users.update_one(
        {'id': current_user['id']},
        {'$set': {'leaderboard_opt_in': new_status}}
    )
    return {'leaderboard_opt_in': new_status}

@api_router.post("/users/subscription")
async def toggle_subscription(current_user: dict = Depends(get_current_user)):
    user = await db.users.find_one({'id': current_user['id']}, {'_id': 0})
    new_status = not user.get('subscription_active', False)
    await db.users.update_one(
        {'id': current_user['id']},
        {'$set': {'subscription_active': new_status}}
    )
    return {'subscription_active': new_status}

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()