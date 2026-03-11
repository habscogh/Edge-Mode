"""
Push notification routes for Edge Mode
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
import uuid
import json
import asyncio
from pywebpush import webpush, WebPushException

from config import db, logger
from utils.auth import get_current_user
import os

router = APIRouter(prefix="/push", tags=["Push Notifications"])

# VAPID Configuration
VAPID_PUBLIC_KEY = os.environ.get('VAPID_PUBLIC_KEY')
VAPID_PRIVATE_KEY = os.environ.get('VAPID_PRIVATE_KEY')
VAPID_CLAIMS_EMAIL = os.environ.get('VAPID_CLAIMS_EMAIL', 'admin@edgemodeapp.com')


class PushSubscription(BaseModel):
    endpoint: str
    keys: dict  # Contains p256dh and auth keys


class PushMessage(BaseModel):
    title: str
    body: str
    icon: Optional[str] = "/logo192.png"
    badge: Optional[str] = "/badge.png"
    url: Optional[str] = "/"
    tag: Optional[str] = None


# ============ Helper Functions ============

async def send_push_notification(subscription_info: dict, message: PushMessage) -> bool:
    """Send a push notification to a single subscription"""
    if not VAPID_PRIVATE_KEY or not VAPID_PUBLIC_KEY:
        logger.warning("VAPID keys not configured, skipping push notification")
        return False
    
    try:
        payload = json.dumps({
            "title": message.title,
            "body": message.body,
            "icon": message.icon,
            "badge": message.badge,
            "url": message.url,
            "tag": message.tag,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        await asyncio.to_thread(
            webpush,
            subscription_info=subscription_info,
            data=payload,
            vapid_private_key=VAPID_PRIVATE_KEY,
            vapid_claims={"sub": f"mailto:{VAPID_CLAIMS_EMAIL}"}
        )
        return True
    except WebPushException as e:
        logger.error(f"Push notification failed: {e}")
        # If subscription is invalid/expired, mark for cleanup
        if e.response and e.response.status_code in [404, 410]:
            return False
        return False
    except Exception as e:
        logger.error(f"Unexpected push error: {e}")
        return False


async def send_push_to_user(user_id: str, message: PushMessage) -> int:
    """Send push notification to all devices of a user"""
    subscriptions = await db.push_subscriptions.find(
        {'user_id': user_id},
        {'_id': 0}
    ).to_list(10)
    
    sent_count = 0
    failed_ids = []
    
    for sub in subscriptions:
        subscription_info = {
            'endpoint': sub['endpoint'],
            'keys': sub['keys']
        }
        success = await send_push_notification(subscription_info, message)
        if success:
            sent_count += 1
        else:
            failed_ids.append(sub['id'])
    
    # Clean up failed/expired subscriptions
    if failed_ids:
        await db.push_subscriptions.delete_many({'id': {'$in': failed_ids}})
        logger.info(f"Cleaned up {len(failed_ids)} expired push subscriptions for user {user_id}")
    
    return sent_count


async def send_push_to_users(user_ids: List[str], message: PushMessage) -> int:
    """Send push notification to multiple users"""
    total_sent = 0
    for user_id in user_ids:
        sent = await send_push_to_user(user_id, message)
        total_sent += sent
    return total_sent


# ============ Routes ============

@router.get("/vapid-key")
async def get_vapid_public_key():
    """Get the VAPID public key for push subscription"""
    if not VAPID_PUBLIC_KEY:
        raise HTTPException(status_code=503, detail="Push notifications not configured")
    return {"publicKey": VAPID_PUBLIC_KEY}


@router.post("/subscribe")
async def subscribe_push(subscription: PushSubscription, current_user: dict = Depends(get_current_user)):
    """Subscribe to push notifications"""
    user_id = current_user['id']
    
    # Check if this endpoint is already registered
    existing = await db.push_subscriptions.find_one({
        'user_id': user_id,
        'endpoint': subscription.endpoint
    })
    
    if existing:
        # Update the keys in case they changed
        await db.push_subscriptions.update_one(
            {'id': existing['id']},
            {'$set': {
                'keys': subscription.keys,
                'updated_at': datetime.now(timezone.utc).isoformat()
            }}
        )
        return {'message': 'Subscription updated', 'subscription_id': existing['id']}
    
    # Create new subscription
    sub_doc = {
        'id': str(uuid.uuid4()),
        'user_id': user_id,
        'endpoint': subscription.endpoint,
        'keys': subscription.keys,
        'created_at': datetime.now(timezone.utc).isoformat(),
        'updated_at': datetime.now(timezone.utc).isoformat()
    }
    await db.push_subscriptions.insert_one(sub_doc)
    
    # Update user's push notification preference
    await db.users.update_one(
        {'id': user_id},
        {'$set': {'push_enabled': True}}
    )
    
    # Send a welcome push notification (don't clean up on failure for new subscriptions)
    try:
        subscription_info = {
            'endpoint': subscription.endpoint,
            'keys': subscription.keys
        }
        await send_push_notification(subscription_info, PushMessage(
            title="🎉 Push Notifications Enabled!",
            body="You'll now receive updates about streaks, badges, and challenges.",
            url="/dashboard",
            tag="welcome"
        ))
    except Exception as e:
        logger.error(f"Failed to send welcome push: {e}")
        # Don't clean up - this is expected to fail for invalid test endpoints
    
    return {'message': 'Subscribed successfully', 'subscription_id': sub_doc['id']}


@router.delete("/unsubscribe")
async def unsubscribe_push(current_user: dict = Depends(get_current_user)):
    """Unsubscribe from push notifications (removes all subscriptions for user)"""
    user_id = current_user['id']
    
    result = await db.push_subscriptions.delete_many({'user_id': user_id})
    
    await db.users.update_one(
        {'id': user_id},
        {'$set': {'push_enabled': False}}
    )
    
    return {'message': 'Unsubscribed from push notifications', 'removed': result.deleted_count}


@router.get("/status")
async def get_push_status(current_user: dict = Depends(get_current_user)):
    """Get user's push notification status"""
    user_id = current_user['id']
    
    subscription_count = await db.push_subscriptions.count_documents({'user_id': user_id})
    user = await db.users.find_one({'id': user_id}, {'_id': 0, 'push_enabled': 1})
    
    return {
        'push_enabled': user.get('push_enabled', False),
        'subscribed_devices': subscription_count,
        'vapid_configured': bool(VAPID_PUBLIC_KEY)
    }


