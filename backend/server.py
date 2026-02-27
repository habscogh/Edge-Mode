from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
import asyncio
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr, ConfigDict, validator
from typing import List, Optional, Dict
import uuid
from datetime import datetime, timezone, timedelta
import bcrypt
import jwt
import secrets
import string
import resend
from emergentintegrations.payments.stripe.checkout import StripeCheckout, CheckoutSessionResponse, CheckoutStatusResponse, CheckoutSessionRequest

# Password reset tokens storage (in production, use Redis or similar)
password_reset_tokens = {}

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

# Resend email configuration
RESEND_API_KEY = os.environ.get('RESEND_API_KEY')
SENDER_EMAIL = os.environ.get('SENDER_EMAIL', 'noreply@edgemodeapp.com')
if RESEND_API_KEY:
    resend.api_key = RESEND_API_KEY

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

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str

class PasswordChange(BaseModel):
    current_password: str
    new_password: str

class EmailChange(BaseModel):
    new_email: EmailStr
    password: str

class DeleteSession(BaseModel):
    session_id: str

class EditSession(BaseModel):
    session_id: str
    minutes_spent: int
    pillar: Optional[str] = None
    note: Optional[str] = None

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
    trial_ends_at: Optional[str] = None
    is_trial: bool = False
    last_log_date: Optional[str] = None
    leaderboard_opt_in: bool = False
    total_sessions_completed: int = 0

