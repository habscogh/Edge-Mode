"""
Engagement routes for Edge Mode - XP, Levels, Daily Rewards, Friend Streaks, XP Events
"""
from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timezone, timedelta
from typing import Optional
from pydantic import BaseModel
import uuid

from config import db, XP_REWARDS, LEVEL_THRESHOLDS, LEVEL_TITLES, LOGIN_STREAK_BONUSES
from utils.auth import get_current_user, require_admin as get_current_admin
from utils.timezone import get_today_eastern

router = APIRouter(prefix="/engagement", tags=["Engagement"])


# ============ XP Event Models ============

class CreateXPEvent(BaseModel):
    name: str
    description: str
    multiplier: float = 2.0  # 2x XP by default
    event_type: str = "all"  # "all", "sessions", "daily_login", "challenges"
    starts_at: str  # ISO datetime
    ends_at: str  # ISO datetime
    icon: str = "⚡"


class UpdateXPEvent(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    multiplier: Optional[float] = None
    is_active: Optional[bool] = None


# ============ XP Event Helpers ============

async def get_active_xp_event(event_type: str = "all") -> Optional[dict]:
    """Get the currently active XP event that applies to a given action type"""
    now = datetime.now(timezone.utc).isoformat()
    
    # Find active events that match this action type
    event = await db.xp_events.find_one({
        'is_active': True,
        'starts_at': {'$lte': now},
        'ends_at': {'$gte': now},
        '$or': [
            {'event_type': 'all'},
            {'event_type': event_type}
        ]
    }, {'_id': 0})
    
    return event


async def get_xp_multiplier(event_type: str = "all") -> tuple[float, Optional[dict]]:
    """Get current XP multiplier and event info"""
    event = await get_active_xp_event(event_type)
    if event:
        return event.get('multiplier', 1.0), event
    return 1.0, None


def calculate_level(xp: int) -> dict:
    """Calculate user level from XP"""
    level = 1
    for i, threshold in enumerate(LEVEL_THRESHOLDS):
        if xp >= threshold:
            level = i + 1
        else:
            break
    
    # Get XP progress to next level
    current_threshold = LEVEL_THRESHOLDS[min(level - 1, len(LEVEL_THRESHOLDS) - 1)]
    next_threshold = LEVEL_THRESHOLDS[min(level, len(LEVEL_THRESHOLDS) - 1)]
    
    if level >= len(LEVEL_THRESHOLDS):
        # Max level - show progress beyond
        xp_in_level = xp - LEVEL_THRESHOLDS[-1]
        xp_to_next = 10000  # Arbitrary for display
    else:
        xp_in_level = xp - current_threshold
        xp_to_next = next_threshold - current_threshold
    
    progress_pct = min((xp_in_level / xp_to_next) * 100, 100) if xp_to_next > 0 else 100
    
    # Get title
    title = "Rookie"
    for lvl, t in sorted(LEVEL_TITLES.items(), reverse=True):
        if level >= lvl:
            title = t
            break
    
    return {
        'level': level,
        'title': title,
        'total_xp': xp,
        'xp_in_level': xp_in_level,
        'xp_to_next_level': xp_to_next,
        'progress_pct': round(progress_pct, 1)
    }


async def award_xp(user_id: str, amount: int, reason: str, event_type: str = "all") -> dict:
    """Award XP to a user and return updated level info. Applies active event multipliers."""
    user = await db.users.find_one({'id': user_id}, {'_id': 0})
    if not user:
        return None
    
    # Check for active XP event
    multiplier, active_event = await get_xp_multiplier(event_type)
    boosted_amount = int(amount * multiplier)
    
    current_xp = user.get('xp', 0)
    new_xp = current_xp + boosted_amount
    
    old_level_info = calculate_level(current_xp)
    new_level_info = calculate_level(new_xp)
    
    leveled_up = new_level_info['level'] > old_level_info['level']
    
    # Update user XP
    await db.users.update_one(
        {'id': user_id},
        {'$set': {'xp': new_xp}}
    )
    
    # Log XP transaction
    transaction = {
        'user_id': user_id,
        'amount': boosted_amount,
        'base_amount': amount,
        'reason': reason,
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'new_total': new_xp
    }
    
    # Add event info if boosted
    if active_event:
        transaction['event_id'] = active_event.get('id')
        transaction['event_name'] = active_event.get('name')
        transaction['multiplier'] = multiplier
    
    await db.xp_transactions.insert_one(transaction)
    
    return {
        'xp_earned': boosted_amount,
        'base_xp': amount,
        'multiplier': multiplier,
        'event_active': active_event is not None,
        'event_name': active_event.get('name') if active_event else None,
        'reason': reason,
        'leveled_up': leveled_up,
        'old_level': old_level_info['level'],
        'new_level': new_level_info['level'],
        'level_info': new_level_info
    }


@router.post("/daily-login")
async def claim_daily_login(current_user: dict = Depends(get_current_user)):
    """Claim daily login reward - coins and XP for just opening the app"""
    user_id = current_user['id']
    today = get_today_eastern().isoformat()
    
    user = await db.users.find_one({'id': user_id}, {'_id': 0})
    
    # Check if already claimed today
    last_login_claim = user.get('last_login_claim')
    if last_login_claim == today:
        return {
            'already_claimed': True,
            'message': 'Already claimed today!',
            'login_streak': user.get('login_streak', 1),
            'coins': user.get('coins', 0),
            'level_info': calculate_level(user.get('xp', 0))
        }
    
    # Calculate login streak
    yesterday = (get_today_eastern() - timedelta(days=1)).isoformat()
    current_login_streak = user.get('login_streak', 0)
    
    if last_login_claim == yesterday:
        # Continuing streak
        new_login_streak = current_login_streak + 1
    else:
        # Streak broken or first login
        new_login_streak = 1
    
    # Cap streak day for bonus calculation (cycles weekly)
    streak_day = ((new_login_streak - 1) % 7) + 1
    coins_earned = LOGIN_STREAK_BONUSES.get(streak_day, 5)
    
    # Award XP for daily login (with event multiplier)
    xp_result = await award_xp(user_id, XP_REWARDS['daily_login'], 'daily_login', 'daily_login')
    
    # Update user
    current_coins = user.get('coins', 0)
    await db.users.update_one(
        {'id': user_id},
        {'$set': {
            'last_login_claim': today,
            'login_streak': new_login_streak,
            'coins': current_coins + coins_earned
        }}
    )
    
    return {
        'already_claimed': False,
        'coins_earned': coins_earned,
        'xp_earned': XP_REWARDS['daily_login'],
        'login_streak': new_login_streak,
        'streak_day': streak_day,
        'total_coins': current_coins + coins_earned,
        'leveled_up': xp_result.get('leveled_up', False) if xp_result else False,
        'level_info': xp_result.get('level_info') if xp_result else calculate_level(user.get('xp', 0)),
        'message': f"🎁 +{coins_earned} coins, +{XP_REWARDS['daily_login']} XP!"
    }


@router.get("/status")
async def get_engagement_status(current_user: dict = Depends(get_current_user)):
    """Get user's current XP, level, coins, streaks, and active events"""
    user = await db.users.find_one({'id': current_user['id']}, {'_id': 0, 'password': 0})
    
    today = get_today_eastern().isoformat()
    can_claim_daily = user.get('last_login_claim') != today
    
    # Check for active XP event
    active_event = await get_active_xp_event()
    
    return {
        'xp': user.get('xp', 0),
        'level_info': calculate_level(user.get('xp', 0)),
        'coins': user.get('coins', 0),
        'login_streak': user.get('login_streak', 0),
        'session_streak': user.get('current_streak', 0),
        'can_claim_daily': can_claim_daily,
        'last_login_claim': user.get('last_login_claim'),
        'active_event': {
            'id': active_event.get('id'),
            'name': active_event.get('name'),
            'description': active_event.get('description'),
            'multiplier': active_event.get('multiplier'),
            'icon': active_event.get('icon', '⚡'),
            'ends_at': active_event.get('ends_at')
        } if active_event else None
    }


@router.get("/leaderboard/xp")
async def get_xp_leaderboard(limit: int = 25):
    """Get top users by XP/Level"""
    users = await db.users.find(
        {'is_admin': {'$ne': True}},
        {'_id': 0, 'id': 1, 'username': 1, 'xp': 1}
    ).sort('xp', -1).to_list(limit)
    
    leaderboard = []
    for i, user in enumerate(users):
        level_info = calculate_level(user.get('xp', 0))
        leaderboard.append({
            'rank': i + 1,
            'username': user.get('username', 'Anonymous'),
            'xp': user.get('xp', 0),
            'level': level_info['level'],
            'title': level_info['title']
        })
    
    return {'leaderboard': leaderboard}


# ============ Friend Streaks (Snap Streaks Style) ============

@router.get("/friend-streaks")
async def get_friend_streaks(current_user: dict = Depends(get_current_user)):
    """Get mutual activity streaks with friends (people you've both logged on same days)"""
    user_id = current_user['id']
    today = get_today_eastern()
    
    # Get user's groups to find teammates
    user_groups = await db.groups.find(
        {'members': user_id}
    ).to_list(10)
    
    # Get all teammate IDs
    teammate_ids = set()
    for group in user_groups:
        for member_id in group.get('members', []):
            if member_id != user_id:
                teammate_ids.add(member_id)
    
    # Also check friend challenges to find friends
    friend_challenges = await db.friend_challenges.find({
        '$or': [
            {'challenger_id': user_id},
            {'challenged_id': user_id}
        ]
    }).to_list(100)
    
    for challenge in friend_challenges:
        if challenge['challenger_id'] == user_id:
            teammate_ids.add(challenge['challenged_id'])
        else:
            teammate_ids.add(challenge['challenger_id'])
    
    if not teammate_ids:
        return {'friend_streaks': [], 'message': 'Join a team or challenge friends to see mutual streaks!'}
    
    # Get user's session dates for last 30 days
    thirty_days_ago = (today - timedelta(days=30)).isoformat()
    user_sessions = await db.daily_sessions.find({
        'user_id': user_id,
        'date': {'$gte': thirty_days_ago}
    }, {'_id': 0, 'date': 1}).to_list(100)
    user_dates = set(s['date'] for s in user_sessions)
    
    friend_streaks = []
    
    for friend_id in teammate_ids:
        # Get friend info
        friend = await db.users.find_one({'id': friend_id}, {'_id': 0, 'id': 1, 'username': 1})
        if not friend:
            continue
        
        # Get friend's session dates
        friend_sessions = await db.daily_sessions.find({
            'user_id': friend_id,
            'date': {'$gte': thirty_days_ago}
        }, {'_id': 0, 'date': 1}).to_list(100)
        friend_dates = set(s['date'] for s in friend_sessions)
        
        # Find mutual dates (both logged on same day)
        mutual_dates = user_dates.intersection(friend_dates)
        
        if not mutual_dates:
            continue
        
        # Calculate current mutual streak (consecutive days both logged)
        sorted_dates = sorted(mutual_dates, reverse=True)
        streak = 0
        check_date = today
        
        for i in range(30):
            date_str = check_date.isoformat()
            if date_str in mutual_dates:
                streak += 1
                check_date -= timedelta(days=1)
            else:
                # Allow one day gap for "active" streaks
                if i == 0:
                    check_date -= timedelta(days=1)
                    continue
                break
        
        if streak > 0:
            friend_streaks.append({
                'friend_id': friend_id,
                'friend_username': friend.get('username', 'Friend'),
                'mutual_streak': streak,
                'total_mutual_days': len(mutual_dates)
            })
    
    # Sort by streak length
    friend_streaks.sort(key=lambda x: x['mutual_streak'], reverse=True)
    
    return {'friend_streaks': friend_streaks[:10]}  # Top 10 friend streaks


@router.get("/xp-history")
async def get_xp_history(current_user: dict = Depends(get_current_user), limit: int = 20):
    """Get recent XP transactions"""
    transactions = await db.xp_transactions.find(
        {'user_id': current_user['id']},
        {'_id': 0}
    ).sort('timestamp', -1).to_list(limit)
    
    return {'transactions': transactions}


# ============ XP Events Endpoints ============

@router.get("/events/active")
async def get_active_events():
    """Get all currently active XP events (public endpoint)"""
    now = datetime.now(timezone.utc).isoformat()
    
    events = await db.xp_events.find({
        'is_active': True,
        'starts_at': {'$lte': now},
        'ends_at': {'$gte': now}
    }, {'_id': 0}).to_list(10)
    
    # Calculate time remaining for each event
    for event in events:
        ends_at = datetime.fromisoformat(event['ends_at'].replace('Z', '+00:00'))
        now_dt = datetime.now(timezone.utc)
        remaining = ends_at - now_dt
        event['hours_remaining'] = max(0, int(remaining.total_seconds() / 3600))
        event['minutes_remaining'] = max(0, int((remaining.total_seconds() % 3600) / 60))
    
    return {'events': events}


@router.get("/events/upcoming")
async def get_upcoming_events():
    """Get upcoming XP events (starts within 7 days)"""
    now = datetime.now(timezone.utc).isoformat()
    week_later = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
    
    events = await db.xp_events.find({
        'is_active': True,
        'starts_at': {'$gt': now, '$lte': week_later}
    }, {'_id': 0}).sort('starts_at', 1).to_list(10)
    
    return {'events': events}


@router.get("/events")
async def list_all_events(current_user: dict = Depends(get_current_admin)):
    """Admin: List all XP events"""
    events = await db.xp_events.find({}, {'_id': 0}).sort('created_at', -1).to_list(100)
    return {'events': events}


@router.post("/events")
async def create_xp_event(event_data: CreateXPEvent, current_user: dict = Depends(get_current_admin)):
    """Admin: Create a new XP event"""
    # Validate dates
    try:
        starts_at = datetime.fromisoformat(event_data.starts_at.replace('Z', '+00:00'))
        ends_at = datetime.fromisoformat(event_data.ends_at.replace('Z', '+00:00'))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use ISO format.")
    
    if ends_at <= starts_at:
        raise HTTPException(status_code=400, detail="End date must be after start date")
    
    if event_data.multiplier < 1.0 or event_data.multiplier > 10.0:
        raise HTTPException(status_code=400, detail="Multiplier must be between 1.0 and 10.0")
    
    event_doc = {
        'id': str(uuid.uuid4()),
        'name': event_data.name,
        'description': event_data.description,
        'multiplier': event_data.multiplier,
        'event_type': event_data.event_type,
        'icon': event_data.icon,
        'starts_at': starts_at.isoformat(),
        'ends_at': ends_at.isoformat(),
        'is_active': True,
        'created_by': current_user['id'],
        'created_at': datetime.now(timezone.utc).isoformat()
    }
    
    await db.xp_events.insert_one(event_doc)
    
    return {
        'message': f"XP Event '{event_data.name}' created!",
        'event': {k: v for k, v in event_doc.items() if k != '_id'}
    }


@router.put("/events/{event_id}")
async def update_xp_event(event_id: str, update_data: UpdateXPEvent, current_user: dict = Depends(get_current_admin)):
    """Admin: Update an XP event"""
    event = await db.xp_events.find_one({'id': event_id}, {'_id': 0})
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    updates = {}
    if update_data.name is not None:
        updates['name'] = update_data.name
    if update_data.description is not None:
        updates['description'] = update_data.description
    if update_data.multiplier is not None:
        if update_data.multiplier < 1.0 or update_data.multiplier > 10.0:
            raise HTTPException(status_code=400, detail="Multiplier must be between 1.0 and 10.0")
        updates['multiplier'] = update_data.multiplier
    if update_data.is_active is not None:
        updates['is_active'] = update_data.is_active
    
    if updates:
        updates['updated_at'] = datetime.now(timezone.utc).isoformat()
        await db.xp_events.update_one({'id': event_id}, {'$set': updates})
    
    return {'message': 'Event updated', 'updates': updates}


@router.delete("/events/{event_id}")
async def delete_xp_event(event_id: str, current_user: dict = Depends(get_current_admin)):
    """Admin: Delete an XP event"""
    result = await db.xp_events.delete_one({'id': event_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Event not found")
    
    return {'message': 'Event deleted'}


# ============ Quick Event Creation Helpers ============

@router.post("/events/quick/double-xp-weekend")
async def create_double_xp_weekend(current_user: dict = Depends(get_current_admin)):
    """Admin: Quick create a Double XP Weekend (Sat-Sun)"""
    now = datetime.now(timezone.utc)
    
    # Find next Saturday
    days_until_saturday = (5 - now.weekday()) % 7
    if days_until_saturday == 0 and now.hour >= 12:
        days_until_saturday = 7  # Next week's Saturday
    
    saturday = now + timedelta(days=days_until_saturday)
    saturday = saturday.replace(hour=0, minute=0, second=0, microsecond=0)
    sunday_end = saturday + timedelta(days=2)  # End of Sunday
    
    event_data = CreateXPEvent(
        name="🔥 Double XP Weekend!",
        description="Earn 2x XP on all activities this weekend!",
        multiplier=2.0,
        event_type="all",
        starts_at=saturday.isoformat(),
        ends_at=sunday_end.isoformat(),
        icon="🔥"
    )
    
    return await create_xp_event(event_data, current_user)


@router.post("/events/quick/challenge-rush")
async def create_challenge_rush(hours: int = 24, multiplier: float = 3.0, current_user: dict = Depends(get_current_admin)):
    """Admin: Quick create a Challenge Rush event (bonus XP for challenges)"""
    now = datetime.now(timezone.utc)
    ends_at = now + timedelta(hours=hours)
    
    event_data = CreateXPEvent(
        name=f"⚡ {int(multiplier)}x Challenge Rush!",
        description=f"Earn {int(multiplier)}x XP for the next {hours} hours!",
        multiplier=multiplier,
        event_type="all",
        starts_at=now.isoformat(),
        ends_at=ends_at.isoformat(),
        icon="⚡"
    )
    
    return await create_xp_event(event_data, current_user)


@router.post("/events/{event_id}/broadcast")
async def broadcast_event_notification(event_id: str, current_user: dict = Depends(get_current_admin)):
    """Admin: Manually broadcast push notifications for an event"""
    event = await db.xp_events.find_one({'id': event_id}, {'_id': 0})
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Import push functions
    from routes.push import broadcast_xp_event_started
    
    # Send notifications
    sent_count = await broadcast_xp_event_started(event)
    
    return {
        'message': f"Broadcast sent for '{event.get('name')}'",
        'notifications_sent': sent_count
    }

