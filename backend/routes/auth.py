"""
Authentication routes for Edge Mode
"""
from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timezone, timedelta
import uuid
import secrets

from config import db, logger, VALID_COACH_CODES
from models.schemas import (
    UserRegister, UserLogin, CoachRegister, 
    PasswordResetRequest, PasswordResetConfirm
)
from utils.auth import hash_password, verify_password, create_token, get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Password reset tokens storage (in production, use Redis or similar)
password_reset_tokens = {}


@router.post("/register")
async def register(user_data: UserRegister):
    existing = await db.users.find_one({'email': user_data.email}, {'_id': 0})
    if existing:
        raise HTTPException(status_code=400, detail='Email already registered')
    
    user_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    trial_end = now + timedelta(days=14)
    
    referral_code = f"{user_data.username[:4].upper()}{secrets.token_hex(3).upper()}"
    
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
        'subscription_active': True,
        'is_trial': True,
        'trial_ends_at': trial_end.isoformat(),
        'last_log_date': None,
        'leaderboard_opt_in': False,
        'total_sessions_completed': 0,
        'referral_code': referral_code,
        'referred_by': referred_by
    }
    
    await db.users.insert_one(user_doc)
    
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


@router.post("/login")
async def login(credentials: UserLogin):
    user = await db.users.find_one({'email': credentials.email}, {'_id': 0})
    if not user or not verify_password(credentials.password, user['password']):
        raise HTTPException(status_code=401, detail='Invalid credentials')
    
    token = create_token(user['id'])
    return {'token': token, 'user_id': user['id'], 'is_coach': user.get('is_coach', False)}


@router.post("/coach/register")
async def register_coach(coach_data: CoachRegister):
    """Register a new coach account - coaches are always free"""
    existing = await db.users.find_one({'email': coach_data.email}, {'_id': 0})
    if existing:
        raise HTTPException(status_code=400, detail='Email already registered')
    
    coach_id = str(uuid.uuid4())
    team_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    
    has_extended_trial = False
    if coach_data.special_code and coach_data.special_code.upper() in VALID_COACH_CODES:
        has_extended_trial = True
    
    team_invite_code = f"TEAM-{secrets.token_hex(4).upper()}"
    
    coach_doc = {
        'id': coach_id,
        'email': coach_data.email,
        'name': coach_data.name,
        'password': hash_password(coach_data.password),
        'join_date': now.isoformat(),
        'is_coach': True,
        'subscription_active': True,
        'is_trial': False,
        'trial_ends_at': None,
        'team_id': team_id,
        'special_code': coach_data.special_code.upper() if coach_data.special_code else None,
        'has_extended_trial': has_extended_trial,
        'onboarding_complete': True
    }
    
    await db.users.insert_one(coach_doc)
    
    team_doc = {
        'id': team_id,
        'name': coach_data.team_name,
        'type': 'team',
        'created_by': coach_id,
        'coach_id': coach_id,
        'members': [coach_id],
        'created_at': now.isoformat(),
        'invite_code': team_invite_code,
        'has_extended_trial': has_extended_trial
    }
    
    await db.groups.insert_one(team_doc)
    
    token = create_token(coach_id)
    invite_link = f"/join/{team_invite_code}"
    
    return {
        'token': token,
        'coach_id': coach_id,
        'team_id': team_id,
        'team_name': coach_data.team_name,
        'invite_code': team_invite_code,
        'invite_link': invite_link,
        'has_extended_trial': has_extended_trial,
        'message': 'Coach account created successfully! Share your invite link with players.'
    }


@router.post("/player/join-team")
async def register_player_with_team(user_data: UserRegister, team_code: str):
    """Register a new player and automatically add them to a coach's team"""
    team = await db.groups.find_one({'invite_code': team_code}, {'_id': 0})
    if not team:
        raise HTTPException(status_code=404, detail='Invalid team code')
    
    existing = await db.users.find_one({'email': user_data.email}, {'_id': 0})
    if existing:
        raise HTTPException(status_code=400, detail='Email already registered')
    
    user_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    
    trial_days = 30 if team.get('has_extended_trial') else 14
    trial_end = now + timedelta(days=trial_days)
    
    referral_code = f"{user_data.username[:4].upper()}{secrets.token_hex(3).upper()}"
    
    user_doc = {
        'id': user_id,
        'email': user_data.email,
        'username': user_data.username,
        'password': hash_password(user_data.password),
        'age': user_data.age,
        'join_date': now.isoformat(),
        'current_streak': 0,
        'longest_streak': 0,
        'subscription_active': True,
        'is_trial': True,
        'trial_ends_at': trial_end.isoformat(),
        'last_log_date': None,
        'leaderboard_opt_in': False,
        'total_sessions_completed': 0,
        'referral_code': referral_code,
        'team_id': team['id'],
        'joined_via_coach': True
    }
    
    await db.users.insert_one(user_doc)
    
    await db.groups.update_one(
        {'id': team['id']},
        {'$addToSet': {'members': user_id}}
    )
    
    token = create_token(user_id)
    
    return {
        'token': token,
        'user_id': user_id,
        'trial_ends_at': trial_end.isoformat(),
        'trial_days': trial_days,
        'team_name': team['name'],
        'message': f'Welcome to {team["name"]}! You have a {trial_days}-day free trial.'
    }


@router.post("/forgot-password")
async def forgot_password(request: PasswordResetRequest):
    user = await db.users.find_one({'email': request.email}, {'_id': 0})
    if not user:
        return {'message': 'If that email exists, a reset link has been sent'}
    
    reset_token = secrets.token_urlsafe(32)
    password_reset_tokens[reset_token] = {
        'user_id': user['id'],
        'expires': datetime.now(timezone.utc) + timedelta(hours=1)
    }
    
    logger.info(f"Password reset token for {request.email}: {reset_token}")
    
    return {
        'message': 'If that email exists, a reset link has been sent',
        'reset_token': reset_token
    }


@router.post("/reset-password")
async def reset_password(request: PasswordResetConfirm):
    token_data = password_reset_tokens.get(request.token)
    if not token_data:
        raise HTTPException(status_code=400, detail='Invalid or expired reset token')
    
    if datetime.now(timezone.utc) > token_data['expires']:
        del password_reset_tokens[request.token]
        raise HTTPException(status_code=400, detail='Reset token has expired')
    
    new_password_hash = hash_password(request.new_password)
    await db.users.update_one(
        {'id': token_data['user_id']},
        {'$set': {'password': new_password_hash}}
    )
    
    del password_reset_tokens[request.token]
    
    return {'message': 'Password reset successfully'}
