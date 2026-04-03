"""
Quests routes for Edge Mode - Daily & Weekly Quests with Coin Rewards
"""
from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timezone, timedelta
from typing import Optional, List
from pydantic import BaseModel
import uuid

from config import db
from utils.auth import get_current_user, require_admin as get_current_admin
from utils.timezone import get_today_eastern, get_eastern_now

router = APIRouter(prefix="/quests", tags=["Quests"])


# ============ Quest Definitions ============

DAILY_QUESTS = [
    {
        "id": "daily-login",
        "name": "Daily Check-In",
        "description": "Log in to the app",
        "icon": "👋",
        "target": 1,
        "reward_coins": 1,
        "reward_xp": 0,
        "track_field": "logins",
        "difficulty": "easy"
    },
    {
        "id": "daily-session",
        "name": "One Session Wonder",
        "description": "Log at least 1 session today",
        "icon": "📝",
        "target": 1,
        "reward_coins": 2,
        "reward_xp": 5,
        "track_field": "sessions_logged",
        "difficulty": "easy"
    },
    {
        "id": "daily-sessions-3",
        "name": "Triple Threat",
        "description": "Log 3 sessions today",
        "icon": "🎯",
        "target": 3,
        "reward_coins": 3,
        "reward_xp": 15,
        "track_field": "sessions_logged",
        "difficulty": "medium"
    },
    {
        "id": "daily-xp-50",
        "name": "XP Hunter",
        "description": "Earn 50 XP today",
        "icon": "⚡",
        "target": 50,
        "reward_coins": 2,
        "reward_xp": 0,
        "track_field": "xp_earned",
        "difficulty": "medium"
    },
    {
        "id": "daily-streak-maintain",
        "name": "Streak Keeper",
        "description": "Maintain your streak today",
        "icon": "🔥",
        "target": 1,
        "reward_coins": 2,
        "reward_xp": 5,
        "track_field": "streak_maintained",
        "difficulty": "easy"
    }
]

WEEKLY_QUESTS = [
    {
        "id": "weekly-sessions-10",
        "name": "Consistency Champion",
        "description": "Log 10 sessions this week",
        "icon": "🏆",
        "target": 10,
        "reward_coins": 5,
        "reward_xp": 30,
        "track_field": "sessions_logged",
        "difficulty": "medium"
    },
    {
        "id": "weekly-sessions-20",
        "name": "Dedication Master",
        "description": "Log 20 sessions this week",
        "icon": "💪",
        "target": 20,
        "reward_coins": 10,
        "reward_xp": 50,
        "track_field": "sessions_logged",
        "difficulty": "hard"
    },
    {
        "id": "weekly-xp-200",
        "name": "XP Grinder",
        "description": "Earn 200 XP this week",
        "icon": "⚡",
        "target": 200,
        "reward_coins": 4,
        "reward_xp": 0,
        "track_field": "xp_earned",
        "difficulty": "medium"
    },
    {
        "id": "weekly-streak-7",
        "name": "Perfect Week",
        "description": "Maintain a 7-day streak",
        "icon": "🌟",
        "target": 7,
        "reward_coins": 8,
        "reward_xp": 50,
        "track_field": "streak_days",
        "difficulty": "hard"
    },
    {
        "id": "weekly-login-5",
        "name": "Dedicated User",
        "description": "Log in 5 different days this week",
        "icon": "📅",
        "target": 5,
        "reward_coins": 3,
        "reward_xp": 20,
        "track_field": "login_days",
        "difficulty": "easy"
    },
    {
        "id": "weekly-challenges",
        "name": "Challenge Accepted",
        "description": "Complete 2 challenges this week",
        "icon": "🎮",
        "target": 2,
        "reward_coins": 6,
        "reward_xp": 40,
        "track_field": "challenges_completed",
        "difficulty": "hard"
    }
]


# ============ Helper Functions ============

def get_week_start_eastern() -> datetime:
    """Get the start of the current week (Sunday) in Eastern time"""
    now = get_eastern_now()
    # Go back to Sunday
    days_since_sunday = now.weekday() + 1  # Monday is 0, so Sunday is -1 + 7 = 6... actually weekday() returns 6 for Sunday
    if now.weekday() == 6:  # Sunday
        days_since_sunday = 0
    else:
        days_since_sunday = now.weekday() + 1
    
    week_start = now - timedelta(days=days_since_sunday)
    return week_start.replace(hour=0, minute=0, second=0, microsecond=0)


