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
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from emergentintegrations.payments.stripe.checkout import StripeCheckout, CheckoutSessionResponse, CheckoutStatusResponse, CheckoutSessionRequest

# Password reset tokens storage (in production, use Redis or similar)
password_reset_tokens = {}

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Initialize scheduler
scheduler = AsyncIOScheduler()

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

# Badge Definitions
BADGES = {
    "first_session": {
        "id": "first_session",
        "name": "First Step",
        "description": "Log your first session",
        "icon": "🏆",
        "category": "milestone"
    },
    "streak_7": {
        "id": "streak_7",
        "name": "Week Warrior",
        "description": "Maintain a 7-day streak",
        "icon": "🔥",
        "category": "streak"
    },
    "streak_14": {
        "id": "streak_14",
        "name": "Fortnight Fighter",
        "description": "Maintain a 14-day streak",
        "icon": "🔥",
        "category": "streak"
    },
    "streak_30": {
        "id": "streak_30",
        "name": "Monthly Master",
        "description": "Maintain a 30-day streak",
        "icon": "🔥",
        "category": "streak"
    },
    "sessions_100": {
        "id": "sessions_100",
        "name": "Century Club",
        "description": "Complete 100 sessions",
        "icon": "💯",
        "category": "milestone"
    },
    "hours_50": {
        "id": "hours_50",
        "name": "50 Hour Club",
        "description": "Log 50+ hours total",
        "icon": "⏱️",
        "category": "milestone"
    },
    "perfect_week": {
        "id": "perfect_week",
        "name": "Perfect Week",
        "description": "Log every day for a week",
        "icon": "✨",
        "category": "consistency"
    },
    "pillar_master": {
        "id": "pillar_master",
        "name": "Pillar Master",
        "description": "Hit target on all pillars in a week",
        "icon": "🎯",
        "category": "mastery"
    }
}

# Models
class UserRegister(BaseModel):
    email: EmailStr
    username: str
    password: str
    age: int
    referral_code: Optional[str] = None  # Optional referral code from inviter

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

class EmailInvite(BaseModel):
    friend_email: EmailStr
    friend_name: Optional[str] = None

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
    local_date: Optional[str] = None  # Client's local date (YYYY-MM-DD) to handle timezone correctly

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
    
    return current_streak, longest_streak, total_sessions

# Badge checking and awarding functions
async def award_badge(user_id: str, badge_id: str) -> dict:
    """Award a badge to a user if they don't already have it"""
    # Check if user already has this badge
    existing = await db.user_badges.find_one({
        'user_id': user_id,
        'badge_id': badge_id
    })
    
    if existing:
        return None  # Already has badge
    
    # Award the badge
    badge_doc = {
        'id': str(uuid.uuid4()),
        'user_id': user_id,
        'badge_id': badge_id,
        'earned_at': datetime.now(timezone.utc).isoformat()
    }
    await db.user_badges.insert_one(badge_doc)
    
    logger.info(f"Badge '{badge_id}' awarded to user {user_id}")
    return {**BADGES[badge_id], 'earned_at': badge_doc['earned_at']}

async def check_and_award_badges(user_id: str) -> List[dict]:
    """Check all badge conditions and award any newly earned badges"""
    user = await db.users.find_one({'id': user_id}, {'_id': 0})
    if not user:
        return []
    
    newly_earned = []
    now = datetime.now(timezone.utc)
    
    # Get user's session stats
    all_sessions = await db.daily_sessions.find({'user_id': user_id}, {'_id': 0}).to_list(10000)
    total_sessions = len(all_sessions)
    total_minutes = sum(s.get('minutes_spent', 0) for s in all_sessions)
    total_hours = total_minutes / 60
    
    # Check First Session badge
    if total_sessions >= 1:
        badge = await award_badge(user_id, 'first_session')
        if badge:
            newly_earned.append(badge)
    
    # Check Streak badges
    current_streak = user.get('current_streak', 0)
    longest_streak = user.get('longest_streak', 0)
    max_streak = max(current_streak, longest_streak)
    
    if max_streak >= 7:
        badge = await award_badge(user_id, 'streak_7')
        if badge:
            newly_earned.append(badge)
    
    if max_streak >= 14:
        badge = await award_badge(user_id, 'streak_14')
        if badge:
            newly_earned.append(badge)
    
    if max_streak >= 30:
        badge = await award_badge(user_id, 'streak_30')
        if badge:
            newly_earned.append(badge)
    
    # Check Century Club (100 sessions)
    if total_sessions >= 100:
        badge = await award_badge(user_id, 'sessions_100')
        if badge:
            newly_earned.append(badge)
    
    # Check 50 Hour Club
    if total_hours >= 50:
        badge = await award_badge(user_id, 'hours_50')
        if badge:
            newly_earned.append(badge)
    
    # Check Perfect Week (logged every day for 7 consecutive days)
    if current_streak >= 7:
        badge = await award_badge(user_id, 'perfect_week')
        if badge:
            newly_earned.append(badge)
    
    # Check Pillar Master (hit target on all pillars in current week)
    user_pillars = await db.user_pillars.find({'user_id': user_id}, {'_id': 0}).to_list(100)
    if user_pillars:
        week_start = now.date() - timedelta(days=now.weekday())
        week_sessions = await db.daily_sessions.find({
            'user_id': user_id,
            'date': {'$gte': week_start.isoformat()}
        }, {'_id': 0}).to_list(1000)
        
        all_targets_met = True
        for pillar in user_pillars:
            pillar_sessions = [s for s in week_sessions if s['pillar'] == pillar['pillar_name']]
            if len(pillar_sessions) < pillar['weekly_target_sessions']:
                all_targets_met = False
                break
        
        if all_targets_met:
            badge = await award_badge(user_id, 'pillar_master')
            if badge:
                newly_earned.append(badge)
    
    return newly_earned

