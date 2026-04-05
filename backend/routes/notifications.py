"""
Notification and email routes for Edge Mode
"""
from fastapi import APIRouter, Depends
from datetime import datetime, timezone, timedelta
import asyncio
import resend

from config import db, logger, RESEND_API_KEY, SENDER_EMAIL
from models.schemas import EmailSettings, NotificationSettingsUpdate
from utils.auth import get_current_user

router = APIRouter(prefix="/notifications", tags=["Notifications"])


# ============ Email Helper Functions ============

async def send_email_async(to_email: str, subject: str, html_content: str):
    """Send email using Resend API (non-blocking)"""
    if not RESEND_API_KEY:
        logger.warning("RESEND_API_KEY not configured, skipping email")
        return None
    
    params = {
        "from": SENDER_EMAIL,
        "to": [to_email],
        "subject": subject,
        "html": html_content
    }
    
    try:
        result = await asyncio.to_thread(resend.Emails.send, params)
        logger.info(f"Email sent to {to_email}: {result}")
        return result
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        return None


def get_streak_reminder_html(username: str, streak: int) -> str:
    return f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background: #09090b; color: white;">
        <div style="text-align: center; padding: 20px 0;">
            <h1 style="color: #fff; margin: 0; font-size: 24px;">🔥 Don't Break Your Streak!</h1>
        </div>
        <div style="padding: 20px; background: #18181b; border-radius: 8px; margin: 20px 0;">
            <p style="margin: 0; font-size: 16px;">Hey <strong>{username}</strong>,</p>
            <p style="margin: 15px 0;">You're on a <strong style="color: #f97316; font-size: 20px;">{streak}-day streak</strong>! Keep the momentum going.</p>
            <p style="margin: 15px 0;">Log a session today to continue your progress.</p>
        </div>
        <div style="text-align: center; padding: 20px;">
            <p style="color: #71717a; font-size: 12px;">Edge Mode - 1% Better Every Day</p>
        </div>
    </div>
    """


def get_weekly_summary_html(username: str, stats: dict) -> str:
    return f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background: #09090b; color: white;">
        <div style="text-align: center; padding: 20px 0;">
            <h1 style="color: #fff; margin: 0; font-size: 24px;">📊 Your Weekly Summary</h1>
        </div>
        <div style="padding: 20px; background: #18181b; border-radius: 8px; margin: 20px 0;">
            <p style="margin: 0; font-size: 16px;">Hey <strong>{username}</strong>,</p>
            <p style="margin: 15px 0;">Here's how you did this week:</p>
            <div style="display: flex; justify-content: space-around; padding: 15px 0;">
                <div style="text-align: center;">
                    <div style="font-size: 28px; font-weight: bold; color: #f97316;">{stats.get('total_sessions', 0)}</div>
                    <div style="color: #71717a; font-size: 12px;">Sessions</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 28px; font-weight: bold; color: #22c55e;">{stats.get('total_minutes', 0)}</div>
                    <div style="color: #71717a; font-size: 12px;">Minutes</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 28px; font-weight: bold; color: #3b82f6;">{stats.get('consistency_pct', 0):.0f}%</div>
                    <div style="color: #71717a; font-size: 12px;">Consistency</div>
                </div>
            </div>
        </div>
        <div style="text-align: center; padding: 20px;">
            <p style="color: #71717a; font-size: 12px;">Edge Mode - 1% Better Every Day</p>
        </div>
    </div>
    """