def get_difficulty_color(difficulty: str) -> str:
    """Get color for difficulty level"""
    colors = {
        "easy": "#22c55e",      # Green
        "medium": "#f59e0b",    # Amber
        "hard": "#ef4444"       # Red
    }
    return colors.get(difficulty, "#9ca3af")


async def get_user_quest_progress(user_id: str, quest_type: str = "daily") -> dict:
    """Get or create user's quest progress for today/this week"""
    today = get_today_eastern().isoformat()
    week_start = get_week_start_eastern().isoformat()[:10]  # Just the date part
    
    period_key = today if quest_type == "daily" else week_start
    
    progress = await db.quest_progress.find_one({
        'user_id': user_id,
        'quest_type': quest_type,
        'period': period_key
    }, {'_id': 0})
    
    if not progress:
        # Create new progress document
        progress = {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'quest_type': quest_type,
            'period': period_key,
            'progress': {},  # quest_id -> current progress
            'completed': [],  # list of completed quest_ids
            'claimed': [],  # list of claimed quest_ids
            'created_at': datetime.now(timezone.utc).isoformat()
        }
        await db.quest_progress.insert_one(progress)
    
    return progress


async def update_quest_progress(user_id: str, track_field: str, amount: int = 1, quest_type: str = "both"):
    """
    Update user's quest progress for a specific tracking field.
    Called when user performs actions (logs session, earns XP, etc.)
    """
    types_to_update = ["daily", "weekly"] if quest_type == "both" else [quest_type]
    
    for qtype in types_to_update:
        progress = await get_user_quest_progress(user_id, qtype)
        quests = DAILY_QUESTS if qtype == "daily" else WEEKLY_QUESTS
        
        # Find quests that track this field
        updated = False
        for quest in quests:
            if quest['track_field'] == track_field and quest['id'] not in progress.get('completed', []):
                current = progress.get('progress', {}).get(quest['id'], 0)
                new_value = current + amount
                
                if 'progress' not in progress:
                    progress['progress'] = {}
                progress['progress'][quest['id']] = new_value
                updated = True
                
                # Check if quest is now complete
                if new_value >= quest['target'] and quest['id'] not in progress.get('completed', []):
                    if 'completed' not in progress:
                        progress['completed'] = []
                    progress['completed'].append(quest['id'])
        
        if updated:
            await db.quest_progress.update_one(
                {'id': progress['id']},
                {'$set': {
                    'progress': progress.get('progress', {}),
                    'completed': progress.get('completed', [])
                }}
            )


# ============ API Endpoints ============

@router.get("/daily")
async def get_daily_quests(current_user: dict = Depends(get_current_user)):
    """Get user's daily quests with progress"""
    progress = await get_user_quest_progress(current_user['id'], "daily")
    
    quests_with_progress = []
    for quest in DAILY_QUESTS:
        current_progress = progress.get('progress', {}).get(quest['id'], 0)
        is_completed = quest['id'] in progress.get('completed', [])
        is_claimed = quest['id'] in progress.get('claimed', [])
        
        quests_with_progress.append({
            **quest,
            'current': min(current_progress, quest['target']),
            'is_completed': is_completed,
            'is_claimed': is_claimed,
            'progress_pct': min(100, (current_progress / quest['target']) * 100),
            'difficulty_color': get_difficulty_color(quest['difficulty'])
        })
    
    # Calculate totals
    total_quests = len(DAILY_QUESTS)
    completed_count = len([q for q in quests_with_progress if q['is_completed']])
    claimed_count = len([q for q in quests_with_progress if q['is_claimed']])
    
    return {
        'quests': quests_with_progress,
        'summary': {
            'total': total_quests,
            'completed': completed_count,
            'claimed': claimed_count,
            'available_rewards': sum(q['reward_coins'] for q in quests_with_progress if q['is_completed'] and not q['is_claimed'])
        },
        'resets_at': get_today_eastern().isoformat() + "T00:00:00-05:00"  # Midnight Eastern tomorrow
    }