class UserPillar(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    user_id: str
    pillar_name: str
    weekly_target_sessions: int

class PillarSetup(BaseModel):
    pillar_name: str
    weekly_target_sessions: int

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

class DailySession(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    user_id: str
    pillar: str
    date: str
    timestamp: str
    minutes_spent: int = 0
    note: Optional[str] = None

class SessionComplete(BaseModel):
    pillar: str
    minutes_spent: Optional[int] = 30
    note: Optional[str] = None

class WeeklyStats(BaseModel):
    consistency_pct: float
    target_completion_pct: float
    performance_index: float
    total_sessions: int
    total_minutes: int
    days_logged: int
    pillars_data: List[dict]

class DailyComparison(BaseModel):
    today_sessions: int
    yesterday_sessions: int
    today_minutes: int
    yesterday_minutes: int
    improvement_pct: float

class PerformanceHistory(BaseModel):
    dates: List[str]
    scores: List[float]

class WeeklyReview(BaseModel):
    week_start: str
    week_end: str
    improved_pillars: List[dict]
    dropped_pillars: List[dict]
    average_daily_output_change: float
    total_sessions: int
    consistency_pct: float
    performance_index: float

class Group(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    name: str
    type: str
    created_by: str
    members: List[str]
    created_at: str
    invite_code: str

class GroupCreate(BaseModel):
    name: str
    type: str = "private"

class GroupJoin(BaseModel):
    invite_code: str

class LeaderboardEntry(BaseModel):
    username: str
    consistency_pct: float
    performance_index: float
    age_group: str
    improvement_pct: float

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

def generate_invite_code() -> str:
    return ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))

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
    total_sessions = user.get('total_sessions_completed', 0) + 1
    
    await db.users.update_one(
        {'id': user_id},
        {'$set': {
            'current_streak': current_streak,
            'longest_streak': longest_streak,
            'last_log_date': log_date,
            'total_sessions_completed': total_sessions
        }}
    )

# Routes
@api_router.post("/auth/register")
async def register(user_data: UserRegister):
    existing = await db.users.find_one({'email': user_data.email}, {'_id': 0})
    if existing:
        raise HTTPException(status_code=400, detail='Email already registered')
    
    user_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    trial_end = now + timedelta(days=7)
    
    user_doc = {
        'id': user_id,
        'email': user_data.email,
        'username': user_data.username,
        'password': hash_password(user_data.password),
        'age': user_data.age,
        'join_date': now.isoformat(),
        'current_streak': 0,
        'longest_streak': 0,
        'subscription_active': True,  # Active during trial
        'is_trial': True,
        'trial_ends_at': trial_end.isoformat(),
        'last_log_date': None,
        'leaderboard_opt_in': False,
        'total_sessions_completed': 0
    }
    
    await db.users.insert_one(user_doc)
    token = create_token(user_id)
    
    return {'token': token, 'user_id': user_id, 'trial_ends_at': trial_end.isoformat()}

@api_router.post("/auth/login")
async def login(credentials: UserLogin):
    user = await db.users.find_one({'email': credentials.email}, {'_id': 0})
    if not user or not verify_password(credentials.password, user['password']):
        raise HTTPException(status_code=401, detail='Invalid credentials')
    
    token = create_token(user['id'])
    return {'token': token, 'user_id': user['id']}

@api_router.post("/auth/forgot-password")
async def forgot_password(request: PasswordResetRequest):
    user = await db.users.find_one({'email': request.email}, {'_id': 0})
    if not user:
        # Don't reveal if email exists or not (security)
        return {'message': 'If that email exists, a reset link has been sent'}
    
    # Generate reset token
    reset_token = secrets.token_urlsafe(32)
    password_reset_tokens[reset_token] = {
        'user_id': user['id'],
        'expires': datetime.now(timezone.utc) + timedelta(hours=1)
    }
    
    # In production, send email with reset link
    # For now, return token (in production this would be in email)
    logger.info(f"Password reset token for {request.email}: {reset_token}")
    
    return {
        'message': 'If that email exists, a reset link has been sent',
        'reset_token': reset_token  # Remove this in production
    }

@api_router.post("/auth/reset-password")
async def reset_password(request: PasswordResetConfirm):
    # Check if token exists and is valid
    token_data = password_reset_tokens.get(request.token)
    if not token_data:
        raise HTTPException(status_code=400, detail='Invalid or expired reset token')
    
    # Check if expired
    if datetime.now(timezone.utc) > token_data['expires']:
        del password_reset_tokens[request.token]
        raise HTTPException(status_code=400, detail='Reset token has expired')
    
    # Update password
    new_password_hash = hash_password(request.new_password)
    await db.users.update_one(
        {'id': token_data['user_id']},
        {'$set': {'password': new_password_hash}}
    )
    
    # Remove used token
    del password_reset_tokens[request.token]
    
    return {'message': 'Password reset successfully'}

@api_router.post("/users/change-password")
async def change_password(request: PasswordChange, current_user: dict = Depends(get_current_user)):
    user = await db.users.find_one({'id': current_user['id']}, {'_id': 0})
    
    # Verify current password
    if not verify_password(request.current_password, user['password']):
        raise HTTPException(status_code=400, detail='Current password is incorrect')
    
    # Update to new password
    new_password_hash = hash_password(request.new_password)
    await db.users.update_one(
        {'id': current_user['id']},
        {'$set': {'password': new_password_hash}}
    )
    
    return {'message': 'Password changed successfully'}

@api_router.post("/users/change-email")
async def change_email(request: EmailChange, current_user: dict = Depends(get_current_user)):
    user = await db.users.find_one({'id': current_user['id']}, {'_id': 0})
    
    # Verify password
    if not verify_password(request.password, user['password']):
        raise HTTPException(status_code=400, detail='Password is incorrect')
    
    # Check if new email already exists
    existing = await db.users.find_one({'email': request.new_email}, {'_id': 0})
    if existing:
        raise HTTPException(status_code=400, detail='Email already in use')
    
    # Update email
    await db.users.update_one(
        {'id': current_user['id']},
        {'$set': {'email': request.new_email}}
    )
    
    return {'message': 'Email changed successfully'}

@api_router.delete("/users/account")
async def delete_account(current_user: dict = Depends(get_current_user)):
    user_id = current_user['id']
    
    # Delete user's data
    await db.users.delete_one({'id': user_id})
    await db.user_pillars.delete_many({'user_id': user_id})
    await db.daily_sessions.delete_many({'user_id': user_id})
    await db.payment_transactions.delete_many({'metadata.user_id': user_id})
    
    # Remove from groups
    await db.groups.update_many(
        {'members': user_id},
        {'$pull': {'members': user_id}}
    )
    
    # Delete groups they created with no other members
    await db.groups.delete_many({'created_by': user_id, 'members': {'$size': 0}})
    
    return {'message': 'Account deleted successfully'}

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
            'weekly_target_sessions': pillar_setup.weekly_target_sessions
        }
        await db.user_pillars.insert_one(pillar_doc)
    
    return {'message': 'Onboarding complete'}

@api_router.get("/users/pillars", response_model=List[UserPillar])
async def get_user_pillars(current_user: dict = Depends(get_current_user)):
    pillars = await db.user_pillars.find({'user_id': current_user['id']}, {'_id': 0}).to_list(100)
    return [UserPillar(**p) for p in pillars]

@api_router.post("/sessions/complete", response_model=DailySession)
async def complete_session(session_data: SessionComplete, current_user: dict = Depends(get_current_user)):
    # Check trial status
    if current_user.get('is_trial') and current_user.get('trial_ends_at'):
        trial_end = datetime.fromisoformat(current_user['trial_ends_at'])
        if datetime.now(timezone.utc) > trial_end:
            raise HTTPException(status_code=403, detail='Trial expired. Please subscribe to continue.')
    
    user_id = current_user['id']
    now = datetime.now(timezone.utc)
    today = now.date().isoformat()
    
    user_pillars = await db.user_pillars.find({'user_id': user_id}, {'_id': 0}).to_list(100)
    pillar_names = [p['pillar_name'] for p in user_pillars]
    
    if session_data.pillar not in pillar_names:
        raise HTTPException(status_code=400, detail='Invalid pillar for this user')
    
    session_doc = {
        'id': str(uuid.uuid4()),
        'user_id': user_id,
        'pillar': session_data.pillar,
        'date': today,
        'timestamp': now.isoformat(),
        'minutes_spent': session_data.minutes_spent or 30,
        'note': session_data.note
    }
    await db.daily_sessions.insert_one(session_doc)
    
    await update_streak(user_id, now.isoformat())
    
    return DailySession(**session_doc)