def get_inactive_reminder_html(username: str, days_inactive: int) -> str:
    return f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background: #09090b; color: white;">
        <div style="text-align: center; padding: 20px 0;">
            <h1 style="color: #fff; margin: 0; font-size: 24px;">👋 We Miss You!</h1>
        </div>
        <div style="padding: 20px; background: #18181b; border-radius: 8px; margin: 20px 0;">
            <p style="margin: 0; font-size: 16px;">Hey <strong>{username}</strong>,</p>
            <p style="margin: 15px 0;">It's been <strong style="color: #f97316;">{days_inactive} days</strong> since your last session.</p>
            <p style="margin: 15px 0;">Remember: <em>Small steps lead to big changes.</em> Even 15 minutes today counts!</p>
            <p style="margin: 15px 0;">Your future self will thank you. 💪</p>
        </div>
        <div style="text-align: center; padding: 20px;">
            <p style="color: #71717a; font-size: 12px;">Edge Mode - 1% Better Every Day</p>
        </div>
    </div>
    """


def get_trial_ending_html(username: str, days_left: int, streak: int, consistency_pct: float) -> str:
    """Generate HTML for trial ending reminder email"""
    days_text = "tomorrow" if days_left == 1 else f"in {days_left} days"
    
    streak_section = ""
    if streak > 0:
        streak_section = f"""
            <div style="text-align: center; padding: 15px; background: #27272a; border-radius: 8px; margin: 10px 0;">
                <div style="font-size: 32px; font-weight: bold; color: #f97316;">🔥 {streak}</div>
                <div style="color: #71717a; font-size: 12px;">Day Streak</div>
            </div>
        """
    
    consistency_section = ""
    if consistency_pct > 0:
        consistency_section = f"""
            <div style="text-align: center; padding: 15px; background: #27272a; border-radius: 8px; margin: 10px 0;">
                <div style="font-size: 32px; font-weight: bold; color: #22c55e;">📈 {consistency_pct:.0f}%</div>
                <div style="color: #71717a; font-size: 12px;">Consistency Score</div>
            </div>
        """
    
    return f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background: #09090b; color: white;">
        <div style="text-align: center; padding: 20px 0;">
            <h1 style="color: #fff; margin: 0; font-size: 24px;">⏰ Your Trial Ends {days_text.title()}</h1>
        </div>
        <div style="padding: 20px; background: #18181b; border-radius: 8px; margin: 20px 0;">
            <p style="margin: 0; font-size: 16px;">Hey <strong>{username}</strong>,</p>
            <p style="margin: 15px 0;">Your 14-day free trial ends <strong style="color: #f97316;">{days_text}</strong>.</p>
            
            {streak_section}
            {consistency_section}
            
            <p style="margin: 15px 0; padding: 15px; background: #7f1d1d40; border: 1px solid #7f1d1d; border-radius: 8px; text-align: center;">
                <strong style="color: #fca5a5;">Don't lose your progress.</strong><br/>
                <span style="color: #a1a1aa; font-size: 14px;">Subscribe now to keep your momentum going.</span>
            </p>
        </div>
        <div style="text-align: center; padding: 20px;">
            <p style="color: #71717a; font-size: 12px;">Edge Mode - 1% Better Every Day</p>
        </div>
    </div>
    """


# ============ Notification Routes ============

@router.get("/inbox")
async def get_notifications(current_user: dict = Depends(get_current_user)):
    """Get user's in-app notifications"""
    notifications = await db.notifications.find(
        {'user_id': current_user['id']},
        {'_id': 0}
    ).sort('created_at', -1).limit(50).to_list(50)
    
    unread_count = await db.notifications.count_documents({
        'user_id': current_user['id'],
        'read': False
    })
    
    return {
        'notifications': notifications,
        'unread_count': unread_count
    }


@router.post("/mark-read/{notification_id}")
async def mark_notification_read(notification_id: str, current_user: dict = Depends(get_current_user)):
    """Mark a notification as read"""
    result = await db.notifications.update_one(
        {'id': notification_id, 'user_id': current_user['id']},
        {'$set': {'read': True}}
    )
    return {'success': result.modified_count > 0}


@router.post("/mark-all-read")
async def mark_all_notifications_read(current_user: dict = Depends(get_current_user)):
    """Mark all notifications as read"""
    result = await db.notifications.update_many(
        {'user_id': current_user['id'], 'read': False},
        {'$set': {'read': True}}
    )
    return {'marked_read': result.modified_count}


@router.get("/settings")
async def get_notification_settings(current_user: dict = Depends(get_current_user)):
    user = await db.users.find_one({'id': current_user['id']}, {'_id': 0})
    return {
        'streak_reminders': user.get('streak_reminders', True),
        'weekly_summary': user.get('weekly_summary', True),
        'morning_reminders': user.get('morning_reminders', True),
        'morning_reminder_time': user.get('morning_reminder_time', '08:00')
    }


