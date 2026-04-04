"""
Referral routes for Edge Mode - Invite Friends, Earn Exclusive Rewards
"""
from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel
import uuid
import random
import string

from config import db
from utils.auth import get_current_user

router = APIRouter(prefix="/referrals", tags=["Referrals"])


# ============ Referral Milestones & Exclusive Rewards ============

REFERRAL_MILESTONES = [
    {
        "id": "milestone-1",
        "referrals_required": 1,
        "reward_type": "badge",
        "reward_id": "badge-recruiter",
        "reward_name": "Recruiter Badge",
        "reward_description": "You brought a friend to the Edge!",
        "reward_icon": "🤝",
        "coins_bonus": 25
    },
    {
        "id": "milestone-3",
        "referrals_required": 3,
        "reward_type": "frame",
        "reward_id": "frame-squad-leader",
        "reward_name": "Squad Leader Frame",
        "reward_description": "Lead your squad to greatness",
        "reward_icon": "👑",
        "coins_bonus": 75
    },
    {
        "id": "milestone-5",
        "referrals_required": 5,
        "reward_type": "theme",
        "reward_id": "theme-connector",
        "reward_name": "Connector Theme",
        "reward_description": "Legendary theme for true connectors",
        "reward_icon": "🔗",
        "coins_bonus": 150
    },
    {
        "id": "milestone-10",
        "referrals_required": 10,
        "reward_type": "effect",
        "reward_id": "effect-golden-aura",
        "reward_name": "Golden Aura Effect",
        "reward_description": "The ultimate flex - you're a legend",
        "reward_icon": "✨",
        "coins_bonus": 300
    }
]

# Exclusive items only available through referrals
REFERRAL_EXCLUSIVE_ITEMS = [
    {
        "id": "badge-recruiter",
        "name": "Recruiter Badge",
        "description": "Earned by inviting your first friend",
        "category": "badges",
        "price": 0,
        "rarity": "exclusive",
        "icon": "🤝",
        "referrals_required": 1,
        "is_referral_exclusive": True
    },
    {
        "id": "frame-squad-leader",
        "name": "Squad Leader Frame",
        "description": "Earned by inviting 3 friends",
        "category": "avatars",
        "price": 0,
        "rarity": "exclusive",
        "icon": "👑",
        "referrals_required": 3,
        "is_referral_exclusive": True
    },
    {
        "id": "theme-connector",
        "name": "Connector Theme",
        "description": "Legendary theme for inviting 5 friends",
        "category": "themes",
        "price": 0,
        "rarity": "legendary",
        "icon": "🔗",
        "preview_color": "#10b981",
        "referrals_required": 5,
        "is_referral_exclusive": True
    },
    {
        "id": "effect-golden-aura",
        "name": "Golden Aura",
        "description": "Ultimate reward for inviting 10 friends",
        "category": "effects",
        "price": 0,
        "rarity": "legendary",
        "icon": "✨",
        "referrals_required": 10,
        "is_referral_exclusive": True
    }
]


# ============ Helper Functions ============

def generate_referral_code(username: str) -> str:
    """Generate a unique referral code for a user"""
    # Use first 4 chars of username + 4 random chars
    prefix = ''.join(c for c in username[:4].upper() if c.isalnum())
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"{prefix}{suffix}"


async def get_or_create_referral_code(user_id: str, username: str) -> str:
    """Get existing referral code or create one"""
    user = await db.users.find_one({'id': user_id}, {'_id': 0, 'referral_code': 1})
    
    if user and user.get('referral_code'):
        return user['referral_code']
    
    # Generate new code
    code = generate_referral_code(username)
    
    # Ensure uniqueness
    while await db.users.find_one({'referral_code': code}):
        code = generate_referral_code(username)
    
    await db.users.update_one(
        {'id': user_id},
        {'$set': {'referral_code': code}}
    )
    
    return code


async def check_and_award_referral_milestones(user_id: str) -> list:
    """Check if user has reached any new referral milestones and award rewards"""
    user = await db.users.find_one({'id': user_id}, {'_id': 0})
    if not user:
        return []
    
    referral_count = user.get('referral_count', 0)
    claimed_milestones = user.get('referral_milestones_claimed', [])
    
    new_rewards = []
    total_coins_bonus = 0
    
    for milestone in REFERRAL_MILESTONES:
        if (referral_count >= milestone['referrals_required'] and 
            milestone['id'] not in claimed_milestones):
            
            # Award the exclusive item
            inventory_item = {
                'id': str(uuid.uuid4()),
                'user_id': user_id,
                'item_id': milestone['reward_id'],
                'category': milestone['reward_type'] + 's',  # badges, frames, themes, effects
                'is_equipped': False,
                'source': 'referral_milestone',
                'purchased_at': datetime.now(timezone.utc).isoformat()
            }
            await db.user_inventory.insert_one(inventory_item)
            
            # Track milestone claimed
            claimed_milestones.append(milestone['id'])
            total_coins_bonus += milestone['coins_bonus']
            
            new_rewards.append({
                'milestone': milestone,
                'item_awarded': milestone['reward_name']
            })
    
    if new_rewards:
        # Update user with claimed milestones and bonus coins
        current_coins = user.get('coins', 0)
        await db.users.update_one(
            {'id': user_id},
            {'$set': {
                'referral_milestones_claimed': claimed_milestones,
                'coins': current_coins + total_coins_bonus
            }}
        )
    
    return new_rewards


async def seed_referral_items():
    """Add referral exclusive items to shop (marked as exclusive)"""
    for item in REFERRAL_EXCLUSIVE_ITEMS:
        existing = await db.shop_items.find_one({'id': item['id']})
        if not existing:
            item_doc = {
                **item,
                'is_active': True,
                'is_limited': False,
                'stock': None,
                'total_sold': 0,
                'created_at': datetime.now(timezone.utc).isoformat()
            }
            await db.shop_items.insert_one(item_doc)