@api_router.put("/sessions/edit")
async def edit_session(edit_data: EditSession, current_user: dict = Depends(get_current_user)):
    session = await db.daily_sessions.find_one({'id': edit_data.session_id, 'user_id': current_user['id']}, {'_id': 0})
    if not session:
        raise HTTPException(status_code=404, detail='Session not found')
    
    update_fields = {'minutes_spent': edit_data.minutes_spent}
    if edit_data.pillar:
        update_fields['pillar'] = edit_data.pillar
    if edit_data.note is not None:
        update_fields['note'] = edit_data.note if edit_data.note else None
    
    await db.daily_sessions.update_one(
        {'id': edit_data.session_id},
        {'$set': update_fields}
    )
    
    return {'message': 'Session updated successfully'}

@api_router.delete("/sessions/{session_id}")
async def delete_session(session_id: str, current_user: dict = Depends(get_current_user)):
    result = await db.daily_sessions.delete_one({'id': session_id, 'user_id': current_user['id']})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail='Session not found')
    
    return {'message': 'Session deleted successfully'}

@api_router.get("/sessions/history")
async def get_session_history(current_user: dict = Depends(get_current_user), days: int = 30):
    end_date = datetime.now(timezone.utc).date()
    start_date = end_date - timedelta(days=days)
    
    sessions = await db.daily_sessions.find({
        'user_id': current_user['id'],
        'date': {'$gte': start_date.isoformat()}
    }, {'_id': 0}).sort('date', -1).to_list(1000)
    
    return sessions

@api_router.get("/sessions/today")
async def get_today_sessions(current_user: dict = Depends(get_current_user)):
    today = datetime.now(timezone.utc).date().isoformat()
    sessions = await db.daily_sessions.find({
        'user_id': current_user['id'],
        'date': today
    }, {'_id': 0}).to_list(100)
    return sessions

@api_router.get("/stats/weekly", response_model=WeeklyStats)
async def get_weekly_stats(current_user: dict = Depends(get_current_user)):
    user_id = current_user['id']
    today = datetime.now(timezone.utc).date()
    week_start = today - timedelta(days=today.weekday())
    
    sessions = await db.daily_sessions.find({
        'user_id': user_id,
        'date': {'$gte': week_start.isoformat()}
    }, {'_id': 0}).to_list(1000)
    
    user_pillars = await db.user_pillars.find({'user_id': user_id}, {'_id': 0}).to_list(100)
    
    unique_days = set(s['date'] for s in sessions)
    days_logged = len(unique_days)
    consistency_pct = (days_logged / 7) * 100
    
    total_sessions = len(sessions)
    total_minutes = sum(s.get('minutes_spent', 30) for s in sessions)
    total_target = sum(p['weekly_target_sessions'] for p in user_pillars)
    target_completion_pct = min((total_sessions / total_target * 100) if total_target > 0 else 0, 100)
    
    performance_index = min((consistency_pct * 0.7) + (target_completion_pct * 0.3), 100)
    
    pillars_data = []
    for pillar in user_pillars:
        pillar_sessions = [s for s in sessions if s['pillar'] == pillar['pillar_name']]
        pillar_count = len(pillar_sessions)
        pillars_data.append({
            'pillar_name': pillar['pillar_name'],
            'sessions_completed': pillar_count,
            'target_sessions': pillar['weekly_target_sessions'],
            'completion_pct': min((pillar_count / pillar['weekly_target_sessions'] * 100) if pillar['weekly_target_sessions'] > 0 else 0, 100)
        })
    
    return WeeklyStats(
        consistency_pct=round(consistency_pct, 1),
        target_completion_pct=round(target_completion_pct, 1),
        performance_index=round(performance_index, 1),
        total_sessions=total_sessions,
        total_minutes=total_minutes,
        days_logged=days_logged,
        pillars_data=pillars_data
    )