@router.get("/weekly")
async def get_weekly_quests(current_user: dict = Depends(get_current_user)):
    """Get user's weekly quests with progress"""
    progress = await get_user_quest_progress(current_user['id'], "weekly")
    
    quests_with_progress = []
    for quest in WEEKLY_QUESTS:
        current_progress = progress.get('progress', {}).get(quest['id'], 0)
        is_completed = quest['id'] in progress.get('completed', [])
        is_claimed = quest['id'] in progress.get('claimed', [])
        
        quests_with_progress.append({
            **quest,
            'current': min(current_progress, quest['target']),
            'is_completed': is_completed,
            'is_claimed': is_claimed,
            'progress_pct': min(100, (current_progress / quest['target']) * 100),
            'difficulty_color': get_difficulty_color(quest['difficulty'])
        })
    
    # Calculate totals
    total_quests = len(WEEKLY_QUESTS)
    completed_count = len([q for q in quests_with_progress if q['is_completed']])
    claimed_count = len([q for q in quests_with_progress if q['is_claimed']])
    
    # Calculate when week resets (next Sunday midnight Eastern)
    week_start = get_week_start_eastern()
    next_week_start = week_start + timedelta(days=7)
    
    return {
        'quests': quests_with_progress,
        'summary': {
            'total': total_quests,
            'completed': completed_count,
            'claimed': claimed_count,
            'available_rewards': sum(q['reward_coins'] for q in quests_with_progress if q['is_completed'] and not q['is_claimed'])
        },
        'week_start': week_start.isoformat(),
        'resets_at': next_week_start.isoformat()
    }


@router.get("/all")
async def get_all_quests(current_user: dict = Depends(get_current_user)):
    """Get both daily and weekly quests"""
    daily = await get_daily_quests(current_user)
    weekly = await get_weekly_quests(current_user)
    
    return {
        'daily': daily,
        'weekly': weekly,
        'total_available_rewards': daily['summary']['available_rewards'] + weekly['summary']['available_rewards']
    }


@router.post("/claim/{quest_id}")
async def claim_quest_reward(quest_id: str, current_user: dict = Depends(get_current_user)):
    """Claim reward for a completed quest"""
    # Find the quest
    quest = None
    quest_type = None
    
    for q in DAILY_QUESTS:
        if q['id'] == quest_id:
            quest = q
            quest_type = "daily"
            break
    
    if not quest:
        for q in WEEKLY_QUESTS:
            if q['id'] == quest_id:
                quest = q
                quest_type = "weekly"
                break
    
    if not quest:
        raise HTTPException(status_code=404, detail="Quest not found")
    
    # Get user's progress
    progress = await get_user_quest_progress(current_user['id'], quest_type)
    
    # Check if completed
    if quest_id not in progress.get('completed', []):
        raise HTTPException(status_code=400, detail="Quest not completed yet")
    
    # Check if already claimed
    if quest_id in progress.get('claimed', []):
        raise HTTPException(status_code=400, detail="Reward already claimed")
    
    # Award coins and XP
    user = await db.users.find_one({'id': current_user['id']}, {'_id': 0})
    current_coins = user.get('coins', 0)
    current_xp = user.get('xp', 0)
    
    new_coins = current_coins + quest['reward_coins']
    new_xp = current_xp + quest['reward_xp']
    
    await db.users.update_one(
        {'id': current_user['id']},
        {'$set': {'coins': new_coins, 'xp': new_xp}}
    )
    
    # Mark as claimed
    await db.quest_progress.update_one(
        {'id': progress['id']},
        {'$push': {'claimed': quest_id}}
    )
    
    # Log coin transaction
    await db.coin_transactions.insert_one({
        'user_id': current_user['id'],
        'amount': quest['reward_coins'],
        'reason': f"Quest reward: {quest['name']}",
        'quest_id': quest_id,
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'new_balance': new_coins
    })
    
    # Log XP if awarded
    if quest['reward_xp'] > 0:
        await db.xp_transactions.insert_one({
            'user_id': current_user['id'],
            'amount': quest['reward_xp'],
            'reason': f"quest_reward:{quest_id}",
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'new_total': new_xp
        })
    
    return {
        'message': f"🎉 Quest Complete! +{quest['reward_coins']} coins" + (f", +{quest['reward_xp']} XP" if quest['reward_xp'] > 0 else ""),
        'coins_earned': quest['reward_coins'],
        'xp_earned': quest['reward_xp'],
        'new_coin_balance': new_coins,
        'new_xp_total': new_xp,
        'quest': quest
    }


