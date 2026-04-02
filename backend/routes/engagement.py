"""
Engagement routes for Edge Mode - XP, Levels, Daily Rewards, Friend Streaks
"""
from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timezone, timedelta
from typing import Optional

from config import db, XP_REWARDS, LEVEL_THRESHOLDS, LEVEL_TITLES, LOGIN_STREAK_BONUSES
from utils.auth import get_current_user
from utils.timezone import get_today_eastern

router = APIRouter(prefix="/engagement", tags=["Engagement"])


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


async def award_xp(user_id: str, amount: int, reason: str) -> dict:
    """Award XP to a user and return updated level info"""
    user = await db.users.find_one({'id': user_id}, {'_id': 0})
    if not user:
        return None
    
    current_xp = user.get('xp', 0)
    new_xp = current_xp + amount
    
    old_level_info = calculate_level(current_xp)
    new_level_info = calculate_level(new_xp)
    
    leveled_up = new_level_info['level'] > old_level_info['level']
    
    # Update user XP
    await db.users.update_one(
        {'id': user_id},
        {'$set': {'xp': new_xp}}
    )
    
    # Log XP transaction
    await db.xp_transactions.insert_one({
        'user_id': user_id,
        'amount': amount,
        'reason': reason,
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'new_total': new_xp
    })
    
    return {
        'xp_earned': amount,
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
    
    # Award XP for daily login
    xp_result = await award_xp(user_id, XP_REWARDS['daily_login'], 'daily_login')
    
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
    """Get user's current XP, level, coins, and streaks"""
    user = await db.users.find_one({'id': current_user['id']}, {'_id': 0, 'password': 0})
    
    today = get_today_eastern().isoformat()
    can_claim_daily = user.get('last_login_claim') != today
    
    return {
        'xp': user.get('xp', 0),
        'level_info': calculate_level(user.get('xp', 0)),
        'coins': user.get('coins', 0),
        'login_streak': user.get('login_streak', 0),
        'session_streak': user.get('current_streak', 0),
        'can_claim_daily': can_claim_daily,
        'last_login_claim': user.get('last_login_claim')
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