@api_router.get("/stats/comparison", response_model=DailyComparison)
async def get_daily_comparison(current_user: dict = Depends(get_current_user)):
    user_id = current_user['id']
    today = datetime.now(timezone.utc).date()
    yesterday = today - timedelta(days=1)
    
    today_sessions = await db.daily_sessions.find({
        'user_id': user_id,
        'date': today.isoformat()
    }, {'_id': 0}).to_list(100)
    
    yesterday_sessions = await db.daily_sessions.find({
        'user_id': user_id,
        'date': yesterday.isoformat()
    }, {'_id': 0}).to_list(100)
    
    today_count = len(today_sessions)
    yesterday_count = len(yesterday_sessions)
    today_minutes = sum(s.get('minutes_spent', 30) for s in today_sessions)
    yesterday_minutes = sum(s.get('minutes_spent', 30) for s in yesterday_sessions)
    
    improvement_pct = 0
    if yesterday_count > 0:
        improvement_pct = ((today_count - yesterday_count) / yesterday_count) * 100
    elif today_count > 0:
        improvement_pct = 100
    
    return DailyComparison(
        today_sessions=today_count,
        yesterday_sessions=yesterday_count,
        today_minutes=today_minutes,
        yesterday_minutes=yesterday_minutes,
        improvement_pct=round(improvement_pct, 1)
    )

@api_router.get("/stats/history", response_model=PerformanceHistory)
async def get_performance_history(current_user: dict = Depends(get_current_user), days: int = 30):
    user_id = current_user['id']
    end_date = datetime.now(timezone.utc).date()
    start_date = end_date - timedelta(days=days-1)
    
    user_pillars = await db.user_pillars.find({'user_id': user_id}, {'_id': 0}).to_list(100)
    total_target = sum(p['weekly_target_sessions'] for p in user_pillars)
    
    dates = []
    scores = []
    
    for i in range(days):
        date = start_date + timedelta(days=i)
        week_start = date - timedelta(days=date.weekday())
        week_end = week_start + timedelta(days=6)
        
        sessions = await db.daily_sessions.find({
            'user_id': user_id,
            'date': {'$gte': week_start.isoformat(), '$lte': week_end.isoformat()}
        }, {'_id': 0}).to_list(1000)
        
        unique_days = set(s['date'] for s in sessions)
        days_logged = len(unique_days)
        consistency_pct = (days_logged / 7) * 100
        
        total_sessions = len(sessions)
        target_completion_pct = min((total_sessions / total_target * 100) if total_target > 0 else 0, 100)
        
        performance_index = min((consistency_pct * 0.7) + (target_completion_pct * 0.3), 100)
        
        dates.append(date.isoformat())
        scores.append(round(performance_index, 1))
    
    return PerformanceHistory(dates=dates, scores=scores)

@api_router.get("/stats/weekly-review", response_model=WeeklyReview)
async def get_weekly_review(current_user: dict = Depends(get_current_user)):
    user_id = current_user['id']
    today = datetime.now(timezone.utc).date()
    current_week_start = today - timedelta(days=today.weekday())
    last_week_start = current_week_start - timedelta(days=7)
    last_week_end = current_week_start - timedelta(days=1)
    
    current_sessions = await db.daily_sessions.find({
        'user_id': user_id,
        'date': {'$gte': current_week_start.isoformat()}
    }, {'_id': 0}).to_list(1000)
    
    last_sessions = await db.daily_sessions.find({
        'user_id': user_id,
        'date': {'$gte': last_week_start.isoformat(), '$lte': last_week_end.isoformat()}
    }, {'_id': 0}).to_list(1000)
    
    user_pillars = await db.user_pillars.find({'user_id': user_id}, {'_id': 0}).to_list(100)
    
    improved_pillars = []
    dropped_pillars = []
    
    for pillar in user_pillars:
        current_count = len([s for s in current_sessions if s['pillar'] == pillar['pillar_name']])
        last_count = len([s for s in last_sessions if s['pillar'] == pillar['pillar_name']])
        change = current_count - last_count
        
        if change > 0:
            improved_pillars.append({
                'pillar_name': pillar['pillar_name'],
                'change': change,
                'current_sessions': current_count
            })
        elif change < 0:
            dropped_pillars.append({
                'pillar_name': pillar['pillar_name'],
                'change': abs(change),
                'current_sessions': current_count
            })
    
    current_daily_avg = len(current_sessions) / max(len(set(s['date'] for s in current_sessions)), 1)
    last_daily_avg = len(last_sessions) / max(len(set(s['date'] for s in last_sessions)), 1)
    avg_change = 0
    if last_daily_avg > 0:
        avg_change = ((current_daily_avg - last_daily_avg) / last_daily_avg) * 100
    
    unique_days = set(s['date'] for s in current_sessions)
    consistency_pct = (len(unique_days) / 7) * 100
    
    total_target = sum(p['weekly_target_sessions'] for p in user_pillars)
    target_completion = min((len(current_sessions) / total_target * 100) if total_target > 0 else 0, 100)
    performance_index = min((consistency_pct * 0.7) + (target_completion * 0.3), 100)
    
    return WeeklyReview(
        week_start=current_week_start.isoformat(),
        week_end=today.isoformat(),
        improved_pillars=improved_pillars,
        dropped_pillars=dropped_pillars,
        average_daily_output_change=round(avg_change, 1),
        total_sessions=len(current_sessions),
        consistency_pct=round(consistency_pct, 1),
        performance_index=round(performance_index, 1)
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
        'created_at': datetime.now(timezone.utc).isoformat(),
        'invite_code': generate_invite_code()
    }
    await db.groups.insert_one(group_doc)
    return Group(**group_doc)