# Routes
@api_router.post("/auth/register")
async def register(user_data: UserRegister):
    existing = await db.users.find_one({'email': user_data.email}, {'_id': 0})
    if existing:
        raise HTTPException(status_code=400, detail='Email already registered')
    
    user_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    trial_end = now + timedelta(days=14)
    
    # Generate unique referral code for this user
    referral_code = f"{user_data.username[:4].upper()}{secrets.token_hex(3).upper()}"
    
    # Check if referred by someone
    referred_by = None
    if user_data.referral_code:
        referrer = await db.users.find_one({'referral_code': user_data.referral_code}, {'_id': 0, 'id': 1})
        if referrer:
            referred_by = referrer['id']
    
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
        'total_sessions_completed': 0,
        'referral_code': referral_code,
        'referred_by': referred_by
    }
    
    await db.users.insert_one(user_doc)
    
    # If referred, record the referral
    if referred_by:
        await db.referrals.insert_one({
            'id': str(uuid.uuid4()),
            'referrer_id': referred_by,
            'referred_id': user_id,
            'referred_email': user_data.email,
            'created_at': now.isoformat()
        })
    
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

# ============ Badges/Achievements Endpoints ============

@api_router.get("/badges/all")
async def get_all_badges():
    """Get all available badges with their definitions"""
    return list(BADGES.values())

@api_router.get("/badges/user")
async def get_user_badges(current_user: dict = Depends(get_current_user)):
    """Get all badges earned by the current user"""
    user_badges = await db.user_badges.find(
        {'user_id': current_user['id']},
        {'_id': 0}
    ).to_list(100)
    
    # Enrich with badge details
    earned_badges = []
    for ub in user_badges:
        badge_def = BADGES.get(ub['badge_id'])
        if badge_def:
            earned_badges.append({
                **badge_def,
                'earned_at': ub['earned_at']
            })
    
    # Get all badges with earned status
    all_badges = []
    for badge_id, badge_def in BADGES.items():
        earned = next((b for b in user_badges if b['badge_id'] == badge_id), None)
        all_badges.append({
            **badge_def,
            'earned': earned is not None,
            'earned_at': earned['earned_at'] if earned else None
        })
    
    return {
        'earned_badges': earned_badges,
        'all_badges': all_badges,
        'total_earned': len(earned_badges),
        'total_available': len(BADGES)
    }

