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
    """Search users by email, username, name, or school"""
    if len(q) < 2:
        raise HTTPException(status_code=400, detail="Search query must be at least 2 characters")
    
    users = await db.users.find(
        {
            "$or": [
                {"email": {"$regex": q, "$options": "i"}},
                {"username": {"$regex": q, "$options": "i"}},
                {"name": {"$regex": q, "$options": "i"}},
                {"school_name": {"$regex": q, "$options": "i"}},
                {"school_base_name": {"$regex": q, "$options": "i"}}
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



@router.post("/fix-premium-status/{user_email}")
async def fix_premium_status(user_email: str, admin_user: dict = Depends(require_admin)):
    """Fix a user's premium status - set is_trial=False for paid subscribers"""
    user = await db.users.find_one({'email': user_email.lower()}, {'_id': 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update to premium status
    await db.users.update_one(
        {'email': user_email.lower()},
        {'$set': {
            'is_trial': False,
            'subscription_active': True,
            'trial_ends_at': None,
            'is_admin': True if user_email.lower() == 'admin@edgemodeapp.com' else user.get('is_admin', False)
        }}
    )
    
    logger.info(f"Fixed premium status for {user_email}")
    
    return {
        "message": f"Premium status fixed for {user_email}",
        "is_trial": False,
        "subscription_active": True
    }


@router.post("/users/extend-access")
async def extend_user_access(
    email: str,
    days: int,
    admin_user: dict = Depends(require_admin)
):
    """Extend a user's access period by a specified number of days"""
    user = await db.users.find_one({'email': email.lower()}, {'_id': 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    now = datetime.now(timezone.utc)
    
    # Calculate new end date
    # If they have an existing trial_ends_at, extend from that date
    # Otherwise extend from now
    if user.get('trial_ends_at'):
        try:
            current_end = datetime.fromisoformat(user['trial_ends_at'].replace('Z', '+00:00'))
            # If trial already expired, extend from now
            if current_end < now:
                new_end = now + timedelta(days=days)
            else:
                new_end = current_end + timedelta(days=days)
        except:
            new_end = now + timedelta(days=days)
    else:
        new_end = now + timedelta(days=days)
    
    # Update user
    await db.users.update_one(
        {'email': email.lower()},
        {'$set': {
            'trial_ends_at': new_end.isoformat(),
            'subscription_active': True,
            'is_trial': True,
            'has_extended_trial': True
        }}
    )
    
    logger.info(f"Admin {admin_user.get('email')} extended access for {email} by {days} days until {new_end}")
    
    return {
        "message": f"Access extended for {email}",
        "new_end_date": new_end.isoformat(),
        "days_added": days
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


# ============ Groups Management ============

@router.get("/groups")
async def get_all_groups(admin_user: dict = Depends(require_admin)):
    """Get all groups with their members"""
    groups = await db.groups.find({}, {'_id': 0}).sort('created_at', -1).to_list(200)
    
    result = []
    for group in groups:
        # Get member details
        member_ids = group.get('members', [])
        members = []
        
        for member_id in member_ids:
            user = await db.users.find_one(
                {'id': member_id}, 
                {'_id': 0, 'id': 1, 'username': 1, 'name': 1, 'email': 1, 'is_coach': 1, 'join_date': 1, 'current_streak': 1}
            )
            if user:
                members.append({
                    'id': user['id'],
                    'name': user.get('username') or user.get('name', 'Unknown'),
                    'email': user.get('email'),
                    'is_coach': user.get('is_coach', False),
                    'join_date': user.get('join_date'),
                    'current_streak': user.get('current_streak', 0)
                })
        
        # Get coach info if it's a team
        coach_name = None
        if group.get('coach_id'):
            coach = await db.users.find_one({'id': group['coach_id']}, {'_id': 0, 'name': 1, 'username': 1})
            if coach:
                coach_name = coach.get('name') or coach.get('username')
        
        result.append({
            'id': group['id'],
            'name': group.get('name', 'Unnamed Group'),
            'type': group.get('type', 'private'),
            'invite_code': group.get('invite_code'),
            'coach_id': group.get('coach_id'),
            'coach_name': coach_name,
            'member_count': len(members),
            'members': members,
            'created_at': group.get('created_at'),
            'has_extended_trial': group.get('has_extended_trial', False)
        })
    
    return {'groups': result, 'total': len(result)}


@router.delete("/groups/{group_id}")
async def delete_group(group_id: str, admin_user: dict = Depends(require_admin)):
    """Delete a group and optionally clean up member references"""
    # Find the group
    group = await db.groups.find_one({'id': group_id}, {'_id': 0})
    if not group:
        raise HTTPException(status_code=404, detail='Group not found')
    
    # Remove team_id reference from all members
    member_ids = group.get('members', [])
    if member_ids:
        await db.users.update_many(
            {'id': {'$in': member_ids}},
            {'$unset': {'team_id': '', 'joined_via_coach': ''}}
        )
    
    # Delete the group
    result = await db.groups.delete_one({'id': group_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=500, detail='Failed to delete group')
    
    logger.info(f"Admin {admin_user.get('email')} deleted group: {group.get('name')} ({group_id})")
    
    return {
        'message': f'Group "{group.get("name")}" deleted successfully',
        'members_updated': len(member_ids)
    }


@router.put("/groups/{group_id}/name")
async def update_group_name(group_id: str, new_name: str, admin_user: dict = Depends(require_admin)):
    """Update a group's name"""
    if not new_name or not new_name.strip():
        raise HTTPException(status_code=400, detail='Group name cannot be empty')
    
    # Find the group
    group = await db.groups.find_one({'id': group_id}, {'_id': 0})
    if not group:
        raise HTTPException(status_code=404, detail='Group not found')
    
    old_name = group.get('name', 'Unknown')
    
    # Update the name
    result = await db.groups.update_one(
        {'id': group_id},
        {'$set': {'name': new_name.strip()}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=500, detail='Failed to update group name')
    
    logger.info(f"Admin {admin_user.get('email')} renamed group: '{old_name}' -> '{new_name.strip()}' ({group_id})")
    
    return {
        'message': f'Group renamed to "{new_name.strip()}"',
        'old_name': old_name,
        'new_name': new_name.strip()
    }


@router.delete("/groups/{group_id}/members/{member_id}")
async def remove_member_from_group(group_id: str, member_id: str, admin_user: dict = Depends(require_admin)):
    """Remove a single member from a group"""
    # Find the group
    group = await db.groups.find_one({'id': group_id}, {'_id': 0})
    if not group:
        raise HTTPException(status_code=404, detail='Group not found')
    
    # Check if member is in the group
    if member_id not in group.get('members', []):
        raise HTTPException(status_code=404, detail='Member not in this group')
    
    # Don't allow removing the coach from their own team
    if group.get('coach_id') == member_id:
        raise HTTPException(status_code=400, detail='Cannot remove the coach from their own team. Delete the group instead.')
    
    # Get member info for logging
    member = await db.users.find_one({'id': member_id}, {'_id': 0, 'username': 1, 'name': 1, 'email': 1})
    member_name = member.get('username') or member.get('name') or member.get('email', 'Unknown') if member else 'Unknown'
    
    # Remove member from group
    await db.groups.update_one(
        {'id': group_id},
        {'$pull': {'members': member_id}}
    )
    
    # Remove team_id reference from the user
    await db.users.update_one(
        {'id': member_id},
        {'$unset': {'team_id': '', 'joined_via_coach': ''}}
    )
    
    logger.info(f"Admin {admin_user.get('email')} removed {member_name} from group {group.get('name')} ({group_id})")
    
    return {
        'message': f'{member_name} removed from group',
        'member_id': member_id,
        'group_name': group.get('name')
    }


# ============ Site Settings ============

@router.get("/settings")
async def get_site_settings(admin_user: dict = Depends(require_admin)):
    """Get all site settings"""
    settings = await db.site_settings.find_one({'id': 'main'}, {'_id': 0})
    if not settings:
        # Default settings
        settings = {
            'id': 'main',
            'social_proof_enabled': True,
            'testimonials': []
        }
        await db.site_settings.insert_one(settings)
    return settings


@router.put("/settings")
async def update_site_settings(
    social_proof_enabled: bool = None,
    admin_user: dict = Depends(require_admin)
):
    """Update site settings"""
    update_data = {}
    if social_proof_enabled is not None:
        update_data['social_proof_enabled'] = social_proof_enabled
    
    if update_data:
        await db.site_settings.update_one(
            {'id': 'main'},
            {'$set': update_data},
            upsert=True
        )
    
    settings = await db.site_settings.find_one({'id': 'main'}, {'_id': 0})
    return settings


@router.post("/testimonials")
async def add_testimonial(
    name: str,
    role: str,
    quote: str,
    avatar_url: str = "",
    admin_user: dict = Depends(require_admin)
):
    """Add a testimonial"""
    testimonial = {
        'id': str(uuid.uuid4()),
        'name': name,
        'role': role,
        'quote': quote,
        'avatar_url': avatar_url,
        'created_at': datetime.now(timezone.utc).isoformat()
    }
    
    await db.site_settings.update_one(
        {'id': 'main'},
        {'$push': {'testimonials': testimonial}},
        upsert=True
    )
    
    return {'message': 'Testimonial added', 'testimonial': testimonial}


@router.delete("/testimonials/{testimonial_id}")
async def delete_testimonial(testimonial_id: str, admin_user: dict = Depends(require_admin)):
    """Delete a testimonial"""
    await db.site_settings.update_one(
        {'id': 'main'},
        {'$pull': {'testimonials': {'id': testimonial_id}}}
    )
    return {'message': 'Testimonial deleted'}


# ============ Public Endpoints (No Auth) ============

public_router = APIRouter(tags=["Public"])


@public_router.get("/platform-stats")
async def get_platform_stats():
    """
    Public endpoint for landing page - returns platform statistics
    No authentication required
    """
    # Get settings to check if social proof is enabled
    settings = await db.site_settings.find_one({'id': 'main'}, {'_id': 0})
    if not settings:
        settings = {'social_proof_enabled': True, 'testimonials': []}
    
    if not settings.get('social_proof_enabled', True):
        return {
            'enabled': False,
            'stats': {},
            'testimonials': []
        }
    
    # Gather stats
    total_users = await db.users.count_documents({})
    total_sessions = await db.daily_sessions.count_documents({})
    total_badges = await db.user_badges.count_documents({})
    
    # Calculate total minutes logged
    pipeline = [
        {"$group": {"_id": None, "total_minutes": {"$sum": "$minutes_spent"}}}
    ]
    result = await db.daily_sessions.aggregate(pipeline).to_list(1)
    total_minutes = result[0]['total_minutes'] if result else 0
    
    # Format for display
    hours_logged = total_minutes // 60
    
    return {
        'enabled': True,
        'stats': {
            'total_users': total_users,
            'sessions_logged': total_sessions,
            'badges_earned': total_badges,
            'hours_logged': hours_logged
        },
        'testimonials': settings.get('testimonials', [])
    }



@router.get("/debug/sessions")
async def debug_sessions(admin_user: dict = Depends(require_admin)):
    """Debug endpoint to check session data - useful for diagnosing weekly summary issues"""
    from utils.timezone import get_today_eastern
    
    today_eastern = get_today_eastern()
    week_start = (today_eastern - timedelta(days=7)).isoformat()
    
    # Get session stats
    total_sessions = await db.daily_sessions.count_documents({})
    recent_sessions = await db.daily_sessions.count_documents({'date': {'$gte': week_start}})
    
    # Get most recent 10 sessions
    latest = await db.daily_sessions.find({}, {'_id': 0, 'user_id': 1, 'date': 1, 'pillar': 1}).sort('date', -1).to_list(10)
    
    # Get unique dates in last 7 days
    recent_dates = await db.daily_sessions.distinct('date', {'date': {'$gte': week_start}})
    
    # Get users with sessions this week
    users_with_sessions = await db.daily_sessions.distinct('user_id', {'date': {'$gte': week_start}})
    
    return {
        'debug_info': {
            'today_eastern': today_eastern.isoformat(),
            'week_start': week_start,
            'total_sessions_in_db': total_sessions,
            'sessions_in_last_7_days': recent_sessions,
            'unique_users_with_sessions_this_week': len(users_with_sessions),
            'dates_with_activity_this_week': sorted(recent_dates)
        },
        'latest_10_sessions': latest
    }