@api_router.post("/groups/join")
async def join_group(join_data: GroupJoin, current_user: dict = Depends(get_current_user)):
    group = await db.groups.find_one({'invite_code': join_data.invite_code}, {'_id': 0})
    if not group:
        raise HTTPException(status_code=404, detail='Invalid invite code')
    
    if current_user['id'] in group['members']:
        return {'message': 'Already a member', 'group': group}
    
    await db.groups.update_one(
        {'id': group['id']},
        {'$push': {'members': current_user['id']}}
    )
    
    group['members'].append(current_user['id'])
    return {'message': 'Joined successfully', 'group': group}

@api_router.post("/groups/{group_id}/leave")
async def leave_group(group_id: str, current_user: dict = Depends(get_current_user)):
    group = await db.groups.find_one({'id': group_id}, {'_id': 0})
    if not group:
        raise HTTPException(status_code=404, detail='Group not found')
    
    # Can't leave if you're the creator and there are other members
    if group['created_by'] == current_user['id'] and len(group['members']) > 1:
        raise HTTPException(status_code=400, detail='Transfer ownership before leaving')
    
    # Can't leave if you're not a member
    if current_user['id'] not in group['members']:
        raise HTTPException(status_code=400, detail='Not a member of this group')
    
    # Remove user from members
    await db.groups.update_one(
        {'id': group_id},
        {'$pull': {'members': current_user['id']}}
    )
    
    # If creator left and they were the only member, delete the group
    if group['created_by'] == current_user['id'] and len(group['members']) == 1:
        await db.groups.delete_one({'id': group_id})
        return {'message': 'Group deleted (you were the only member)'}
    
    return {'message': 'Left group successfully'}

class TransferOwnership(BaseModel):
    new_owner_id: str

@api_router.post("/groups/{group_id}/transfer")
async def transfer_ownership(group_id: str, transfer_data: TransferOwnership, current_user: dict = Depends(get_current_user)):
    group = await db.groups.find_one({'id': group_id}, {'_id': 0})
    if not group:
        raise HTTPException(status_code=404, detail='Group not found')
    
    # Only creator can transfer ownership
    if group['created_by'] != current_user['id']:
        raise HTTPException(status_code=403, detail='Only the group creator can transfer ownership')
    
    # New owner must be a member
    if transfer_data.new_owner_id not in group['members']:
        raise HTTPException(status_code=400, detail='New owner must be a member of the group')
    
    # Can't transfer to yourself
    if transfer_data.new_owner_id == current_user['id']:
        raise HTTPException(status_code=400, detail='You are already the owner')
    
    # Transfer ownership
    await db.groups.update_one(
        {'id': group_id},
        {'$set': {'created_by': transfer_data.new_owner_id}}
    )
    
    # Get new owner info for response
    new_owner = await db.users.find_one({'id': transfer_data.new_owner_id}, {'_id': 0, 'password': 0})
    
    return {
        'message': f'Ownership transferred to {new_owner.get("username", "user")}',
        'new_owner': new_owner.get('username')
    }

@api_router.get("/groups/{group_id}/leaderboard")
async def get_group_leaderboard(group_id: str, current_user: dict = Depends(get_current_user)):
    group = await db.groups.find_one({'id': group_id}, {'_id': 0})
    if not group or current_user['id'] not in group['members']:
        raise HTTPException(status_code=404, detail='Group not found')
    
    member_ids = group['members']
    today = datetime.now(timezone.utc).date()
    week_start = today - timedelta(days=today.weekday())
    
    # Batch fetch all data at once
    users = await db.users.find({'id': {'$in': member_ids}}, {'_id': 0, 'password': 0}).to_list(100)
    users_by_id = {user['id']: user for user in users}
    
    all_sessions = await db.daily_sessions.find({
        'user_id': {'$in': member_ids},
        'date': {'$gte': week_start.isoformat()}
    }, {'_id': 0}).to_list(5000)
    sessions_by_user = {}
    for session in all_sessions:
        sessions_by_user.setdefault(session['user_id'], []).append(session)
    
    all_pillars = await db.user_pillars.find({'user_id': {'$in': member_ids}}, {'_id': 0}).to_list(500)
    pillars_by_user = {}
    for pillar in all_pillars:
        pillars_by_user.setdefault(pillar['user_id'], []).append(pillar)
    
    leaderboard = []
    for member_id in member_ids:
        user = users_by_id.get(member_id)
        if not user:
            continue
        
        sessions = sessions_by_user.get(member_id, [])
        user_pillars = pillars_by_user.get(member_id, [])
        
        unique_days = set(s['date'] for s in sessions)
        days_logged = len(unique_days)
        consistency_pct = (days_logged / 7) * 100
        
        total_sessions = len(sessions)
        total_target = sum(p['weekly_target_sessions'] for p in user_pillars)
        target_completion_pct = min((total_sessions / total_target * 100) if total_target > 0 else 0, 100)
        
        performance_index = min((consistency_pct * 0.7) + (target_completion_pct * 0.3), 100)
        
        leaderboard.append({
            'user_id': user['id'],
            'username': user['username'],
            'consistency_pct': round(consistency_pct, 1),
            'performance_index': round(performance_index, 1),
            'current_streak': user.get('current_streak', 0),
            'total_sessions': total_sessions
        })
    
    leaderboard.sort(key=lambda x: x['performance_index'], reverse=True)
    return leaderboard

