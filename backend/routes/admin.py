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


class SubscriptionActivateRequest(BaseModel):
    email: str
    plan: str = "yearly"  # "monthly" or "yearly"
    duration_days: int = 365  # Default 1 year


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



@router.get("/ambassadors")
async def get_ambassadors(admin_user: dict = Depends(require_admin)):
    """Get list of all ambassadors"""
    ambassadors = await db.users.find(
        {'is_ambassador': True},
        {'_id': 0, 'password_hash': 0}
    ).sort('ambassador_since', -1).to_list(500)
    
    total = await db.users.count_documents({'is_ambassador': True})
    
    return {
        'ambassadors': ambassadors,
        'total': total
    }


@router.get("/subscribers")
async def get_subscribers(admin_user: dict = Depends(require_admin)):
    """Get list of all active subscribers (paid or valid trial)"""
    now = datetime.now(timezone.utc)
    
    # Get paid subscribers
    paid_subscribers = await db.users.find(
        {'subscription_active': True},
        {'_id': 0, 'password_hash': 0}
    ).sort('subscription_start_date', -1).to_list(500)
    
    # Get users with active trial
    trial_users = await db.users.find(
        {
            'subscription_active': {'$ne': True},
            'trial_ends_at': {'$gte': now.isoformat()}
        },
        {'_id': 0, 'password_hash': 0}
    ).sort('join_date', -1).to_list(500)
    
    return {
        'paid_subscribers': paid_subscribers,
        'paid_count': len(paid_subscribers),
        'trial_users': trial_users,
        'trial_count': len(trial_users),
        'total': len(paid_subscribers) + len(trial_users)
    }


@router.post("/messages/ambassadors")
async def send_ambassador_message(
    request: GroupMessageRequest,
    admin_user: dict = Depends(require_admin)
):
    """Send a message to all ambassadors"""
    ambassadors = await db.users.find(
        {'is_ambassador': True},
        {'_id': 0, 'id': 1, 'email': 1, 'username': 1}
    ).to_list(500)
    
    if not ambassadors:
        return {'message': 'No ambassadors found', 'sent_to': 0}
    
    # Store message in database
    message_doc = {
        'type': 'ambassador_message',
        'subject': request.subject,
        'message': request.message,
        'sent_by': admin_user['id'],
        'sent_at': datetime.now(timezone.utc).isoformat(),
        'recipient_count': len(ambassadors),
        'recipients': [a['email'] for a in ambassadors]
    }
    await db.admin_messages.insert_one(message_doc)
    
    # Send emails if requested and resend is available
    emails_sent = 0
    if request.send_email and RESEND_AVAILABLE:
        for ambassador in ambassadors:
            try:
                resend.Emails.send({
                    "from": "Edge Mode <notifications@edgemodeapp.com>",
                    "to": ambassador['email'],
                    "subject": request.subject,
                    "html": f"""
                    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                        <h2 style="color: #22c55e;">🌟 Ambassador Update</h2>
                        <p>Hi {ambassador.get('username', 'Ambassador')},</p>
                        <div style="background: #f4f4f5; padding: 20px; border-radius: 8px; margin: 20px 0;">
                            {request.message.replace(chr(10), '<br>')}
                        </div>
                        <p style="color: #666;">Thank you for being a Founding Ambassador!</p>
                        <p style="color: #666;">- The Edge Mode Team</p>
                    </div>
                    """
                })
                emails_sent += 1
            except Exception as e:
                logger.error(f"Failed to send email to {ambassador['email']}: {e}")
    
    return {
        'message': 'Message sent to ambassadors',
        'sent_to': len(ambassadors),
        'emails_sent': emails_sent if request.send_email else 'Email sending disabled',
        'email_available': RESEND_AVAILABLE
    }