@router.post("/claim-all/{quest_type}")
async def claim_all_rewards(quest_type: str, current_user: dict = Depends(get_current_user)):
    """Claim all completed quest rewards at once"""
    if quest_type not in ["daily", "weekly"]:
        raise HTTPException(status_code=400, detail="Invalid quest type")
    
    progress = await get_user_quest_progress(current_user['id'], quest_type)
    quests = DAILY_QUESTS if quest_type == "daily" else WEEKLY_QUESTS
    
    # Find completed but unclaimed quests
    claimable = []
    for quest in quests:
        if quest['id'] in progress.get('completed', []) and quest['id'] not in progress.get('claimed', []):
            claimable.append(quest)
    
    if not claimable:
        raise HTTPException(status_code=400, detail="No rewards to claim")
    
    # Calculate totals
    total_coins = sum(q['reward_coins'] for q in claimable)
    total_xp = sum(q['reward_xp'] for q in claimable)
    
    # Award rewards
    user = await db.users.find_one({'id': current_user['id']}, {'_id': 0})
    new_coins = user.get('coins', 0) + total_coins
    new_xp = user.get('xp', 0) + total_xp
    
    await db.users.update_one(
        {'id': current_user['id']},
        {'$set': {'coins': new_coins, 'xp': new_xp}}
    )
    
    # Mark all as claimed
    claimed_ids = [q['id'] for q in claimable]
    await db.quest_progress.update_one(
        {'id': progress['id']},
        {'$push': {'claimed': {'$each': claimed_ids}}}
    )
    
    # Log transaction
    await db.coin_transactions.insert_one({
        'user_id': current_user['id'],
        'amount': total_coins,
        'reason': f"Claimed {len(claimable)} {quest_type} quest rewards",
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'new_balance': new_coins
    })
    
    return {
        'message': f"🎉 Claimed {len(claimable)} rewards! +{total_coins} coins" + (f", +{total_xp} XP" if total_xp > 0 else ""),
        'quests_claimed': len(claimable),
        'total_coins': total_coins,
        'total_xp': total_xp,
        'new_coin_balance': new_coins,
        'new_xp_total': new_xp
    }


# ============ Quest Progress Tracking (called from other routes) ============

async def track_session_logged(user_id: str):
    """Track when a user logs a session"""
    await update_quest_progress(user_id, "sessions_logged", 1, "both")
    await update_quest_progress(user_id, "streak_maintained", 1, "daily")


async def track_xp_earned(user_id: str, amount: int):
    """Track when a user earns XP"""
    await update_quest_progress(user_id, "xp_earned", amount, "both")


async def track_login(user_id: str):
    """Track daily login"""
    # Check if already logged in today
    today = get_today_eastern().isoformat()
    progress = await get_user_quest_progress(user_id, "daily")
    
    # Update daily login quest
    await update_quest_progress(user_id, "logins", 1, "daily")
    
    # Update weekly login days (only count unique days)
    week_progress = await get_user_quest_progress(user_id, "weekly")
    login_days = week_progress.get('login_days_set', set())
    
    if today not in login_days:
        await db.quest_progress.update_one(
            {'id': week_progress['id']},
            {
                '$addToSet': {'login_days_set': today},
                '$set': {f'progress.weekly-login-5': len(login_days) + 1}
            }
        )
        
        # Check if weekly login quest is complete
        if len(login_days) + 1 >= 5:
            await db.quest_progress.update_one(
                {'id': week_progress['id']},
                {'$addToSet': {'completed': 'weekly-login-5'}}
            )


async def track_streak_days(user_id: str, streak_days: int):
    """Track streak days for weekly quest"""
    await db.quest_progress.update_one(
        {'user_id': user_id, 'quest_type': 'weekly'},
        {'$set': {'progress.weekly-streak-7': streak_days}}
    )
    
    if streak_days >= 7:
        await db.quest_progress.update_one(
            {'user_id': user_id, 'quest_type': 'weekly'},
            {'$addToSet': {'completed': 'weekly-streak-7'}}
        )


async def track_challenge_completed(user_id: str):
    """Track when user completes a challenge"""
    await update_quest_progress(user_id, "challenges_completed", 1, "weekly")