@api_router.get("/leaderboard/global")
async def get_global_leaderboard(age_group: Optional[str] = None):
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
    user_ids = [user['id'] for user in users]
    
    if not user_ids:
        return []
    
    today = datetime.now(timezone.utc).date()
    week_start = today - timedelta(days=today.weekday())
    last_week_start = week_start - timedelta(days=7)
    last_week_end = week_start - timedelta(days=1)
    
    # Batch fetch all sessions for current and last week
    all_current_sessions = await db.daily_sessions.find({
        'user_id': {'$in': user_ids},
        'date': {'$gte': week_start.isoformat()}
    }, {'_id': 0}).to_list(10000)
    
    all_last_sessions = await db.daily_sessions.find({
        'user_id': {'$in': user_ids},
        'date': {'$gte': last_week_start.isoformat(), '$lte': last_week_end.isoformat()}
    }, {'_id': 0}).to_list(10000)
    
    all_pillars = await db.user_pillars.find({'user_id': {'$in': user_ids}}, {'_id': 0}).to_list(5000)
    
    # Group data by user_id
    current_sessions_by_user = {}
    for session in all_current_sessions:
        current_sessions_by_user.setdefault(session['user_id'], []).append(session)
    
    last_sessions_by_user = {}
    for session in all_last_sessions:
        last_sessions_by_user.setdefault(session['user_id'], []).append(session)
    
    pillars_by_user = {}
    for pillar in all_pillars:
        pillars_by_user.setdefault(pillar['user_id'], []).append(pillar)
    
    leaderboard = []
    for user in users:
        current_sessions = current_sessions_by_user.get(user['id'], [])
        last_sessions = last_sessions_by_user.get(user['id'], [])
        user_pillars = pillars_by_user.get(user['id'], [])
        
        unique_days = set(s['date'] for s in current_sessions)
        days_logged = len(unique_days)
        consistency_pct = (days_logged / 7) * 100
        
        total_sessions = len(current_sessions)
        total_target = sum(p.get('weekly_target_sessions', p.get('weekly_target_minutes', 5)) for p in user_pillars)
        target_completion = min((total_sessions / total_target * 100) if total_target > 0 else 0, 100)
        performance_index = min((consistency_pct * 0.7) + (target_completion * 0.3), 100)
        
        last_total = len(last_sessions)
        improvement_pct = 0
        if last_total > 0:
            improvement_pct = ((total_sessions - last_total) / last_total) * 100
        elif total_sessions > 0:
            improvement_pct = 100
        
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
            'age_group': user_age_group,
            'improvement_pct': round(improvement_pct, 1)
        })
    
    leaderboard.sort(key=lambda x: x['improvement_pct'], reverse=True)
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

# Stripe Payment Integration
STRIPE_API_KEY = os.environ.get('STRIPE_API_KEY')
SUBSCRIPTION_PRICES = {
    'monthly': 5.99,
    'yearly': 59.99
}

class CreateCheckoutRequest(BaseModel):
    origin_url: str
    plan: str = 'monthly'

@api_router.post("/payments/create-checkout")
async def create_checkout(request: CreateCheckoutRequest, current_user: dict = Depends(get_current_user)):
    try:
        # Validate plan
        if request.plan not in SUBSCRIPTION_PRICES:
            raise HTTPException(status_code=400, detail='Invalid subscription plan')
        
        amount = SUBSCRIPTION_PRICES[request.plan]
        
        # Initialize Stripe
        host_url = request.origin_url
        webhook_url = f"{host_url}/api/webhook/stripe"
        stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)
        
        # Create success and cancel URLs
        success_url = f"{host_url}/subscription-success?session_id={{CHECKOUT_SESSION_ID}}"
        cancel_url = f"{host_url}/profile"
        
        # Create checkout session
        checkout_request = CheckoutSessionRequest(
            amount=amount,
            currency="usd",
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                "user_id": current_user['id'],
                "email": current_user['email'],
                "username": current_user['username'],
                "plan": request.plan
            }
        )
        
        session = await stripe_checkout.create_checkout_session(checkout_request)
        
        # Create payment transaction record
        transaction_doc = {
            'id': str(uuid.uuid4()),
            'session_id': session.session_id,
            'user_id': current_user['id'],
            'amount': amount,
            'currency': 'usd',
            'plan': request.plan,
            'payment_status': 'pending',
            'status': 'initiated',
            'created_at': datetime.now(timezone.utc).isoformat(),
            'metadata': {
                "user_id": current_user['id'],
                "email": current_user['email'],
                "plan": request.plan
            }
        }
        await db.payment_transactions.insert_one(transaction_doc)
        
        return {'url': session.url, 'session_id': session.session_id}
    
    except Exception as e:
        logger.error(f"Failed to create checkout: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/payments/status/{session_id}")
