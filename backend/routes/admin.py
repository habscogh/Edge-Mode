"""
Admin routes for Edge Mode
"""
from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel
from typing import Optional, List
import os

from config import db, logger
from utils.auth import require_admin

router = APIRouter(prefix="/admin", tags=["Admin"])

# Try to import resend for email sending
try:
    import resend
    resend.api_key = os.environ.get('RESEND_API_KEY')
    RESEND_AVAILABLE = bool(resend.api_key)
except ImportError:
    RESEND_AVAILABLE = False


class GroupMessageRequest(BaseModel):
    subject: str
    message: str
    send_email: bool = True


@router.get("/stats")
async def get_admin_stats(admin_user: dict = Depends(require_admin)):
    """Get overall app statistics for admin dashboard"""
    now = datetime.now(timezone.utc)
    today = now.date().isoformat()
    week_ago = (now - timedelta(days=7)).isoformat()
    
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
    
    active_user_ids = await db.daily_sessions.distinct('user_id', {
        'timestamp': {'$gte': week_ago}
    })
    active_users = len(active_user_ids)
    
    total_sessions = await db.daily_sessions.count_documents({})
    sessions_today = await db.daily_sessions.count_documents({
        'date': today
    })
    sessions_this_week = await db.daily_sessions.count_documents({
        'timestamp': {'$gte': week_ago}
    })
    
    paid_subscribers = await db.users.count_documents({'subscription_active': True})
    trial_users = await db.users.count_documents({
        'subscription_active': {'$ne': True},
        'trial_ends_at': {'$gte': now.isoformat()}
    })
    
    total_groups = await db.groups.count_documents({})
    
    # Ambassador count
    ambassador_count = await db.users.count_documents({'is_ambassador': True})
    
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
        'ambassadors': {
            'total': ambassador_count
        },
        'generated_at': now.isoformat()
    }


@router.get("/users")
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


@router.get("/recent-activity")
async def get_recent_activity(admin_user: dict = Depends(require_admin)):
    """Get recent signups and sessions"""
    now = datetime.now(timezone.utc)
    week_ago = (now - timedelta(days=7)).isoformat()
    
    recent_signups = await db.users.find(
        {'join_date': {'$gte': (now - timedelta(days=7)).date().isoformat()}},
        {'_id': 0, 'id': 1, 'username': 1, 'email': 1, 'join_date': 1}
    ).sort('join_date', -1).to_list(20)
    
    recent_sessions = await db.daily_sessions.find(
        {'timestamp': {'$gte': week_ago}},
        {'_id': 0}
    ).sort('timestamp', -1).limit(20).to_list(20)
    
    for session in recent_sessions:
        user = await db.users.find_one({'id': session['user_id']}, {'_id': 0, 'username': 1})
        session['username'] = user.get('username', 'Unknown') if user else 'Unknown'
    
    return {
        'recent_signups': recent_signups,
        'recent_sessions': recent_sessions
    }
