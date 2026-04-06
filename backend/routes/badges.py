"""
Badge routes for Edge Mode
"""
from fastapi import APIRouter, Depends

from config import db, BADGES
from utils.auth import get_current_user

router = APIRouter(prefix="/badges", tags=["Badges"])


@router.get("/all")
async def get_all_badges():
    """Get all available badges with their definitions"""
    return list(BADGES.values())


@router.get("/user")
async def get_user_badges(current_user: dict = Depends(get_current_user)):
    """Get all badges earned by the current user"""
    user_badges = await db.user_badges.find(
        {'user_id': current_user['id']},
        {'_id': 0}
    ).to_list(100)
    
    earned_badges = []
    for ub in user_badges:
        badge_def = BADGES.get(ub['badge_id'])
        if badge_def:
            earned_badges.append({
                **badge_def,
                'earned_at': ub['earned_at']
            })
    
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


@router.get("/progress")
async def get_badge_progress(current_user: dict = Depends(get_current_user)):
    """Get progress towards unearned badges"""
    user_id = current_user['id']
    user = await db.users.find_one({'id': user_id}, {'_id': 0})
    
    all_sessions = await db.daily_sessions.find({'user_id': user_id}, {'_id': 0}).to_list(10000)
    total_sessions = len(all_sessions)
    total_minutes = sum(s.get('minutes_spent', 0) for s in all_sessions)
    total_hours = total_minutes / 60
    
    current_streak = user.get('current_streak', 0)
    longest_streak = user.get('longest_streak', 0)
    max_streak = max(current_streak, longest_streak)
    
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
    
    if 'streak_21' not in earned_ids:
        progress.append({
            'badge_id': 'streak_21',
            'current': max_streak,
            'target': 21,
            'percent': min(100, (max_streak / 21) * 100)
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
