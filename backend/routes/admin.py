"""
Admin routes for Edge Mode
"""
from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel
from typing import Optional, List
import os
import uuid

from config import db, logger, STRIPE_API_KEY
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


@router.get("/stripe-debug")
async def get_stripe_debug(admin_user: dict = Depends(require_admin)):
    """Debug endpoint to check which Stripe key is being used - ADMIN ONLY"""
    stripe_secret_key = os.environ.get('STRIPE_SECRET_KEY', 'NOT_SET')
    stripe_api_key = os.environ.get('STRIPE_API_KEY', 'NOT_SET')
    
    def mask_key(key):
        if key == 'NOT_SET':
            return key
        return f"{key[:12]}...{key[-4:]}" if len(key) > 16 else "INVALID_KEY"
    
    is_live_mode = STRIPE_API_KEY.startswith('sk_live_') if STRIPE_API_KEY else False
    
    return {
        "stripe_secret_key_env": mask_key(stripe_secret_key),
        "stripe_api_key_env": mask_key(stripe_api_key),
        "active_key_being_used": mask_key(STRIPE_API_KEY),
        "is_live_mode": is_live_mode,
        "key_type": "LIVE" if is_live_mode else "TEST",
        "message": "✅ Ready for live payments" if is_live_mode else "⚠️ STILL IN TEST MODE - Check Customer Keys"
    }


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
            "is_trial": False,  # Important: mark as no longer trial
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



@router.delete("/users/{email}")
async def delete_user(
    email: str,
    admin_user: dict = Depends(require_admin)
):
    """Delete a user and all their related data"""
    # Find user by email (case-insensitive)
    user = await db.users.find_one(
        {"email": {"$regex": f"^{email}$", "$options": "i"}},
        {"_id": 0, "id": 1, "email": 1, "username": 1}
    )
    
    if not user:
        raise HTTPException(status_code=404, detail=f"User not found with email: {email}")
    
    user_id = user["id"]
    
    # Delete all related data
    deleted_counts = {}
    
    # Delete sessions
    result = await db.daily_sessions.delete_many({"user_id": user_id})
    deleted_counts["sessions"] = result.deleted_count
    
    # Delete reflections
    result = await db.reflections.delete_many({"user_id": user_id})
    deleted_counts["reflections"] = result.deleted_count
    
    # Delete pillars
    result = await db.user_pillars.delete_many({"user_id": user_id})
    deleted_counts["pillars"] = result.deleted_count
    
    # Delete badges
    result = await db.user_badges.delete_many({"user_id": user_id})
    deleted_counts["badges"] = result.deleted_count
    
    # Delete group memberships
    result = await db.group_members.delete_many({"user_id": user_id})
    deleted_counts["group_memberships"] = result.deleted_count
    
    # Delete payment transactions
    result = await db.payment_transactions.delete_many({"user_id": user_id})
    deleted_counts["payment_transactions"] = result.deleted_count
    
    # Delete notifications
    result = await db.notifications.delete_many({"user_id": user_id})
    deleted_counts["notifications"] = result.deleted_count
    
    # Finally delete the user
    result = await db.users.delete_one({"id": user_id})
    deleted_counts["user"] = result.deleted_count
    
    logger.info(f"Admin {admin_user.get('email')} deleted user {user.get('email')} ({user.get('username')})")
    
    return {
        "message": "User deleted successfully",
        "deleted_user": {
            "email": user["email"],
            "username": user.get("username")
        },
        "deleted_counts": deleted_counts
    }



@router.post("/users/expire-trial")
async def expire_user_trial(
    email: str,
    admin_user: dict = Depends(require_admin)
):
    """Set a user's trial to expired (for testing payment flow)"""
    user = await db.users.find_one(
        {"email": {"$regex": f"^{email}$", "$options": "i"}},
        {"_id": 0, "id": 1, "email": 1, "username": 1}
    )
    
    if not user:
        raise HTTPException(status_code=404, detail=f"User not found: {email}")
    
    # Set trial to expired (yesterday)
    expired_date = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    
    await db.users.update_one(
        {"id": user["id"]},
        {"$set": {
            "trial_ends_at": expired_date,
            "subscription_active": False,
            "is_trial": True
        }}
    )
    
    logger.info(f"Admin {admin_user.get('email')} expired trial for {user.get('email')}")
    
    return {
        "message": f"Trial expired for {user['email']}",
        "user": user["username"],
        "trial_ends_at": expired_date
    }



