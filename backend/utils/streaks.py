"""
Streak calculation utilities for Edge Mode
"""
from datetime import datetime, timezone

from config import db


async def update_streak(user_id: str, log_date: str):
    """Update user's streak based on new log entry"""
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