@router.post("/test")
async def send_test_push(current_user: dict = Depends(get_current_user)):
    """Send a test push notification to the current user"""
    sent = await send_push_to_user(
        current_user['id'],
        PushMessage(
            title="🔔 Test Notification",
            body="Push notifications are working! You're all set.",
            url="/dashboard",
            tag="test"
        )
    )
    
    if sent > 0:
        return {'message': f'Test notification sent to {sent} device(s)'}
    else:
        raise HTTPException(status_code=404, detail="No active push subscriptions found")


# ============ Notification Types for Scheduler ============

async def send_streak_reminder_push(user_id: str, username: str, streak: int):
    """Send push notification for streak reminder"""
    await send_push_to_user(user_id, PushMessage(
        title="🔥 Don't Break Your Streak!",
        body=f"You're on a {streak}-day streak, {username}! Log a session today.",
        url="/dashboard",
        tag="streak-reminder"
    ))


async def send_badge_earned_push(user_id: str, badge_name: str, badge_icon: str):
    """Send push notification when user earns a badge"""
    await send_push_to_user(user_id, PushMessage(
        title=f"{badge_icon} New Badge Earned!",
        body=f"Congratulations! You earned the '{badge_name}' badge!",
        url="/achievements",
        tag=f"badge-{badge_name.lower().replace(' ', '-')}"
    ))


async def send_challenge_update_push(user_id: str, challenge_name: str, rank: int):
    """Send push notification for challenge rank update"""
    if rank <= 3:
        await send_push_to_user(user_id, PushMessage(
            title="🏆 You're on the Podium!",
            body=f"You're ranked #{rank} in '{challenge_name}'! Keep it up!",
            url="/challenges",
            tag=f"challenge-{challenge_name.lower().replace(' ', '-')}"
        ))


async def send_trial_ending_push(user_id: str, days_left: int):
    """Send push notification for trial ending"""
    await send_push_to_user(user_id, PushMessage(
        title="⏰ Trial Ending Soon!",
        body=f"Your free trial ends in {days_left} day{'s' if days_left > 1 else ''}. Subscribe to keep your progress!",
        url="/profile",
        tag="trial-ending"
    ))


async def send_inactivity_push(user_id: str, days_inactive: int):
    """Send push notification for inactivity"""
    await send_push_to_user(user_id, PushMessage(
        title="👋 We Miss You!",
        body=f"It's been {days_inactive} days since your last session. Small steps lead to big changes!",
        url="/dashboard",
        tag="inactivity"
    ))



async def send_badge_earned_push(user_id: str, badge_name: str, badge_icon: str, badge_description: str):
    """Send push notification when user earns a badge"""
    await send_push_to_user(user_id, PushMessage(
        title=f"{badge_icon} Badge Earned: {badge_name}!",
        body=badge_description,
        url="/achievements",
        tag=f"badge-{badge_name.lower().replace(' ', '-')}"
    ))


async def send_challenge_winner_push(user_id: str, place: int, challenge_name: str):
    """Send push notification to challenge winners"""
    medals = {1: "🥇", 2: "🥈", 3: "🥉"}
    places = {1: "1st", 2: "2nd", 3: "3rd"}
    
    medal = medals.get(place, "🏆")
    place_text = places.get(place, f"{place}th")
    
    await send_push_to_user(user_id, PushMessage(
        title=f"{medal} Congratulations! You placed {place_text}!",
        body=f"You finished {place_text} in {challenge_name}. Check your new badge!",
        url="/achievements",
        tag=f"challenge-winner-{challenge_name.lower().replace(' ', '-')}"
    ))