@router.post("/challenges/cleanup-duplicates")
async def cleanup_duplicate_challenges(admin_user: dict = Depends(require_admin)):
    """Remove duplicate challenges, keeping only one of each type per period"""
    
    # Get all challenges grouped by name and start_date
    pipeline = [
        {
            "$group": {
                "_id": {"name": "$name", "start_date": "$start_date"},
                "ids": {"$push": "$id"},
                "count": {"$sum": 1}
            }
        },
        {
            "$match": {"count": {"$gt": 1}}
        }
    ]
    
    duplicates = await db.challenges.aggregate(pipeline).to_list(100)
    
    deleted_count = 0
    for dup in duplicates:
        # Keep the first one, delete the rest
        ids_to_delete = dup["ids"][1:]  # Skip first ID
        for challenge_id in ids_to_delete:
            # Delete participants for this challenge
            await db.challenge_participants.delete_many({"challenge_id": challenge_id})
            # Delete the challenge
            await db.challenges.delete_one({"id": challenge_id})
            deleted_count += 1
    
    logger.info(f"Admin {admin_user.get('email')} cleaned up {deleted_count} duplicate challenges")
    
    return {
        "message": f"Removed {deleted_count} duplicate challenges",
        "duplicates_found": len(duplicates)
    }


# ============ Coach Code Management ============

@router.get("/coach-codes")
async def get_coach_codes(admin_user: dict = Depends(require_admin)):
    """Get all coach codes"""
    codes = await db.coach_codes.find({}, {'_id': 0}).sort('created_at', -1).to_list(100)
    
    # Also get usage stats for each code
    for code in codes:
        usage_count = await db.users.count_documents({
            'special_code': code['code'],
            'is_coach': True
        })
        code['usage_count'] = usage_count
    
    return {'codes': codes}


@router.post("/coach-codes")
async def create_coach_code(
    code: str,
    description: str = "",
    max_uses: int = 0,
    extended_trial_days: int = 30,
    admin_user: dict = Depends(require_admin)
):
    """Create a new coach code"""
    code = code.upper().strip()
    
    # Check if code already exists
    existing = await db.coach_codes.find_one({'code': code})
    if existing:
        raise HTTPException(status_code=400, detail='Code already exists')
    
    code_doc = {
        'id': str(uuid.uuid4()),
        'code': code,
        'description': description,
        'max_uses': max_uses,  # 0 = unlimited
        'extended_trial_days': extended_trial_days,
        'is_active': True,
        'created_at': datetime.now(timezone.utc).isoformat(),
        'created_by': admin_user.get('email')
    }
    
    await db.coach_codes.insert_one(code_doc)
    logger.info(f"Admin created coach code: {code}")
    
    return {'message': f'Coach code {code} created', 'code': {k: v for k, v in code_doc.items() if k != '_id'}}


@router.put("/coach-codes/{code_id}")
async def update_coach_code(
    code_id: str,
    is_active: bool = None,
    description: str = None,
    max_uses: int = None,
    admin_user: dict = Depends(require_admin)
):
    """Update a coach code"""
    code = await db.coach_codes.find_one({'id': code_id})
    if not code:
        raise HTTPException(status_code=404, detail='Code not found')
    
    update_data = {}
    if is_active is not None:
        update_data['is_active'] = is_active
    if description is not None:
        update_data['description'] = description
    if max_uses is not None:
        update_data['max_uses'] = max_uses
    
    if update_data:
        update_data['updated_at'] = datetime.now(timezone.utc).isoformat()
        await db.coach_codes.update_one({'id': code_id}, {'$set': update_data})
    
    updated = await db.coach_codes.find_one({'id': code_id}, {'_id': 0})
    return {'message': 'Code updated', 'code': updated}


@router.delete("/coach-codes/{code_id}")
async def delete_coach_code(code_id: str, admin_user: dict = Depends(require_admin)):
    """Delete a coach code"""
    code = await db.coach_codes.find_one({'id': code_id})
    if not code:
        raise HTTPException(status_code=404, detail='Code not found')
    
    await db.coach_codes.delete_one({'id': code_id})
    logger.info(f"Admin deleted coach code: {code['code']}")
    
    return {'message': f"Code {code['code']} deleted"}


@router.get("/coaches")
async def get_all_coaches(admin_user: dict = Depends(require_admin)):
    """Get all coaches with their team info"""
    coaches = await db.users.find(
        {'is_coach': True},
        {'_id': 0, 'password': 0}
    ).sort('join_date', -1).to_list(100)
    
    for coach in coaches:
        if coach.get('team_id'):
            team = await db.groups.find_one({'id': coach['team_id']}, {'_id': 0})
            if team:
                coach['team_name'] = team.get('name')
                coach['team_member_count'] = len(team.get('members', [])) - 1  # Exclude coach
                coach['team_invite_code'] = team.get('invite_code')
    
    return {'coaches': coaches}