@api_router.get("/badges/progress")
async def get_badge_progress(current_user: dict = Depends(get_current_user)):
    """Get progress towards unearned badges"""
    user_id = current_user['id']
    user = await db.users.find_one({'id': user_id}, {'_id': 0})
    
    # Get user's current stats
    all_sessions = await db.daily_sessions.find({'user_id': user_id}, {'_id': 0}).to_list(10000)
    total_sessions = len(all_sessions)
    total_minutes = sum(s.get('minutes_spent', 0) for s in all_sessions)
    total_hours = total_minutes / 60
    
    current_streak = user.get('current_streak', 0)
    longest_streak = user.get('longest_streak', 0)
    max_streak = max(current_streak, longest_streak)
    
    # Get earned badges
    user_badges = await db.user_badges.find({'user_id': user_id}, {'_id': 0, 'badge_id': 1}).to_list(100)
    earned_ids = {b['badge_id'] for b in user_badges}
    
    progress = []
    
    if 'first_session' not in earned_ids:
        progress.append({
            'badge_id': 'first_session',
            'current': total_sessions,
            'target': 1,
            'percent': min(100, (total_sessions / 1) * 100)
        })
    
    if 'streak_7' not in earned_ids:
        progress.append({
            'badge_id': 'streak_7',
            'current': max_streak,
            'target': 7,
            'percent': min(100, (max_streak / 7) * 100)
        })
    
    if 'streak_14' not in earned_ids:
        progress.append({
            'badge_id': 'streak_14',
            'current': max_streak,
            'target': 14,
            'percent': min(100, (max_streak / 14) * 100)
        })
    
    if 'streak_30' not in earned_ids:
        progress.append({
            'badge_id': 'streak_30',
            'current': max_streak,
            'target': 30,
            'percent': min(100, (max_streak / 30) * 100)
        })
    
    if 'sessions_100' not in earned_ids:
        progress.append({
            'badge_id': 'sessions_100',
            'current': total_sessions,
            'target': 100,
            'percent': min(100, (total_sessions / 100) * 100)
        })
    
    if 'hours_50' not in earned_ids:
        progress.append({
            'badge_id': 'hours_50',
            'current': round(total_hours, 1),
            'target': 50,
            'percent': min(100, (total_hours / 50) * 100)
        })
    
    if 'perfect_week' not in earned_ids:
        progress.append({
            'badge_id': 'perfect_week',
            'current': current_streak,
            'target': 7,
            'percent': min(100, (current_streak / 7) * 100)
        })
    
    return progress

# ============ Referral/Invite Endpoints ============

def get_invite_email_html(inviter_name: str, friend_name: str, referral_link: str) -> str:
    """Generate HTML for invite email"""
    greeting = f"Hey {friend_name}," if friend_name else "Hey there,"
    return f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background: #09090b; color: white;">
        <div style="text-align: center; padding: 20px 0;">
            <h1 style="color: #fff; margin: 0; font-size: 28px;">You're Invited! 🎯</h1>
        </div>
        <div style="padding: 20px; background: #18181b; border-radius: 8px; margin: 20px 0;">
            <p style="margin: 0; font-size: 16px;">{greeting}</p>
            <p style="margin: 15px 0;"><strong>{inviter_name}</strong> thinks you'd love Edge Mode - an app that helps teens become 1% better every day.</p>
            
            <div style="text-align: center; padding: 20px; background: #27272a; border-radius: 8px; margin: 20px 0;">
                <p style="margin: 0 0 15px 0; color: #a1a1aa;">What you'll get:</p>
                <p style="margin: 5px 0; color: #fff;">✓ Track daily progress across pillars</p>
                <p style="margin: 5px 0; color: #fff;">✓ Build streaks & earn badges</p>
                <p style="margin: 5px 0; color: #fff;">✓ Compete with friends on leaderboards</p>
                <p style="margin: 5px 0; color: #fff;">✓ 14-day free trial</p>
            </div>
            
            <div style="text-align: center; margin: 25px 0;">
                <a href="{referral_link}" style="display: inline-block; background: #22c55e; color: white; padding: 14px 28px; text-decoration: none; border-radius: 8px; font-weight: bold; font-size: 16px;">Join Edge Mode</a>
            </div>
        </div>
        <div style="text-align: center; padding: 20px;">
            <p style="color: #71717a; font-size: 12px;">Edge Mode - 1% Better Every Day</p>
        </div>
    </div>
    """

@api_router.get("/referral/info")
async def get_referral_info(current_user: dict = Depends(get_current_user)):
    """Get user's referral code and stats"""
    user_id = current_user['id']
    
    # Get or generate referral code
    referral_code = current_user.get('referral_code')
    if not referral_code:
        # Generate one if missing (for existing users)
        referral_code = f"{current_user['username'][:4].upper()}{secrets.token_hex(3).upper()}"
        await db.users.update_one(
            {'id': user_id},
            {'$set': {'referral_code': referral_code}}
        )
    
    # Count successful referrals
    referral_count = await db.referrals.count_documents({'referrer_id': user_id})
    
    # Get list of referred users
    referrals = await db.referrals.find(
        {'referrer_id': user_id},
        {'_id': 0, 'referred_email': 1, 'created_at': 1}
    ).sort('created_at', -1).to_list(50)
    
    # Base URL for referral link
    base_url = "https://edgemodeapp.com"
    referral_link = f"{base_url}/auth?ref={referral_code}"
    
    return {
        'referral_code': referral_code,
        'referral_link': referral_link,
        'total_referrals': referral_count,
        'referrals': referrals
    }