async def get_payment_status(session_id: str, current_user: dict = Depends(get_current_user)):
    try:
        logger.info(f"Checking payment status for session: {session_id}")
        
        # Check if we already processed this payment
        existing_transaction = await db.payment_transactions.find_one({
            'session_id': session_id,
            'payment_status': 'paid'
        }, {'_id': 0})
        
        if existing_transaction:
            logger.info(f"Transaction already processed and paid for session: {session_id}")
            return {
                'status': 'complete',
                'payment_status': 'paid',
                'already_processed': True
            }
        
        # Get status from Stripe
        stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY)
        checkout_status = await stripe_checkout.get_checkout_status(session_id)
        
        logger.info(f"Stripe status for {session_id}: {checkout_status.payment_status}")
        
        # Update transaction record
        await db.payment_transactions.update_one(
            {'session_id': session_id},
            {'$set': {
                'status': checkout_status.status,
                'payment_status': checkout_status.payment_status,
                'updated_at': datetime.now(timezone.utc).isoformat()
            }}
        )
        
        # If payment successful, activate subscription
        if checkout_status.payment_status == 'paid':
            transaction = await db.payment_transactions.find_one({'session_id': session_id}, {'_id': 0})
            if transaction:
                user_id = transaction.get('metadata', {}).get('user_id')
                if user_id:
                    # Update user subscription status
                    update_result = await db.users.update_one(
                        {'id': user_id},
                        {'$set': {'subscription_active': True}}
                    )
                    logger.info(f"Activated subscription for user {user_id} - matched: {update_result.matched_count}, modified: {update_result.modified_count}")
                    
                    # Verify it was actually updated
                    user = await db.users.find_one({'id': user_id}, {'_id': 0, 'username': 1, 'subscription_active': 1})
                    logger.info(f"User {user.get('username')} subscription_active is now: {user.get('subscription_active')}")
                else:
                    logger.error(f"No user_id found in transaction metadata for session {session_id}")
            else:
                logger.error(f"Transaction not found for session {session_id}")
        
        return {
            'status': checkout_status.status,
            'payment_status': checkout_status.payment_status
        }
    
    except Exception as e:
        logger.error(f"Failed to get payment status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    try:
        body = await request.body()
        signature = request.headers.get("Stripe-Signature")
        
        stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY)
        webhook_response = await stripe_checkout.handle_webhook(body, signature)
        
        # Update transaction record
        await db.payment_transactions.update_one(
            {'session_id': webhook_response.session_id},
            {'$set': {
                'payment_status': webhook_response.payment_status,
                'event_type': webhook_response.event_type,
                'updated_at': datetime.now(timezone.utc).isoformat()
            }}
        )
        
        # If payment successful, activate subscription
        if webhook_response.payment_status == 'paid':
            user_id = webhook_response.metadata.get('user_id')
            if user_id:
                await db.users.update_one(
                    {'id': user_id},
                    {'$set': {'subscription_active': True}}
                )
        
        return {'status': 'success'}
    
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

# ============ Email Notification Endpoints ============

class EmailSettings(BaseModel):
    streak_reminders: bool = True
    weekly_summary: bool = True

async def send_email_async(to_email: str, subject: str, html_content: str):
    """Send email using Resend API (non-blocking)"""
    if not RESEND_API_KEY:
        logger.warning("RESEND_API_KEY not configured, skipping email")
        return None
    
    params = {
        "from": SENDER_EMAIL,
        "to": [to_email],
        "subject": subject,
        "html": html_content
    }
    
    try:
        result = await asyncio.to_thread(resend.Emails.send, params)
        logger.info(f"Email sent to {to_email}: {result}")
        return result
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        return None