@router.put("/settings")
async def update_notification_settings(settings: NotificationSettingsUpdate, current_user: dict = Depends(get_current_user)):
    update_fields = {}
    if settings.streak_reminders is not None:
        update_fields['streak_reminders'] = settings.streak_reminders
    if settings.weekly_summary is not None:
        update_fields['weekly_summary'] = settings.weekly_summary
    if settings.morning_reminders is not None:
        update_fields['morning_reminders'] = settings.morning_reminders
    if settings.morning_reminder_time is not None:
        update_fields['morning_reminder_time'] = settings.morning_reminder_time
    
    if update_fields:
        await db.users.update_one(
            {'id': current_user['id']},
            {'$set': update_fields}
        )
    return {'message': 'Notification settings updated', 'updated_fields': list(update_fields.keys())}


@router.post("/send-streak-reminder")
async def send_streak_reminder(current_user: dict = Depends(get_current_user)):
    """Send streak reminder email to the current user (for testing)"""
    if not current_user.get('streak_reminders', True):
        return {'message': 'Streak reminders disabled for this user'}
    
    html = get_streak_reminder_html(
        current_user.get('username', 'User'),
        current_user.get('current_streak', 0)
    )
    
    result = await send_email_async(
        current_user['email'],
        "🔥 Don't Break Your Streak! - Edge Mode",
        html
    )
    
    if result:
        return {'message': 'Streak reminder sent', 'email_id': result.get('id')}
    return {'message': 'Email not sent (check configuration)'}


@router.post("/send-weekly-summary")
async def send_weekly_summary(current_user: dict = Depends(get_current_user)):
    """Send weekly summary email to the current user (for testing)"""
    if not current_user.get('weekly_summary', True):
        return {'message': 'Weekly summaries disabled for this user'}
    
    user_id = current_user['id']
    now = datetime.now(timezone.utc)
    week_start = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
    
    sessions = await db.daily_sessions.find({
        'user_id': user_id,
        'timestamp': {'$gte': week_start.isoformat()}
    }, {'_id': 0}).to_list(100)
    
    total_sessions = len(sessions)
    total_minutes = sum(s.get('minutes_spent', 0) for s in sessions)
    days_logged = len(set(s.get('date') for s in sessions))
    consistency_pct = (days_logged / 7) * 100
    
    stats = {
        'total_sessions': total_sessions,
        'total_minutes': total_minutes,
        'consistency_pct': consistency_pct
    }
    
    html = get_weekly_summary_html(current_user.get('username', 'User'), stats)
    
    result = await send_email_async(
        current_user['email'],
        "📊 Your Weekly Summary - Edge Mode",
        html
    )
    
    if result:
        return {'message': 'Weekly summary sent', 'email_id': result.get('id'), 'stats': stats}
    return {'message': 'Email not sent (check configuration)', 'stats': stats}


@router.post("/send-trial-ending")
async def send_trial_ending_reminder(current_user: dict = Depends(get_current_user)):
    """Send trial ending reminder email to the current user (for testing)"""
    if not current_user.get('is_trial'):
        return {'message': 'User is not on trial'}
    
    if not current_user.get('streak_reminders', True):
        return {'message': 'Streak reminders disabled for this user'}
    
    now = datetime.now(timezone.utc)
    trial_end = datetime.fromisoformat(current_user['trial_ends_at'].replace('Z', '+00:00'))
    days_left = max(1, (trial_end.date() - now.date()).days)
    
    user_id = current_user['id']
    week_start = now.date() - timedelta(days=now.weekday())
    
    sessions = await db.daily_sessions.find({
        'user_id': user_id,
        'date': {'$gte': week_start.isoformat()}
    }, {'_id': 0}).to_list(100)
    
    unique_days = set(s['date'] for s in sessions)
    consistency_pct = (len(unique_days) / 7) * 100
    
    html = get_trial_ending_html(
        current_user.get('username', 'User'),
        days_left,
        current_user.get('current_streak', 0),
        consistency_pct
    )
    
    result = await send_email_async(
        current_user['email'],
        f"⏰ Your Edge Mode Trial Ends {'Tomorrow' if days_left == 1 else f'in {days_left} Days'}",
        html
    )
    
    if result:
        return {'message': 'Trial ending reminder sent', 'email_id': result.get('id'), 'days_left': days_left}
    return {'message': 'Email not sent (check configuration)', 'days_left': days_left}
