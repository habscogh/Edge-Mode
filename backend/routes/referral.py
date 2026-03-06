"""
Referral routes for Edge Mode
"""
from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timezone, timedelta
import asyncio
import secrets
import resend
import uuid

from config import db, logger, RESEND_API_KEY, SENDER_EMAIL
from models.schemas import EmailInvite
from utils.auth import get_current_user

router = APIRouter(prefix="/referral", tags=["Referral"])

# Referral rewards configuration
REFERRAL_REWARD_THRESHOLD = 3  # Number of referrals needed for reward
REFERRAL_REWARD_DAYS = 30  # Days of free subscription as reward


def get_invite_email_html(inviter_name: str, friend_name: str, referral_link: str) -> str:
    """Generate HTML for invite email"""
    greeting = f"Hey {friend_name}," if friend_name else "Hey there,"
    return f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background: #09090b; color: white;">
        <div style="text-align: center; padding: 20px 0;">
            <h1 style="color: #fff; margin: 0; font-size: 28px;">You're Invited! 🎯</h1>
        </div>
        <div style="padding: 20px; background: #18181b; border-radius: 8px; margin: 20px 0;">
            <p style="margin: 0; font-size: 16px;">{greeting}</p>
            <p style="margin: 15px 0;"><strong>{inviter_name}</strong> thinks you'd love Edge Mode - an app that helps teens become 1% better every day.</p>
            
            <div style="text-align: center; padding: 20px; background: #27272a; border-radius: 8px; margin: 20px 0;">
                <p style="margin: 0 0 15px 0; color: #a1a1aa;">What you'll get:</p>
                <p style="margin: 5px 0; color: #fff;">✓ Track daily progress across pillars</p>
                <p style="margin: 5px 0; color: #fff;">✓ Build streaks & earn badges</p>
                <p style="margin: 5px 0; color: #fff;">✓ Compete with friends on leaderboards</p>
                <p style="margin: 5px 0; color: #fff;">✓ 14-day free trial</p>
            </div>
            
            <div style="text-align: center; margin: 25px 0;">
                <a href="{referral_link}" style="display: inline-block; background: #22c55e; color: white; padding: 14px 28px; text-decoration: none; border-radius: 8px; font-weight: bold; font-size: 16px;">Join Edge Mode</a>
            </div>
        </div>
        <div style="text-align: center; padding: 20px;">
            <p style="color: #71717a; font-size: 12px;">Edge Mode - 1% Better Every Day</p>
        </div>
    </div>
    """


@router.get("/info")
async def get_referral_info(current_user: dict = Depends(get_current_user)):
    """Get user's referral code and stats"""
    user_id = current_user['id']
    
    referral_code = current_user.get('referral_code')
    if not referral_code:
        referral_code = f"{current_user.get('username', 'USER')[:4].upper()}{secrets.token_hex(3).upper()}"
        await db.users.update_one(
            {'id': user_id},
            {'$set': {'referral_code': referral_code}}
        )
    
    referral_count = await db.referrals.count_documents({'referrer_id': user_id})
    
    referrals = await db.referrals.find(
        {'referrer_id': user_id},
        {'_id': 0, 'referred_email': 1, 'created_at': 1}
    ).sort('created_at', -1).to_list(50)
    
    base_url = "https://edgemodeapp.com"
    referral_link = f"{base_url}/auth?ref={referral_code}"
    
    return {
        'referral_code': referral_code,
        'referral_link': referral_link,
        'total_referrals': referral_count,
        'referrals': referrals
    }


@router.post("/send-invite")
async def send_invite_email(invite_data: EmailInvite, current_user: dict = Depends(get_current_user)):
    """Send an invite email to a friend"""
    if not RESEND_API_KEY:
        raise HTTPException(status_code=500, detail='Email service not configured')
    
    referral_code = current_user.get('referral_code')
    if not referral_code:
        referral_code = f"{current_user.get('username', 'USER')[:4].upper()}{secrets.token_hex(3).upper()}"
        await db.users.update_one(
            {'id': current_user['id']},
            {'$set': {'referral_code': referral_code}}
        )
    
    existing = await db.users.find_one({'email': invite_data.friend_email}, {'_id': 0, 'id': 1})
    if existing:
        return {'message': 'This person is already on Edge Mode!', 'already_member': True}
    
    recent_invite = await db.sent_invites.find_one({
        'inviter_id': current_user['id'],
        'invited_email': invite_data.friend_email,
        'sent_at': {'$gte': (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()}
    })
    
    if recent_invite:
        return {'message': 'You already invited this person recently', 'already_invited': True}
    
    base_url = "https://edgemodeapp.com"
    referral_link = f"{base_url}/auth?ref={referral_code}"
    
    html = get_invite_email_html(
        current_user.get('username', 'A friend'),
        invite_data.friend_name,
        referral_link
    )
    
    try:
        await asyncio.to_thread(resend.Emails.send, {
            "from": SENDER_EMAIL,
            "to": [invite_data.friend_email],
            "subject": f"{current_user.get('username', 'A friend')} invited you to Edge Mode! 🎯",
            "html": html
        })
        
        await db.sent_invites.insert_one({
            'id': str(uuid.uuid4()),
            'inviter_id': current_user['id'],
            'invited_email': invite_data.friend_email,
            'invited_name': invite_data.friend_name,
            'sent_at': datetime.now(timezone.utc).isoformat()
        })
        
        return {'message': 'Invite sent!', 'success': True}
    except Exception as e:
        logger.error(f"Failed to send invite email: {e}")
        raise HTTPException(status_code=500, detail='Failed to send invite email')


# Need to import uuid for the route
import uuid