def get_streak_reminder_html(username: str, streak: int) -> str:
    return f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background: #09090b; color: white;">
        <div style="text-align: center; padding: 20px 0;">
            <h1 style="color: #fff; margin: 0; font-size: 24px;">🔥 Don't Break Your Streak!</h1>
        </div>
        <div style="padding: 20px; background: #18181b; border-radius: 8px; margin: 20px 0;">
            <p style="margin: 0; font-size: 16px;">Hey <strong>{username}</strong>,</p>
            <p style="margin: 15px 0;">You're on a <strong style="color: #f97316; font-size: 20px;">{streak}-day streak</strong>! Keep the momentum going.</p>
            <p style="margin: 15px 0;">Log a session today to continue your progress.</p>
        </div>
        <div style="text-align: center; padding: 20px;">
            <p style="color: #71717a; font-size: 12px;">Edge Mode - 1% Better Every Day</p>
        </div>
    </div>
    """

def get_weekly_summary_html(username: str, stats: dict) -> str:
    return f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background: #09090b; color: white;">
        <div style="text-align: center; padding: 20px 0;">
            <h1 style="color: #fff; margin: 0; font-size: 24px;">📊 Your Weekly Summary</h1>
        </div>
        <div style="padding: 20px; background: #18181b; border-radius: 8px; margin: 20px 0;">
            <p style="margin: 0; font-size: 16px;">Hey <strong>{username}</strong>,</p>
            <p style="margin: 15px 0;">Here's how you did this week:</p>
            <div style="display: flex; justify-content: space-around; padding: 15px 0;">
                <div style="text-align: center;">
                    <div style="font-size: 28px; font-weight: bold; color: #f97316;">{stats.get('total_sessions', 0)}</div>
                    <div style="color: #71717a; font-size: 12px;">Sessions</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 28px; font-weight: bold; color: #22c55e;">{stats.get('total_minutes', 0)}</div>
                    <div style="color: #71717a; font-size: 12px;">Minutes</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 28px; font-weight: bold; color: #3b82f6;">{stats.get('consistency_pct', 0):.0f}%</div>
                    <div style="color: #71717a; font-size: 12px;">Consistency</div>
                </div>
            </div>
        </div>
        <div style="text-align: center; padding: 20px;">
            <p style="color: #71717a; font-size: 12px;">Edge Mode - 1% Better Every Day</p>
        </div>
    </div>
    """

@api_router.get("/notifications/settings")
async def get_notification_settings(current_user: dict = Depends(get_current_user)):
    user = await db.users.find_one({'id': current_user['id']}, {'_id': 0})
    return EmailSettings(
        streak_reminders=user.get('streak_reminders', True),
        weekly_summary=user.get('weekly_summary', True)
    )

@api_router.put("/notifications/settings")
async def update_notification_settings(settings: EmailSettings, current_user: dict = Depends(get_current_user)):
    await db.users.update_one(
        {'id': current_user['id']},
        {'$set': {
            'streak_reminders': settings.streak_reminders,
            'weekly_summary': settings.weekly_summary
        }}
    )
    return {'message': 'Notification settings updated'}

@api_router.post("/notifications/send-streak-reminder")
async def send_streak_reminder(current_user: dict = Depends(get_current_user)):
    """Send streak reminder email to the current user (for testing)"""
    if not current_user.get('streak_reminders', True):
        return {'message': 'Streak reminders disabled for this user'}
    
    html = get_streak_reminder_html(
        current_user.get('username', 'User'),
        current_user.get('current_streak', 0)
    )
    
    result = await send_email_async(
        current_user['email'],
        "🔥 Don't Break Your Streak! - Edge Mode",
        html
    )
    
    if result:
        return {'message': 'Streak reminder sent', 'email_id': result.get('id')}
    return {'message': 'Email not sent (check configuration)'}

@api_router.post("/notifications/send-weekly-summary")
async def send_weekly_summary(current_user: dict = Depends(get_current_user)):
    """Send weekly summary email to the current user (for testing)"""
    if not current_user.get('weekly_summary', True):
        return {'message': 'Weekly summaries disabled for this user'}
    
    # Get weekly stats
    user_id = current_user['id']
    now = datetime.now(timezone.utc)
    week_start = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
    
    sessions = await db.daily_sessions.find({
        'user_id': user_id,
        'timestamp': {'$gte': week_start.isoformat()}
    }, {'_id': 0}).to_list(100)
    
    total_sessions = len(sessions)
    total_minutes = sum(s.get('minutes_spent', 0) for s in sessions)
    days_logged = len(set(s.get('date') for s in sessions))
    consistency_pct = (days_logged / 7) * 100
    
    stats = {
        'total_sessions': total_sessions,
        'total_minutes': total_minutes,
        'consistency_pct': consistency_pct
    }
    
    html = get_weekly_summary_html(current_user.get('username', 'User'), stats)
    
    result = await send_email_async(
        current_user['email'],
        "📊 Your Weekly Summary - Edge Mode",
        html
    )
    
    if result:
        return {'message': 'Weekly summary sent', 'email_id': result.get('id'), 'stats': stats}
    return {'message': 'Email not sent (check configuration)', 'stats': stats}

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

@app.get("/health")
async def health_check():
    """Health check endpoint for deployment"""
    try:
        # Check MongoDB connection
        await client.admin.command('ping')
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()