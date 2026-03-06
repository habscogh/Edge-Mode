"""
User management routes for Edge Mode
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List
import uuid

from config import db, PILLARS
from models.schemas import (
    User, UserPillar, PillarSetup, PillarAdd, PillarUpdate,
    OnboardingComplete, PasswordChange, EmailChange
)
from utils.auth import hash_password, verify_password, get_current_user

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=User)
async def get_me(current_user: dict = Depends(get_current_user)):
    return User(**current_user)


@router.post("/change-password")
async def change_password(request: PasswordChange, current_user: dict = Depends(get_current_user)):
    user = await db.users.find_one({'id': current_user['id']}, {'_id': 0})
    
    if not verify_password(request.current_password, user['password']):
        raise HTTPException(status_code=400, detail='Current password is incorrect')
    
    new_password_hash = hash_password(request.new_password)
    await db.users.update_one(
        {'id': current_user['id']},
        {'$set': {'password': new_password_hash}}
    )
    
    return {'message': 'Password changed successfully'}


@router.post("/change-email")
async def change_email(request: EmailChange, current_user: dict = Depends(get_current_user)):
    user = await db.users.find_one({'id': current_user['id']}, {'_id': 0})
    
    if not verify_password(request.password, user['password']):
        raise HTTPException(status_code=400, detail='Password is incorrect')
    
    existing = await db.users.find_one({'email': request.new_email}, {'_id': 0})
    if existing:
        raise HTTPException(status_code=400, detail='Email already in use')
    
    await db.users.update_one(
        {'id': current_user['id']},
        {'$set': {'email': request.new_email}}
    )
    
    return {'message': 'Email changed successfully'}


@router.delete("/account")
async def delete_account(current_user: dict = Depends(get_current_user)):
    user_id = current_user['id']
    
    await db.users.delete_one({'id': user_id})
    await db.user_pillars.delete_many({'user_id': user_id})
    await db.daily_sessions.delete_many({'user_id': user_id})
    await db.payment_transactions.delete_many({'metadata.user_id': user_id})
    
    await db.groups.update_many(
        {'members': user_id},
        {'$pull': {'members': user_id}}
    )
    
    await db.groups.delete_many({'created_by': user_id, 'members': {'$size': 0}})
    
    return {'message': 'Account deleted successfully'}


@router.post("/leaderboard-opt-in")
async def toggle_leaderboard_opt_in(current_user: dict = Depends(get_current_user)):
    user = await db.users.find_one({'id': current_user['id']}, {'_id': 0})
    new_status = not user.get('leaderboard_opt_in', False)
    await db.users.update_one(
        {'id': current_user['id']},
        {'$set': {'leaderboard_opt_in': new_status}}
    )
    return {'leaderboard_opt_in': new_status}


@router.post("/subscription")
async def toggle_subscription(current_user: dict = Depends(get_current_user)):
    user = await db.users.find_one({'id': current_user['id']}, {'_id': 0})
    new_status = not user.get('subscription_active', False)
    await db.users.update_one(
        {'id': current_user['id']},
        {'$set': {'subscription_active': new_status}}
    )
    return {'subscription_active': new_status}


# ============ Pillar Management ============

@router.get("/pillars", response_model=List[UserPillar])
async def get_user_pillars(current_user: dict = Depends(get_current_user)):
    pillars = await db.user_pillars.find({'user_id': current_user['id']}, {'_id': 0}).to_list(100)
    return [UserPillar(**p) for p in pillars]


@router.post("/pillars/add")
async def add_pillar(data: PillarAdd, current_user: dict = Depends(get_current_user)):
    """Add a new pillar for the user (max 5 pillars)"""
    user_id = current_user['id']
    
    current_pillars = await db.user_pillars.find({'user_id': user_id}, {'_id': 0}).to_list(100)
    if len(current_pillars) >= 5:
        raise HTTPException(status_code=400, detail='Maximum of 5 pillars allowed')
    
    if data.pillar_name not in PILLARS:
        raise HTTPException(status_code=400, detail='Invalid pillar name')
    
    existing = await db.user_pillars.find_one({
        'user_id': user_id,
        'pillar_name': data.pillar_name
    })
    if existing:
        raise HTTPException(status_code=400, detail='You already have this pillar')
    
    if data.weekly_target_sessions < 1 or data.weekly_target_sessions > 14:
        raise HTTPException(status_code=400, detail='Weekly target must be between 1 and 14')
    
    pillar_doc = {
        'id': str(uuid.uuid4()),
        'user_id': user_id,
        'pillar_name': data.pillar_name,
        'weekly_target_sessions': data.weekly_target_sessions
    }
    await db.user_pillars.insert_one(pillar_doc)
    
    return {'message': 'Pillar added', 'pillar': UserPillar(**pillar_doc).model_dump()}


@router.put("/pillars/{pillar_id}")
async def update_pillar(pillar_id: str, data: PillarUpdate, current_user: dict = Depends(get_current_user)):
    """Update a pillar's weekly target"""
    user_id = current_user['id']
    
    pillar = await db.user_pillars.find_one({
        'id': pillar_id,
        'user_id': user_id
    })
    if not pillar:
        raise HTTPException(status_code=404, detail='Pillar not found')
    
    if data.weekly_target_sessions < 1 or data.weekly_target_sessions > 14:
        raise HTTPException(status_code=400, detail='Weekly target must be between 1 and 14')
    
    await db.user_pillars.update_one(
        {'id': pillar_id},
        {'$set': {'weekly_target_sessions': data.weekly_target_sessions}}
    )
    
    return {'message': 'Pillar updated'}


@router.delete("/pillars/{pillar_id}")
async def delete_pillar(pillar_id: str, current_user: dict = Depends(get_current_user)):
    """Remove a pillar (minimum 1 pillar required)"""
    user_id = current_user['id']
    
    current_pillars = await db.user_pillars.find({'user_id': user_id}, {'_id': 0}).to_list(100)
    if len(current_pillars) <= 1:
        raise HTTPException(status_code=400, detail='You must have at least 1 pillar')
    
    pillar = await db.user_pillars.find_one({
        'id': pillar_id,
        'user_id': user_id
    })
    if not pillar:
        raise HTTPException(status_code=404, detail='Pillar not found')
    
    await db.user_pillars.delete_one({'id': pillar_id})
    
    return {'message': 'Pillar removed'}