@router.post("/messages/subscribers")
async def send_subscriber_message(
    request: GroupMessageRequest,
    admin_user: dict = Depends(require_admin)
):
    """Send a message to all active subscribers (paid only)"""
    subscribers = await db.users.find(
        {'subscription_active': True},
        {'_id': 0, 'id': 1, 'email': 1, 'username': 1}
    ).to_list(500)
    
    if not subscribers:
        return {'message': 'No paid subscribers found', 'sent_to': 0}
    
    # Store message in database
    message_doc = {
        'type': 'subscriber_message',
        'subject': request.subject,
        'message': request.message,
        'sent_by': admin_user['id'],
        'sent_at': datetime.now(timezone.utc).isoformat(),
        'recipient_count': len(subscribers),
        'recipients': [s['email'] for s in subscribers]
    }
    await db.admin_messages.insert_one(message_doc)
    
    # Send emails if requested and resend is available
    emails_sent = 0
    if request.send_email and RESEND_AVAILABLE:
        for subscriber in subscribers:
            try:
                resend.Emails.send({
                    "from": "Edge Mode <notifications@edgemodeapp.com>",
                    "to": subscriber['email'],
                    "subject": request.subject,
                    "html": f"""
                    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                        <h2 style="color: #22c55e;">⚡ Edge Mode Update</h2>
                        <p>Hi {subscriber.get('username', 'there')},</p>
                        <div style="background: #f4f4f5; padding: 20px; border-radius: 8px; margin: 20px 0;">
                            {request.message.replace(chr(10), '<br>')}
                        </div>
                        <p style="color: #666;">Keep pushing forward!</p>
                        <p style="color: #666;">- The Edge Mode Team</p>
                    </div>
                    """
                })
                emails_sent += 1
            except Exception as e:
                logger.error(f"Failed to send email to {subscriber['email']}: {e}")
    
    return {
        'message': 'Message sent to subscribers',
        'sent_to': len(subscribers),
        'emails_sent': emails_sent if request.send_email else 'Email sending disabled',
        'email_available': RESEND_AVAILABLE
    }


@router.get("/messages/history")
async def get_message_history(admin_user: dict = Depends(require_admin)):
    """Get history of sent admin messages"""
    messages = await db.admin_messages.find(
        {},
        {'_id': 0}
    ).sort('sent_at', -1).limit(50).to_list(50)
    
    return {'messages': messages}



@router.post("/subscriptions/activate")
async def activate_subscription(
    request: SubscriptionActivateRequest,
    admin_user: dict = Depends(require_admin)
):
    """Manually activate a user's subscription (for failed webhooks, etc.)"""
    # Find user by email (case-insensitive)
    user = await db.users.find_one(
        {"email": {"$regex": f"^{request.email}$", "$options": "i"}},
        {"_id": 0, "id": 1, "email": 1, "username": 1, "subscription_active": 1}
    )
    
    if not user:
        raise HTTPException(status_code=404, detail=f"User not found with email: {request.email}")
    
    now = datetime.now(timezone.utc)
    subscription_end = now + timedelta(days=request.duration_days)
    
    result = await db.users.update_one(
        {"id": user["id"]},
        {"$set": {
            "subscription_active": True,
            "subscription_start_date": now.isoformat(),
            "subscription_end_date": subscription_end.isoformat(),
            "subscription_plan": request.plan,
            "subscription_activated_by": admin_user["id"],
            "subscription_activated_at": now.isoformat()
        }}
    )
    
    logger.info(f"Admin {admin_user.get('email')} activated subscription for {user.get('email')} until {subscription_end.isoformat()}")
    
    return {
        "message": "Subscription activated successfully",
        "user": {
            "email": user["email"],
            "username": user.get("username")
        },
        "subscription": {
            "plan": request.plan,
            "start_date": now.isoformat(),
            "end_date": subscription_end.isoformat(),
            "duration_days": request.duration_days
        }
    }


@router.post("/subscriptions/deactivate")
async def deactivate_subscription(
    email: str,
    admin_user: dict = Depends(require_admin)
):
    """Deactivate a user's subscription"""
    user = await db.users.find_one(
        {"email": {"$regex": f"^{email}$", "$options": "i"}},
        {"_id": 0, "id": 1, "email": 1}
    )
    
    if not user:
        raise HTTPException(status_code=404, detail=f"User not found with email: {email}")
    
    await db.users.update_one(
        {"id": user["id"]},
        {"$set": {
            "subscription_active": False,
            "subscription_deactivated_by": admin_user["id"],
            "subscription_deactivated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    return {"message": "Subscription deactivated", "email": user["email"]}


@router.get("/users/search")
async def search_users(
    q: str,
    admin_user: dict = Depends(require_admin)
):
    """Search users by email or username"""
    if len(q) < 2:
        raise HTTPException(status_code=400, detail="Search query must be at least 2 characters")
    
    users = await db.users.find(
        {
            "$or": [
                {"email": {"$regex": q, "$options": "i"}},
                {"username": {"$regex": q, "$options": "i"}}
            ]
        },
        {"_id": 0, "password_hash": 0}
    ).limit(20).to_list(20)
    
    return {"users": users, "count": len(users)}