# ============ API Endpoints ============

@router.get("/my-code")
async def get_my_referral_code(current_user: dict = Depends(get_current_user)):
    """Get current user's referral code and stats"""
    await seed_referral_items()  # Ensure exclusive items exist
    
    code = await get_or_create_referral_code(current_user['id'], current_user.get('username', 'USER'))
    
    user = await db.users.find_one({'id': current_user['id']}, {'_id': 0})
    referral_count = user.get('referral_count', 0)
    claimed_milestones = user.get('referral_milestones_claimed', [])
    
    # Build milestones with progress
    milestones_with_progress = []
    for milestone in REFERRAL_MILESTONES:
        milestones_with_progress.append({
            **milestone,
            'current': min(referral_count, milestone['referrals_required']),
            'is_claimed': milestone['id'] in claimed_milestones,
            'is_unlocked': referral_count >= milestone['referrals_required'],
            'progress_pct': min(100, (referral_count / milestone['referrals_required']) * 100)
        })
    
    # Next milestone
    next_milestone = None
    for m in milestones_with_progress:
        if not m['is_unlocked']:
            next_milestone = m
            break
    
    return {
        'referral_code': code,
        'referral_link': f"https://edgemodeapp.com/join?ref={code}",
        'referral_count': referral_count,
        'milestones': milestones_with_progress,
        'next_milestone': next_milestone,
        'referrals_until_next': next_milestone['referrals_required'] - referral_count if next_milestone else 0
    }


@router.get("/my-referrals")
async def get_my_referrals(current_user: dict = Depends(get_current_user)):
    """Get list of users referred by current user"""
    referrals = await db.users.find(
        {'referred_by': current_user['id']},
        {'_id': 0, 'id': 1, 'username': 1, 'created_at': 1, 'current_streak': 1}
    ).sort('created_at', -1).to_list(50)
    
    return {
        'referrals': referrals,
        'total_count': len(referrals)
    }


@router.post("/apply-code")
async def apply_referral_code(code: str, current_user: dict = Depends(get_current_user)):
    """Apply a referral code (usually done during signup)"""
    # Check if user already has a referrer
    user = await db.users.find_one({'id': current_user['id']}, {'_id': 0})
    if user.get('referred_by'):
        raise HTTPException(status_code=400, detail="You already used a referral code")
    
    # Find the referrer
    referrer = await db.users.find_one({'referral_code': code.upper()}, {'_id': 0})
    if not referrer:
        raise HTTPException(status_code=404, detail="Invalid referral code")
    
    if referrer['id'] == current_user['id']:
        raise HTTPException(status_code=400, detail="You can't use your own referral code")
    
    # Update current user
    await db.users.update_one(
        {'id': current_user['id']},
        {'$set': {'referred_by': referrer['id'], 'referred_at': datetime.now(timezone.utc).isoformat()}}
    )
    
    # Increment referrer's count
    await db.users.update_one(
        {'id': referrer['id']},
        {'$inc': {'referral_count': 1}}
    )
    
    # Check for new milestones for referrer
    new_rewards = await check_and_award_referral_milestones(referrer['id'])
    
    # Give welcome bonus to new user
    welcome_bonus = 25
    await db.users.update_one(
        {'id': current_user['id']},
        {'$inc': {'coins': welcome_bonus}}
    )
    
    # Log the referral
    await db.referral_logs.insert_one({
        'id': str(uuid.uuid4()),
        'referrer_id': referrer['id'],
        'referred_id': current_user['id'],
        'code_used': code.upper(),
        'created_at': datetime.now(timezone.utc).isoformat()
    })
    
    return {
        'message': f"Welcome bonus! +{welcome_bonus} coins",
        'referred_by': referrer.get('username', 'A friend'),
        'coins_earned': welcome_bonus
    }


@router.get("/check-code/{code}")
async def check_referral_code(code: str):
    """Check if a referral code is valid (public endpoint for signup)"""
    referrer = await db.users.find_one(
        {'referral_code': code.upper()},
        {'_id': 0, 'username': 1}
    )
    
    if not referrer:
        raise HTTPException(status_code=404, detail="Invalid referral code")
    
    return {
        'valid': True,
        'referrer_username': referrer.get('username', 'A friend'),
        'welcome_bonus': 25
    }


@router.get("/exclusive-items")
async def get_exclusive_items(current_user: dict = Depends(get_current_user)):
    """Get referral exclusive items with unlock status"""
    await seed_referral_items()
    
    user = await db.users.find_one({'id': current_user['id']}, {'_id': 0})
    referral_count = user.get('referral_count', 0)
    
    # Get user's inventory
    inventory = await db.user_inventory.find(
        {'user_id': current_user['id']},
        {'_id': 0, 'item_id': 1}
    ).to_list(100)
    owned_item_ids = [inv['item_id'] for inv in inventory]
    
    items = []
    for item in REFERRAL_EXCLUSIVE_ITEMS:
        is_unlocked = referral_count >= item['referrals_required']
        is_owned = item['id'] in owned_item_ids
        
        items.append({
            **item,
            'is_unlocked': is_unlocked,
            'is_owned': is_owned,
            'current_referrals': referral_count,
            'referrals_needed': max(0, item['referrals_required'] - referral_count)
        })
    
    return {'items': items}


@router.get("/leaderboard")
async def get_referral_leaderboard():
    """Get top referrers"""
    top_referrers = await db.users.find(
        {'referral_count': {'$gt': 0}},
        {'_id': 0, 'id': 1, 'username': 1, 'referral_count': 1}
    ).sort('referral_count', -1).to_list(20)
    
    return {'leaderboard': top_referrers}