@api_router.post("/referral/send-invite")
async def send_invite_email(invite_data: EmailInvite, current_user: dict = Depends(get_current_user)):
    """Send an invite email to a friend"""
    if not RESEND_API_KEY:
        raise HTTPException(status_code=500, detail='Email service not configured')
    
    # Get referral code
    referral_code = current_user.get('referral_code')
    if not referral_code:
        referral_code = f"{current_user['username'][:4].upper()}{secrets.token_hex(3).upper()}"
        await db.users.update_one(
            {'id': current_user['id']},
            {'$set': {'referral_code': referral_code}}
        )
    
    # Check if this email is already registered
    existing = await db.users.find_one({'email': invite_data.friend_email}, {'_id': 0, 'id': 1})
    if existing:
        return {'message': 'This person is already on Edge Mode!', 'already_member': True}
    
    # Check if already invited by this user recently (prevent spam)
    recent_invite = await db.sent_invites.find_one({
        'inviter_id': current_user['id'],
        'invited_email': invite_data.friend_email,
        'sent_at': {'$gte': (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()}
    })
    
    if recent_invite:
        return {'message': 'You already invited this person recently', 'already_invited': True}
    
    # Generate referral link
    base_url = "https://edgemodeapp.com"
    referral_link = f"{base_url}/auth?ref={referral_code}"
    
    # Send email
    html = get_invite_email_html(
        current_user['username'],
        invite_data.friend_name,
        referral_link
    )
    
    try:
        result = await asyncio.to_thread(resend.Emails.send, {
            "from": SENDER_EMAIL,
            "to": [invite_data.friend_email],
            "subject": f"{current_user['username']} invited you to Edge Mode! 🎯",
            "html": html
        })
        
        # Record the invite
        await db.sent_invites.insert_one({
            'id': str(uuid.uuid4()),
            'inviter_id': current_user['id'],
            'invited_email': invite_data.friend_email,
            'invited_name': invite_data.friend_name,
            'sent_at': datetime.now(timezone.utc).isoformat()
        })
        
        return {'message': 'Invite sent!', 'success': True}
    except Exception as e:
        logger.error(f"Failed to send invite email: {e}")
        raise HTTPException(status_code=500, detail='Failed to send invite email')

@api_router.post("/sessions/complete")
async def complete_session(session_data: SessionComplete, current_user: dict = Depends(get_current_user)):
    # Check trial status
    if current_user.get('is_trial') and current_user.get('trial_ends_at'):
        trial_end = datetime.fromisoformat(current_user['trial_ends_at'])
        if datetime.now(timezone.utc) > trial_end:
            raise HTTPException(status_code=403, detail='Trial expired. Please subscribe to continue.')
    
    user_id = current_user['id']
    now = datetime.now(timezone.utc)
    
    # Use client's local date if provided, otherwise fall back to UTC date
    if session_data.local_date:
        # Validate the date format
        try:
            datetime.strptime(session_data.local_date, '%Y-%m-%d')
            today = session_data.local_date
        except ValueError:
            today = now.date().isoformat()
    else:
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
    
    # Update streak and last_log_date
    await update_streak(user_id, now.isoformat())
    await db.users.update_one(
        {'id': user_id},
        {'$set': {'last_log_date': today}}
    )
    
    # Check for newly earned badges
    new_badges = await check_and_award_badges(user_id)
    
    return {
        'session': DailySession(**session_doc).model_dump(),
        'new_badges': new_badges
    }

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
async def get_today_sessions(current_user: dict = Depends(get_current_user), local_date: Optional[str] = None):
    # Use client's local date if provided, otherwise fall back to UTC
    if local_date:
        try:
            datetime.strptime(local_date, '%Y-%m-%d')
            today = local_date
        except ValueError:
            today = datetime.now(timezone.utc).date().isoformat()
    else:
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
    'monthly': 4.99,
    'yearly': 49.99
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

@api_router.get("/scheduler/status")
async def get_scheduler_status(current_user: dict = Depends(get_current_user)):
    """Get the status of the email scheduler"""
    jobs = scheduler.get_jobs()
    job_info = []
    for job in jobs:
        job_info.append({
            'id': job.id,
            'next_run': job.next_run_time.isoformat() if job.next_run_time else None
        })
    
    return {
        'scheduler_running': scheduler.running,
        'jobs': job_info,
        'schedule': {
            'streak_reminders': '8:00 PM UTC daily (3:00 PM Eastern)',
            'inactive_reminders': '6:00 PM UTC daily (2:00 PM Eastern) - for 3-7 days inactive',
            'trial_ending_reminders': '4:00 PM UTC daily (12:00 PM Eastern) - for users with 1-3 days left',
            'weekly_summary': 'Sunday 2:00 PM UTC (10:00 AM Eastern)'
        }
    }

@api_router.post("/notifications/send-trial-ending")
async def send_trial_ending_reminder(current_user: dict = Depends(get_current_user)):
    """Send trial ending reminder email to the current user (for testing)"""
    if not current_user.get('is_trial'):
        return {'message': 'User is not on trial'}
    
    if not current_user.get('streak_reminders', True):
        return {'message': 'Streak reminders disabled for this user'}
    
    # Calculate days left
    now = datetime.now(timezone.utc)
    trial_end = datetime.fromisoformat(current_user['trial_ends_at'].replace('Z', '+00:00'))
    days_left = max(1, (trial_end.date() - now.date()).days)
    
    # Get weekly stats
    user_id = current_user['id']
    week_start = now.date() - timedelta(days=now.weekday())
    
    sessions = await db.daily_sessions.find({
        'user_id': user_id,
        'date': {'$gte': week_start.isoformat()}
    }, {'_id': 0}).to_list(100)
    
    unique_days = set(s['date'] for s in sessions)
    consistency_pct = (len(unique_days) / 7) * 100
    
    html = get_trial_ending_html(
        current_user.get('username', 'User'),
        days_left,
        current_user.get('current_streak', 0),
        consistency_pct
    )
    
    result = await send_email_async(
        current_user['email'],
        f"⏰ Your Edge Mode Trial Ends {'Tomorrow' if days_left == 1 else f'in {days_left} Days'}",
        html
    )
    
    if result:
        return {'message': 'Trial ending reminder sent', 'email_id': result.get('id'), 'days_left': days_left}
    return {'message': 'Email not sent (check configuration)', 'days_left': days_left}

# ============ Admin Endpoints ============

ADMIN_EMAILS = ['admin@edgemodeapp.com']  # Add your admin email(s) here

async def require_admin(current_user: dict = Depends(get_current_user)):
    """Check if user is an admin"""
    if current_user.get('email') not in ADMIN_EMAILS:
        raise HTTPException(status_code=403, detail='Admin access required')
    return current_user

@api_router.get("/admin/stats")
async def get_admin_stats(admin_user: dict = Depends(require_admin)):
    """Get overall app statistics for admin dashboard"""
    now = datetime.now(timezone.utc)
    today = now.date().isoformat()
    week_ago = (now - timedelta(days=7)).isoformat()
    
    # User stats
    total_users = await db.users.count_documents({})
    users_today = await db.users.count_documents({
        'join_date': {'$gte': today}
    })
    users_this_week = await db.users.count_documents({
        'join_date': {'$gte': (now - timedelta(days=7)).date().isoformat()}
    })
    users_this_month = await db.users.count_documents({
        'join_date': {'$gte': (now - timedelta(days=30)).date().isoformat()}
    })
    
    # Active users (logged a session in last 7 days)
    active_user_ids = await db.daily_sessions.distinct('user_id', {
        'timestamp': {'$gte': week_ago}
    })
    active_users = len(active_user_ids)
    
    # Session stats
    total_sessions = await db.daily_sessions.count_documents({})
    sessions_today = await db.daily_sessions.count_documents({
        'date': today
    })
    sessions_this_week = await db.daily_sessions.count_documents({
        'timestamp': {'$gte': week_ago}
    })
    
    # Subscription stats
    paid_subscribers = await db.users.count_documents({'subscription_active': True})
    trial_users = await db.users.count_documents({
        'subscription_active': {'$ne': True},
        'trial_ends_at': {'$gte': now.isoformat()}
    })
    
    # Group stats
    total_groups = await db.groups.count_documents({})
    
    return {
        'users': {
            'total': total_users,
            'today': users_today,
            'this_week': users_this_week,
            'this_month': users_this_month,
            'active_last_7_days': active_users
        },
        'sessions': {
            'total': total_sessions,
            'today': sessions_today,
            'this_week': sessions_this_week
        },
        'subscriptions': {
            'paid': paid_subscribers,
            'trial': trial_users
        },
        'groups': {
            'total': total_groups
        },
        'generated_at': now.isoformat()
    }

@api_router.get("/admin/users")
async def get_admin_users(
    admin_user: dict = Depends(require_admin),
    limit: int = 50,
    skip: int = 0
):
    """Get list of all users for admin"""
    users = await db.users.find(
        {},
        {'_id': 0, 'password_hash': 0}
    ).sort('join_date', -1).skip(skip).limit(limit).to_list(limit)
    
    total = await db.users.count_documents({})
    
    return {
        'users': users,
        'total': total,
        'limit': limit,
        'skip': skip
    }

@api_router.get("/admin/recent-activity")
async def get_recent_activity(admin_user: dict = Depends(require_admin)):
    """Get recent signups and sessions"""
    now = datetime.now(timezone.utc)
    week_ago = (now - timedelta(days=7)).isoformat()
    
    # Recent signups
    recent_signups = await db.users.find(
        {'join_date': {'$gte': (now - timedelta(days=7)).date().isoformat()}},
        {'_id': 0, 'id': 1, 'username': 1, 'email': 1, 'join_date': 1}
    ).sort('join_date', -1).to_list(20)
    
    # Recent sessions with user info
    recent_sessions = await db.daily_sessions.find(
        {'timestamp': {'$gte': week_ago}},
        {'_id': 0}
    ).sort('timestamp', -1).limit(20).to_list(20)
    
    # Add usernames to sessions
    for session in recent_sessions:
        user = await db.users.find_one({'id': session['user_id']}, {'_id': 0, 'username': 1})
        session['username'] = user.get('username', 'Unknown') if user else 'Unknown'
    
    return {
        'recent_signups': recent_signups,
        'recent_sessions': recent_sessions
    }

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

# ============ Scheduled Email Jobs ============

async def send_streak_reminders_job():
    """Send streak reminder emails to users who haven't logged today"""
    if not RESEND_API_KEY:
        logger.warning("RESEND_API_KEY not set, skipping streak reminders")
        return
    
    logger.info("Running streak reminder job...")
    today = datetime.now(timezone.utc).date().isoformat()
    
    try:
        # Find users with streak reminders enabled who haven't logged today
        users = await db.users.find({
            'streak_reminders': {'$ne': False},  # Default is True
            'current_streak': {'$gt': 0}  # Only users with active streaks
        }, {'_id': 0, 'id': 1, 'email': 1, 'username': 1, 'current_streak': 1}).to_list(1000)
        
        sent_count = 0
        for user in users:
            # Check if user logged today
            session_today = await db.daily_sessions.find_one({
                'user_id': user['id'],
                'date': today
            })
            
            if not session_today:
                # User hasn't logged today - send reminder
                html = get_streak_reminder_html(
                    user.get('username', 'User'),
                    user.get('current_streak', 0)
                )
                
                try:
                    await asyncio.to_thread(resend.Emails.send, {
                        "from": SENDER_EMAIL,
                        "to": [user['email']],
                        "subject": "🔥 Don't Break Your Streak! - Edge Mode",
                        "html": html
                    })
                    sent_count += 1
                except Exception as e:
                    logger.error(f"Failed to send streak reminder to {user['email']}: {e}")
        
        logger.info(f"Streak reminder job complete. Sent {sent_count} emails.")
    except Exception as e:
        logger.error(f"Streak reminder job failed: {e}")

async def send_weekly_summaries_job():
    """Send weekly summary emails to all opted-in users"""
    if not RESEND_API_KEY:
        logger.warning("RESEND_API_KEY not set, skipping weekly summaries")
        return
    
    logger.info("Running weekly summary job...")
    now = datetime.now(timezone.utc)
    week_start = (now - timedelta(days=7)).isoformat()
    
    try:
        # Find users with weekly summaries enabled
        users = await db.users.find({
            'weekly_summary': {'$ne': False}  # Default is True
        }, {'_id': 0, 'id': 1, 'email': 1, 'username': 1}).to_list(1000)
        
        sent_count = 0
        for user in users:
            # Get weekly stats
            sessions = await db.daily_sessions.find({
                'user_id': user['id'],
                'timestamp': {'$gte': week_start}
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
            
            html = get_weekly_summary_html(user.get('username', 'User'), stats)
            
            try:
                await asyncio.to_thread(resend.Emails.send, {
                    "from": SENDER_EMAIL,
                    "to": [user['email']],
                    "subject": "📊 Your Weekly Summary - Edge Mode",
                    "html": html
                })
                sent_count += 1
            except Exception as e:
                logger.error(f"Failed to send weekly summary to {user['email']}: {e}")
        
        logger.info(f"Weekly summary job complete. Sent {sent_count} emails.")
    except Exception as e:
        logger.error(f"Weekly summary job failed: {e}")

def get_inactive_reminder_html(username: str, days_inactive: int) -> str:
    return f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background: #09090b; color: white;">
        <div style="text-align: center; padding: 20px 0;">
            <h1 style="color: #fff; margin: 0; font-size: 24px;">👋 We Miss You!</h1>
        </div>
        <div style="padding: 20px; background: #18181b; border-radius: 8px; margin: 20px 0;">
            <p style="margin: 0; font-size: 16px;">Hey <strong>{username}</strong>,</p>
            <p style="margin: 15px 0;">It's been <strong style="color: #f97316;">{days_inactive} days</strong> since your last session.</p>
            <p style="margin: 15px 0;">Remember: <em>Small steps lead to big changes.</em> Even 15 minutes today counts!</p>
            <p style="margin: 15px 0;">Your future self will thank you. 💪</p>
        </div>
        <div style="text-align: center; padding: 20px;">
            <p style="color: #71717a; font-size: 12px;">Edge Mode - 1% Better Every Day</p>
        </div>
    </div>
    """

async def send_inactive_reminders_job():
    """Send reminder emails to users who haven't logged in 2+ days"""
    if not RESEND_API_KEY:
        logger.warning("RESEND_API_KEY not set, skipping inactive reminders")
        return
    
    logger.info("Running inactive user reminder job...")
    now = datetime.now(timezone.utc)
    two_days_ago = (now - timedelta(days=2)).date().isoformat()
    
    try:
        # Find users with streak reminders enabled
        users = await db.users.find({
            'streak_reminders': {'$ne': False}
        }, {'_id': 0, 'id': 1, 'email': 1, 'username': 1, 'last_log_date': 1}).to_list(1000)
        
        sent_count = 0
        for user in users:
            last_log = user.get('last_log_date')
            
            # Check if user hasn't logged in 2+ days
            if last_log and last_log <= two_days_ago:
                # Calculate days inactive
                last_log_date = datetime.fromisoformat(last_log).date()
                days_inactive = (now.date() - last_log_date).days
                
                # Only send if 2-7 days inactive (don't spam long-inactive users)
                if 2 <= days_inactive <= 7:
                    html = get_inactive_reminder_html(
                        user.get('username', 'User'),
                        days_inactive
                    )
                    
                    try:
                        await asyncio.to_thread(resend.Emails.send, {
                            "from": SENDER_EMAIL,
                            "to": [user['email']],
                            "subject": "👋 We Miss You! - Edge Mode",
                            "html": html
                        })
                        sent_count += 1
                    except Exception as e:
                        logger.error(f"Failed to send inactive reminder to {user['email']}: {e}")
        
        logger.info(f"Inactive reminder job complete. Sent {sent_count} emails.")
    except Exception as e:
        logger.error(f"Inactive reminder job failed: {e}")

def get_trial_ending_html(username: str, days_left: int, streak: int, consistency_pct: float) -> str:
    """Generate HTML for trial ending reminder email"""
    days_text = "tomorrow" if days_left == 1 else f"in {days_left} days"
    
    streak_section = ""
    if streak > 0:
        streak_section = f"""
            <div style="text-align: center; padding: 15px; background: #27272a; border-radius: 8px; margin: 10px 0;">
                <div style="font-size: 32px; font-weight: bold; color: #f97316;">🔥 {streak}</div>
                <div style="color: #71717a; font-size: 12px;">Day Streak</div>
            </div>
        """
    
    consistency_section = ""
    if consistency_pct > 0:
        consistency_section = f"""
            <div style="text-align: center; padding: 15px; background: #27272a; border-radius: 8px; margin: 10px 0;">
                <div style="font-size: 32px; font-weight: bold; color: #22c55e;">📈 {consistency_pct:.0f}%</div>
                <div style="color: #71717a; font-size: 12px;">Consistency Score</div>
            </div>
        """
    
    return f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background: #09090b; color: white;">
        <div style="text-align: center; padding: 20px 0;">
            <h1 style="color: #fff; margin: 0; font-size: 24px;">⏰ Your Trial Ends {days_text.title()}</h1>
        </div>
        <div style="padding: 20px; background: #18181b; border-radius: 8px; margin: 20px 0;">
            <p style="margin: 0; font-size: 16px;">Hey <strong>{username}</strong>,</p>
            <p style="margin: 15px 0;">Your 14-day free trial ends <strong style="color: #f97316;">{days_text}</strong>.</p>
            
            {streak_section}
            {consistency_section}
            
            <p style="margin: 15px 0; padding: 15px; background: #7f1d1d40; border: 1px solid #7f1d1d; border-radius: 8px; text-align: center;">
                <strong style="color: #fca5a5;">Don't lose your progress.</strong><br/>
                <span style="color: #a1a1aa; font-size: 14px;">Subscribe now to keep your momentum going.</span>
            </p>
        </div>
        <div style="text-align: center; padding: 20px;">
            <p style="color: #71717a; font-size: 12px;">Edge Mode - 1% Better Every Day</p>
        </div>
    </div>
    """

async def send_trial_ending_reminders_job():
    """Send reminder emails to trial users with 2-3 days left"""
    if not RESEND_API_KEY:
        logger.warning("RESEND_API_KEY not set, skipping trial ending reminders")
        return
    
    logger.info("Running trial ending reminder job...")
    now = datetime.now(timezone.utc)
    
    try:
        # Find trial users
        users = await db.users.find({
            'is_trial': True,
            'trial_ends_at': {'$exists': True},
            'streak_reminders': {'$ne': False}
        }, {'_id': 0}).to_list(1000)
        
        sent_count = 0
        for user in users:
            trial_end = datetime.fromisoformat(user['trial_ends_at'].replace('Z', '+00:00'))
            days_left = (trial_end.date() - now.date()).days
            
            # Only send if 2-3 days remaining (day 12 and 13 of trial)
            if 1 <= days_left <= 3:
                # Get user's weekly stats for consistency
                user_id = user['id']
                week_start = now.date() - timedelta(days=now.weekday())
                
                sessions = await db.daily_sessions.find({
                    'user_id': user_id,
                    'date': {'$gte': week_start.isoformat()}
                }, {'_id': 0}).to_list(100)
                
                unique_days = set(s['date'] for s in sessions)
                consistency_pct = (len(unique_days) / 7) * 100
                
                html = get_trial_ending_html(
                    user.get('username', 'User'),
                    days_left,
                    user.get('current_streak', 0),
                    consistency_pct
                )
                
                try:
                    await asyncio.to_thread(resend.Emails.send, {
                        "from": SENDER_EMAIL,
                        "to": [user['email']],
                        "subject": f"⏰ Your Edge Mode Trial Ends {'Tomorrow' if days_left == 1 else f'in {days_left} Days'}",
                        "html": html
                    })
                    sent_count += 1
                    logger.info(f"Sent trial ending reminder to {user['email']} ({days_left} days left)")
                except Exception as e:
                    logger.error(f"Failed to send trial ending reminder to {user['email']}: {e}")
        
        logger.info(f"Trial ending reminder job complete. Sent {sent_count} emails.")
    except Exception as e:
        logger.error(f"Trial ending reminder job failed: {e}")

@api_router.get("/health")
async def health_check():
    """Health check endpoint for deployment"""
    try:
        # Check MongoDB connection
        await client.admin.command('ping')
        return {"status": "healthy", "database": "connected", "scheduler": scheduler.running}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}

@app.get("/health")
async def root_health_check():
    """Root health check endpoint"""
    return {"status": "ok"}

@app.on_event("startup")
async def startup_scheduler():
    """Start the scheduler when app starts"""
    # Streak reminders - daily at 8 PM UTC (3 PM Eastern)
    scheduler.add_job(
        send_streak_reminders_job,
        CronTrigger(hour=20, minute=0),  # 8 PM UTC
        id="streak_reminders",
        replace_existing=True
    )
    
    # Weekly summaries - every Sunday at 2 PM UTC (10 AM Eastern)
    scheduler.add_job(
        send_weekly_summaries_job,
        CronTrigger(day_of_week='sun', hour=14, minute=0),  # 2 PM UTC = 10 AM Eastern
        id="weekly_summaries",
        replace_existing=True
    )
    
    # Inactive user reminders - daily at 6 PM UTC (2 PM Eastern)
    scheduler.add_job(
        send_inactive_reminders_job,
        CronTrigger(hour=18, minute=0),  # 6 PM UTC = 2 PM Eastern
        id="inactive_reminders",
        replace_existing=True
    )
    
    # Trial ending reminders - daily at 4 PM UTC (12 PM Eastern)
    scheduler.add_job(
        send_trial_ending_reminders_job,
        CronTrigger(hour=16, minute=0),  # 4 PM UTC = 12 PM Eastern
        id="trial_ending_reminders",
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("Email scheduler started - Streak: 8PM UTC, Inactive: 6PM UTC, Trial Ending: 4PM UTC, Weekly: Sun 2PM UTC")

@app.on_event("shutdown")
async def shutdown_db_client():
    scheduler.shutdown()
    client.close()