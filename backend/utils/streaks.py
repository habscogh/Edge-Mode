"""
Streak calculation utilities for Edge Mode
"""
from datetime import datetime, timezone

from config import db
from utils.timezone import get_today_string, datetime_to_eastern


async def update_streak(user_id: str, log_date: str):
    """Update user's streak based on new log entry"""
    user = await db.users.find_one({'id': user_id}, {'_id': 0})
    if not user:
        return
    
    log_dt = datetime.fromisoformat(log_date)
    if log_dt.tzinfo is None:
        log_dt = log_dt.replace(tzinfo=timezone.utc)
    
    # Convert to Eastern Time for date comparison
    log_date_eastern = datetime_to_eastern(log_dt).date()
    
    if user.get('last_log_date'):
        last_log_date = datetime.fromisoformat(user['last_log_date']).date()
        days_diff = (log_date_eastern - last_log_date).days
        
        if days_diff > 1:
            # Missed more than 1 day - streak broken
            current_streak = 1
        elif days_diff == 1:
            # Consecutive day - continue streak
            current_streak = user.get('current_streak', 0) + 1
        else:
            # Same day or somehow in the past - keep current streak
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
            'last_log_date': log_date_eastern.isoformat(),
            'total_sessions_completed': total_sessions
        }}
    )
    
    return current_streak, longest_streak, total_sessions
