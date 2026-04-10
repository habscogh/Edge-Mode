"""
Scheduled jobs for Edge Mode
"""
from datetime import datetime, timezone, timedelta
import asyncio
import resend

from config import db, logger, RESEND_API_KEY, SENDER_EMAIL


# Import push notification functions (lazy import to avoid circular imports)
async def send_push(user_id: str, title: str, body: str, url: str = "/dashboard", tag: str = None):
    """Helper to send push notification"""
    try:
        from routes.push import send_push_to_user, PushMessage
        await send_push_to_user(user_id, PushMessage(
            title=title,
            body=body,
            url=url,
            tag=tag
        ))
    except Exception as e:
        logger.error(f"Failed to send push to {user_id}: {e}")


# ============ Email HTML Templates ============

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


def get_pet_streak_reminder_html(username: str, streak: int, pet_name: str, pet_icon: str, evolution_stage: int = 1) -> str:
    """Email template for streak reminder with virtual pet - pet encourages user to keep the streak"""
    
    # Consistent encouraging message from the pet
    day_word = "day" if streak == 1 else "days"
    pet_message = f"We're building something great - {streak} {day_word} and counting!"
    encouragement = "I believe in you! Let's train together today!"
    streak_color = "#f97316"  # Orange
    
    return f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background: linear-gradient(135deg, #09090b 0%, #1a0a0a 100%); color: white;">
        <div style="text-align: center; padding: 20px 0;">
            <h1 style="color: #f97316; margin: 0; font-size: 26px;">🔥 Don't Break Our Streak!</h1>
        </div>
        
        <div style="text-align: center; padding: 20px 0;">
            <div style="font-size: 70px; margin-bottom: 5px; filter: drop-shadow(0 0 15px rgba(249, 115, 22, 0.5));">{pet_icon}</div>
            <p style="color: #fbbf24; font-size: 18px; margin: 5px 0; font-weight: bold;">{pet_name}</p>
        </div>
        
        <div style="padding: 25px; background: linear-gradient(135deg, #18181b 0%, #1f1410 100%); border-radius: 16px; margin: 20px 0; border: 1px solid #f9731640;">
            <p style="margin: 0; font-size: 18px; color: #e5e5e5;">Hey <strong style="color: #fbbf24;">{username}</strong>,</p>
            
            <div style="text-align: center; margin: 20px 0;">
                <div style="display: inline-block; background: linear-gradient(135deg, #f9731620 0%, #fbbf2420 100%); border: 2px solid {streak_color}; border-radius: 16px; padding: 15px 30px;">
                    <div style="font-size: 42px; font-weight: bold; color: {streak_color};">{streak}</div>
                    <div style="color: #a1a1aa; font-size: 14px; text-transform: uppercase; letter-spacing: 1px;">Day Streak</div>
                </div>
            </div>
            
            <div style="margin: 20px 0; padding: 20px; background: #27272a; border-radius: 12px; border-left: 4px solid #f97316;">
                <p style="margin: 0; font-size: 16px; font-style: italic; color: #d4d4d4;">"{pet_message}</p>
                <p style="margin: 10px 0 0 0; font-size: 16px; font-style: italic; color: #fbbf24;">{encouragement}"</p>
                <p style="margin: 15px 0 0 0; font-size: 14px; color: #a1a1aa; text-align: right;">— {pet_name} {pet_icon}</p>
            </div>
        </div>
        
        <div style="text-align: center; padding: 20px;">
            <a href="https://edgemodeapp.com/dashboard" style="display: inline-block; background: linear-gradient(135deg, #f97316 0%, #ea580c 100%); color: white; padding: 16px 32px; text-decoration: none; border-radius: 12px; font-weight: bold; font-size: 18px; box-shadow: 0 4px 15px rgba(249, 115, 22, 0.4);">Keep Our Streak Alive! 🔥</a>
        </div>
        
        <div style="text-align: center; padding: 15px;">
            <p style="color: #71717a; font-size: 12px; margin: 0;">Edge Mode - 1% Better Every Day</p>
            <p style="color: #525252; font-size: 11px; margin: 5px 0 0 0;">{pet_name} is counting on you!</p>
        </div>
    </div>
    """


def get_weekly_summary_html(username: str, stats: dict) -> str:
    consistency_pct = stats.get('consistency_pct', 0)
    
    # Determine consistency rating and color
    if consistency_pct >= 85:
        rating = "ELITE"
        rating_color = "#22c55e"  # Green
        rating_emoji = "🏆"
        message = "Outstanding! You're in the top tier of performers."
    elif consistency_pct >= 70:
        rating = "STRONG"
        rating_color = "#10b981"  # Teal
        rating_emoji = "💪"
        message = "Great work! You're building solid habits."
    elif consistency_pct >= 50:
        rating = "BUILDING"
        rating_color = "#f59e0b"  # Amber
        rating_emoji = "📈"
        message = "Good progress! Keep pushing for more consistency."
    elif consistency_pct >= 25:
        rating = "DEVELOPING"
        rating_color = "#f97316"  # Orange
        rating_emoji = "🌱"
        message = "You're getting started. Aim for 4+ days next week!"
    else:
        rating = "NEEDS FOCUS"
        rating_color = "#ef4444"  # Red
        rating_emoji = "🎯"
        message = "Let's reset and aim higher next week. You've got this!"
    
    # Calculate days logged
    days_logged = round((consistency_pct / 100) * 7)
    
    # Build the consistency breakdown visual
    days_visual = ""
    day_names = ["M", "T", "W", "T", "F", "S", "S"]
    for i, day in enumerate(day_names):
        if i < days_logged:
            days_visual += f'<span style="display: inline-block; width: 28px; height: 28px; line-height: 28px; margin: 2px; background: {rating_color}; border-radius: 4px; text-align: center; font-weight: bold; font-size: 11px;">{day}</span>'
        else:
            days_visual += f'<span style="display: inline-block; width: 28px; height: 28px; line-height: 28px; margin: 2px; background: #27272a; border-radius: 4px; text-align: center; font-size: 11px; color: #52525b;">{day}</span>'
    
    return f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background: #09090b; color: white;">
        <div style="text-align: center; padding: 20px 0;">
            <h1 style="color: #fff; margin: 0; font-size: 24px;">📊 Your Weekly Summary</h1>
        </div>
        <div style="padding: 20px; background: #18181b; border-radius: 8px; margin: 20px 0;">
            <p style="margin: 0; font-size: 16px;">Hey <strong>{username}</strong>,</p>
            <p style="margin: 15px 0;">Here's how you did this week:</p>
            
            <!-- Stats Row -->
            <div style="display: flex; justify-content: space-around; padding: 15px 0; border-bottom: 1px solid #27272a;">
                <div style="text-align: center;">
                    <div style="font-size: 28px; font-weight: bold; color: #f97316;">{stats.get('total_sessions', 0)}</div>
                    <div style="color: #71717a; font-size: 12px;">Sessions</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 28px; font-weight: bold; color: #22c55e;">{stats.get('total_minutes', 0)}</div>
                    <div style="color: #71717a; font-size: 12px;">Minutes</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 28px; font-weight: bold; color: #3b82f6;">{days_logged}/7</div>
                    <div style="color: #71717a; font-size: 12px;">Days Active</div>
                </div>
            </div>
            
            <!-- Consistency Rating Section -->
            <div style="padding: 20px 0; text-align: center;">
                <div style="font-size: 14px; color: #71717a; margin-bottom: 10px;">CONSISTENCY RATING</div>
                <div style="font-size: 48px; margin-bottom: 5px;">{rating_emoji}</div>
                <div style="font-size: 24px; font-weight: bold; color: {rating_color}; letter-spacing: 2px;">{rating}</div>
                <div style="font-size: 32px; font-weight: bold; color: white; margin: 10px 0;">{consistency_pct:.0f}%</div>
                <p style="color: #a1a1aa; font-size: 14px; margin: 10px 0;">{message}</p>
            </div>
            
            <!-- Days Breakdown -->
            <div style="text-align: center; padding: 15px; background: #0f0f10; border-radius: 8px;">
                <div style="font-size: 11px; color: #71717a; margin-bottom: 8px;">YOUR WEEK</div>
                {days_visual}
            </div>
        </div>
        <div style="text-align: center; padding: 20px;">
            <a href="https://edgemodeapp.com/dashboard" style="display: inline-block; background: #10b981; color: white; padding: 12px 24px; text-decoration: none; border-radius: 8px; font-weight: bold;">View Full Dashboard</a>
        </div>
        <div style="text-align: center; padding: 10px;">
            <p style="color: #71717a; font-size: 12px;">Edge Mode - 1% Better Every Day</p>
        </div>
    </div>
    """


def get_inactive_reminder_html(username: str, days_inactive: int, total_platform_sessions: int = None) -> str:
    # Add community stats section for 7+ days inactive
    community_section = ""
    if total_platform_sessions and days_inactive >= 7:
        community_section = f"""
            <div style="text-align: center; padding: 15px; background: #27272a; border-radius: 8px; margin: 15px 0;">
                <p style="margin: 0; color: #a1a1aa; font-size: 14px;">While you've been away...</p>
                <div style="font-size: 28px; font-weight: bold; color: #10b981; margin: 10px 0;">{total_platform_sessions:,}</div>
                <p style="margin: 0; color: #71717a; font-size: 12px;">total sessions logged by students</p>
            </div>
        """
    
    return f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background: #09090b; color: white;">
        <div style="text-align: center; padding: 20px 0;">
            <h1 style="color: #fff; margin: 0; font-size: 24px;">👋 We Miss You!</h1>
        </div>
        <div style="padding: 20px; background: #18181b; border-radius: 8px; margin: 20px 0;">
            <p style="margin: 0; font-size: 16px;">Hey <strong>{username}</strong>,</p>
            <p style="margin: 15px 0;">It's been <strong style="color: #f97316;">{days_inactive} days</strong> since your last session.</p>
            {community_section}
            <p style="margin: 15px 0;">Remember: <em>Small steps lead to big changes.</em> Even 15 minutes today counts!</p>
            <p style="margin: 15px 0;">Your future self will thank you. 💪</p>
        </div>
        <div style="text-align: center; padding: 20px;">
            <a href="https://edgemodeapp.com/dashboard" style="display: inline-block; background: #10b981; color: white; padding: 12px 24px; text-decoration: none; border-radius: 8px; font-weight: bold;">Log a Session Now</a>
        </div>
        <div style="text-align: center; padding: 10px;">
            <p style="color: #71717a; font-size: 12px;">Edge Mode - 1% Better Every Day</p>
        </div>
    </div>
    """


def get_pet_missing_you_html(username: str, pet_name: str, pet_icon: str, days_inactive: int, happiness: int = 50) -> str:
    """Email template for inactive users with a pet - message comes FROM the pet"""
    
    # Pet's mood based on happiness level
    if happiness >= 70:
        mood_text = "I'm starting to miss our adventures together!"
        mood_color = "#f59e0b"  # Amber
    elif happiness >= 40:
        mood_text = "I've been waiting for you... I'm getting lonely."
        mood_color = "#f97316"  # Orange
    else:
        mood_text = "I really need you! My energy is fading..."
        mood_color = "#ef4444"  # Red
    
    # Different messages based on days inactive
    if days_inactive <= 3:
        urgency = "I haven't seen you in a while!"
        cta_text = "Come Play With Me!"
    elif days_inactive <= 7:
        urgency = f"It's been {days_inactive} days since we trained together..."
        cta_text = "Help Me Grow!"
    else:
        urgency = f"It's been {days_inactive} whole days! I miss you so much!"
        cta_text = "Come Back to Me!"
    
    return f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background: linear-gradient(135deg, #09090b 0%, #1a1a2e 100%); color: white;">
        <div style="text-align: center; padding: 30px 0;">
            <div style="font-size: 80px; margin-bottom: 10px; filter: drop-shadow(0 0 20px rgba(251, 191, 36, 0.5));">{pet_icon}</div>
            <h1 style="color: #fbbf24; margin: 0; font-size: 28px; text-shadow: 0 0 10px rgba(251, 191, 36, 0.3);">A Message from {pet_name}</h1>
        </div>
        
        <div style="padding: 25px; background: linear-gradient(135deg, #18181b 0%, #1f1f2e 100%); border-radius: 16px; margin: 20px 0; border: 1px solid #fbbf2440;">
            <p style="margin: 0; font-size: 18px; color: #e5e5e5;">Hey <strong style="color: #fbbf24;">{username}</strong>,</p>
            
            <div style="margin: 20px 0; padding: 20px; background: #27272a; border-radius: 12px; border-left: 4px solid {mood_color};">
                <p style="margin: 0; font-size: 16px; font-style: italic; color: #d4d4d4;">"{urgency}</p>
                <p style="margin: 10px 0 0 0; font-size: 16px; font-style: italic; color: {mood_color};">{mood_text}"</p>
                <p style="margin: 15px 0 0 0; font-size: 14px; color: #a1a1aa; text-align: right;">— {pet_name} {pet_icon}</p>
            </div>
            
            <div style="text-align: center; margin: 25px 0 15px 0;">
                <p style="color: #fbbf24; font-size: 20px; font-weight: bold; margin: 0;">I need your help to continue my growth!</p>
                <p style="color: #a1a1aa; font-size: 14px; margin: 10px 0 0 0;">Log a session and watch me evolve 🌟</p>
            </div>
        </div>
        
        <div style="text-align: center; padding: 20px;">
            <a href="https://edgemodeapp.com/dashboard" style="display: inline-block; background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%); color: #000; padding: 16px 32px; text-decoration: none; border-radius: 12px; font-weight: bold; font-size: 18px; box-shadow: 0 4px 15px rgba(251, 191, 36, 0.4);">{cta_text}</a>
        </div>
        
        <div style="text-align: center; padding: 15px;">
            <p style="color: #71717a; font-size: 12px; margin: 0;">Edge Mode - 1% Better Every Day</p>
            <p style="color: #525252; font-size: 11px; margin: 5px 0 0 0;">{pet_name} is waiting for you...</p>
        </div>
    </div>
    """


def get_trial_ending_html(username: str, days_left: int, streak: int, consistency_pct: float) -> str:
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


# ============ Scheduled Job Functions ============

async def send_streak_reminders_job():
    """Send streak reminder emails to users who haven't logged today
    If user has a pet, send personalized pet message instead
    """
    if not RESEND_API_KEY:
        logger.warning("RESEND_API_KEY not set, skipping streak reminders")
        return
    
    logger.info("Running streak reminder job...")
    
    # Use Eastern Time for consistency with session dates
    from utils.timezone import get_today_eastern
    today = get_today_eastern().isoformat()
    
    # Create a unique key for today to prevent duplicate emails
    reminder_key = f"streak_{today}"
    
    # Import pet types for icons
    from routes.pets import PET_TYPES
    
    try:
        users = await db.users.find({
            'streak_reminders': {'$ne': False},
            'current_streak': {'$gt': 0},
            'is_admin': {'$ne': True},  # Don't send to admins
            'role': {'$ne': 'admin'},  # Also check role field
            # Skip users who already received today's reminder
            'last_streak_reminder': {'$ne': reminder_key}
        }, {'_id': 0, 'id': 1, 'email': 1, 'username': 1, 'first_name': 1, 'current_streak': 1}).to_list(1000)
        
        sent_count = 0
        for user in users:
            # Double-check: skip if email already sent today (using email_log collection)
            already_sent = await db.email_log.find_one({
                'email': user['email'],
                'type': 'streak_reminder',
                'date': today
            })
            if already_sent:
                logger.debug(f"Skipping {user['email']} - already in email_log")
                continue
            
            session_today = await db.daily_sessions.find_one({
                'user_id': user['id'],
                'date': today
            })
            
            if not session_today:
                # Use atomic findOneAndUpdate to prevent duplicates across multiple instances
                # Only proceeds if this instance "claims" the user first
                result = await db.users.find_one_and_update(
                    {
                        'id': user['id'],
                        'last_streak_reminder': {'$ne': reminder_key}  # Double-check not already sent
                    },
                    {'$set': {'last_streak_reminder': reminder_key}},
                    return_document=False  # Returns original doc (before update)
                )
                
                # If result is None, another instance already claimed this user
                if result is None:
                    logger.debug(f"Skipping {user['email']} - already claimed by another instance")
                    continue
                
                # Log email before sending to prevent race conditions
                await db.email_log.insert_one({
                    'email': user['email'],
                    'user_id': user['id'],
                    'type': 'streak_reminder',
                    'date': today,
                    'sent_at': datetime.now(timezone.utc).isoformat()
                })
                
                streak = user.get('current_streak', 0)
                
                # Check if user has a pet
                user_pet = await db.user_pets.find_one({
                    'user_id': user['id'],
                    'is_active': True
                }, {'_id': 0})
                
                if user_pet and user_pet.get('pet_type') in PET_TYPES:
                    # User has a pet - send personalized pet streak reminder!
                    pet_type = user_pet['pet_type']
                    pet_info = PET_TYPES[pet_type]
                    pet_name = user_pet.get('custom_name') or pet_info['name']
                    evolution_stage = user_pet.get('evolution_stage', 1)
                    
                    # Get pet icon based on evolution stage
                    pet_icon = pet_info['stages'].get(evolution_stage, pet_info['stages'][1])['icon']
                    
                    # Use first name or username for personalization
                    display_name = user.get('first_name') or user.get('username', 'User').split('@')[0].capitalize()
                    
                    html = get_pet_streak_reminder_html(
                        display_name,
                        streak,
                        pet_name,
                        pet_icon,
                        evolution_stage
                    )
                    subject = f"🔥 {pet_name} Says: Don't Break Our Streak! - Edge Mode"
                else:
                    # No pet - send regular streak reminder
                    display_name = user.get('first_name') or user.get('username', 'User').split('@')[0].capitalize()
                    html = get_streak_reminder_html(
                        display_name,
                        streak
                    )
                    subject = "🔥 Don't Break Your Streak! - Edge Mode"
                
                # Send email
                try:
                    await asyncio.to_thread(resend.Emails.send, {
                        "from": SENDER_EMAIL,
                        "to": [user['email']],
                        "subject": subject,
                        "html": html
                    })
                    sent_count += 1
                except Exception as e:
                    logger.error(f"Failed to send streak reminder to {user['email']}: {e}")
                
                # Send push notification (personalized if user has pet)
                if user.get('push_enabled'):
                    if user_pet and user_pet.get('pet_type') in PET_TYPES:
                        pet_name = user_pet.get('custom_name') or PET_TYPES[user_pet['pet_type']]['name']
                        await send_push(
                            user['id'],
                            f"🔥 {pet_name}: Don't Break Our Streak!",
                            f"We're on a {streak}-day streak together! Let's keep it going!",
                            "/dashboard",
                            "pet-streak-reminder"
                        )
                    else:
                        await send_push(
                            user['id'],
                            "🔥 Don't Break Your Streak!",
                            f"You're on a {streak}-day streak! Log a session today.",
                            "/dashboard",
                            "streak-reminder"
                        )
        
        logger.info(f"Streak reminder job complete. Sent {sent_count} emails.")
    except Exception as e:
        logger.error(f"Streak reminder job failed: {e}")


async def send_weekly_summaries_job():
    """Send weekly summary emails to all opted-in users"""
    if not RESEND_API_KEY:
        logger.warning("RESEND_API_KEY not set, skipping weekly summaries")
        return
    
    logger.info("Running weekly summary job...")
    
    # Use Eastern Time for date calculations since sessions are logged with Eastern dates
    from utils.timezone import get_today_eastern
    today_eastern = get_today_eastern()
    week_start_date = (today_eastern - timedelta(days=7)).isoformat()
    
    logger.info(f"Weekly summary: Looking for sessions from {week_start_date} to {today_eastern.isoformat()}")
    
    # Create a unique key for this week to prevent duplicate emails
    week_key = today_eastern.strftime('%Y-W%W')
    
    try:
        # Use findAndModify pattern to atomically mark users and prevent duplicates
        sent_count = 0
        
        while True:
            # Atomically find and mark ONE user at a time to prevent race conditions
            user = await db.users.find_one_and_update(
                {
                    'weekly_summary': {'$ne': False},
                    'last_weekly_summary': {'$ne': week_key},
                    'email': {'$exists': True, '$ne': None}
                },
                {'$set': {'last_weekly_summary': week_key}},
                projection={'_id': 0, 'id': 1, 'email': 1, 'username': 1},
                return_document=False  # Return the document BEFORE update
            )
            
            if not user:
                break  # No more users to process
            
            user_id = user.get('id')
            user_email = user.get('email')
            username = user.get('username', 'User')
            
            if not user_email or not user_id:
                continue
            
            # Query sessions for this user
            sessions = await db.daily_sessions.find({
                'user_id': user_id,
                'date': {'$gte': week_start_date}
            }, {'_id': 0}).to_list(100)
            
            total_sessions = len(sessions)
            total_minutes = sum(s.get('minutes_spent', 0) for s in sessions)
            days_logged = len(set(s.get('date') for s in sessions if s.get('date')))
            consistency_pct = (days_logged / 7) * 100
            
            stats = {
                'total_sessions': total_sessions,
                'total_minutes': total_minutes,
                'consistency_pct': consistency_pct
            }
            
            html = get_weekly_summary_html(username, stats)
            
            try:
                await asyncio.to_thread(resend.Emails.send, {
                    "from": SENDER_EMAIL,
                    "to": [user_email],
                    "subject": "📊 Your Weekly Summary - Edge Mode",
                    "html": html
                })
                sent_count += 1
                logger.info(f"Weekly summary sent to {user_email}: {total_sessions} sessions, {total_minutes} mins")
            except Exception as e:
                logger.error(f"Failed to send weekly summary to {user_email}: {e}")
                # Even if email fails, we've already marked the user to prevent retry spam
        
        logger.info(f"Weekly summary job complete. Sent {sent_count} emails.")
    except Exception as e:
        logger.error(f"Weekly summary job failed: {e}")


async def send_inactive_reminders_job():
    """Send reminder emails to inactive users:
    - Days 2, 4, 6: Every other day reminders
    - Days 7, 10, 14, 21, 30: Extended reminders with community stats
    - If user has a pet, send personalized pet message instead
    """
    if not RESEND_API_KEY:
        logger.warning("RESEND_API_KEY not set, skipping inactive reminders")
        return
    
    logger.info("Running inactive user reminder job...")
    now = datetime.now(timezone.utc)
    
    # Create a unique key for today to prevent duplicate emails
    from utils.timezone import get_today_eastern
    today_eastern = get_today_eastern().isoformat()
    reminder_key = f"inactive_{today_eastern}"
    
    # Define which days to send reminders
    REMINDER_DAYS = [2, 4, 6, 7, 10, 14, 21, 30]
    
    # Import pet types for icons
    from routes.pets import PET_TYPES
    
    try:
        # Get total platform sessions for community stats (used for 7+ day reminders)
        total_platform_sessions = await db.daily_sessions.count_documents({})
        
        # Only send to users who opted in to reminders
        # Exclude admin users and users who already received today's reminder
        users = await db.users.find({
            'streak_reminders': {'$ne': False},
            'is_admin': {'$ne': True},
            'last_inactive_reminder': {'$ne': reminder_key}
        }, {'_id': 0, 'id': 1, 'email': 1, 'username': 1, 'last_log_date': 1}).to_list(1000)
        
        sent_count = 0
        for user in users:
            last_log = user.get('last_log_date')
            
            # Skip if no last_log_date recorded
            if not last_log:
                continue
            
            # Calculate days inactive
            last_log_str = last_log[:10] if len(last_log) > 10 else last_log
            last_log_date = datetime.fromisoformat(last_log_str).date()
            days_inactive = (today_eastern - last_log_date).days
            
            # Only send on specific reminder days
            if days_inactive not in REMINDER_DAYS:
                continue
            
            # Use atomic findOneAndUpdate to prevent duplicates across multiple instances
            result = await db.users.find_one_and_update(
                {
                    'id': user['id'],
                    'last_inactive_reminder': {'$ne': reminder_key}
                },
                {'$set': {'last_inactive_reminder': reminder_key}},
                return_document=False
            )
            
            # If result is None, another instance already claimed this user
            if result is None:
                logger.debug(f"Skipping inactive reminder for {user['email']} - already claimed")
                continue
            
            # Check if user has a pet
            user_pet = await db.user_pets.find_one({
                'user_id': user['id'],
                'is_active': True
            }, {'_id': 0})
            
            if user_pet and user_pet.get('pet_type') in PET_TYPES:
                # User has a pet - send personalized pet message!
                pet_type = user_pet['pet_type']
                pet_info = PET_TYPES[pet_type]
                pet_name = user_pet.get('custom_name') or pet_info['name']
                evolution_stage = user_pet.get('evolution_stage', 1)
                happiness = user_pet.get('happiness', 50)
                
                # Get pet icon based on evolution stage
                pet_icon = pet_info['stages'].get(evolution_stage, pet_info['stages'][1])['icon']
                
                html = get_pet_missing_you_html(
                    user.get('username', 'User'),
                    pet_name,
                    pet_icon,
                    days_inactive,
                    happiness
                )
                subject = f"🐾 {pet_name} Misses You! - Edge Mode"
            else:
                # No pet - send regular inactive reminder
                include_stats = days_inactive >= 7
                html = get_inactive_reminder_html(
                    user.get('username', 'User'),
                    days_inactive,
                    total_platform_sessions if include_stats else None
                )
                subject = "👋 We Miss You! - Edge Mode"
            
            # Send email
            try:
                await asyncio.to_thread(resend.Emails.send, {
                    "from": SENDER_EMAIL,
                    "to": [user['email']],
                    "subject": subject,
                    "html": html
                })
                sent_count += 1
            except Exception as e:
                logger.error(f"Failed to send inactive reminder to {user['email']}: {e}")
            
            # Send push notification (personalized if user has pet)
            if user.get('push_enabled'):
                if user_pet and user_pet.get('pet_type') in PET_TYPES:
                    pet_name = user_pet.get('custom_name') or PET_TYPES[user_pet['pet_type']]['name']
                    await send_push(
                        user['id'],
                        f"🐾 {pet_name} Misses You!",
                        f"{pet_name} needs your help to grow! Come back and train together.",
                        "/dashboard",
                        "pet-inactivity"
                    )
                else:
                    await send_push(
                        user['id'],
                        "👋 We Miss You!",
                        f"It's been {days_inactive} days. Small steps lead to big changes!",
                        "/dashboard",
                        "inactivity"
                    )
        
        logger.info(f"Inactive reminder job complete. Sent {sent_count} emails.")
    except Exception as e:
        logger.error(f"Inactive reminder job failed: {e}")


async def send_trial_ending_reminders_job():
    """Send reminder emails to trial users with 1-3 days left"""
    if not RESEND_API_KEY:
        logger.warning("RESEND_API_KEY not set, skipping trial ending reminders")
        return
    
    logger.info("Running trial ending reminder job...")
    now = datetime.now(timezone.utc)
    
    try:
        # Only get users who are STILL on trial (is_trial=True)
        # Exclude paid subscribers and admins
        users = await db.users.find({
            'is_trial': True,
            'trial_ends_at': {'$exists': True},
            'streak_reminders': {'$ne': False},
            'is_admin': {'$ne': True}  # Exclude admins
        }, {'_id': 0}).to_list(1000)
        
        sent_count = 0
        for user in users:
            # Double-check: skip if user has paid (is_trial should be False for paid users)
            if user.get('is_trial') == False:
                continue
            
            # Skip admin emails
            if user.get('email', '').lower() == 'admin@edgemodeapp.com':
                continue
                
            trial_end = datetime.fromisoformat(user['trial_ends_at'].replace('Z', '+00:00'))
            days_left = (trial_end.date() - now.date()).days
            
            if 1 <= days_left <= 3:
                user_id = user['id']
                week_start = now.date() - timedelta(days=now.weekday())
                
                sessions = await db.daily_sessions.find({
                    'user_id': user_id,
                    'date': {'$gte': week_start.isoformat()}
                }, {'_id': 0}).to_list(100)
                
                unique_days = set(s['date'] for s in sessions)
                consistency_pct = (len(unique_days) / 7) * 100
                
                html = get_trial_ending_html(
                    user.get('username', 'User'),
                    days_left,
                    user.get('current_streak', 0),
                    consistency_pct
                )
                
                try:
                    await asyncio.to_thread(resend.Emails.send, {
                        "from": SENDER_EMAIL,
                        "to": [user['email']],
                        "subject": f"⏰ Your Edge Mode Trial Ends {'Tomorrow' if days_left == 1 else f'in {days_left} Days'}",
                        "html": html
                    })
                    sent_count += 1
                    logger.info(f"Sent trial ending reminder to {user['email']} ({days_left} days left)")
                except Exception as e:
                    logger.error(f"Failed to send trial ending reminder to {user['email']}: {e}")
        
        logger.info(f"Trial ending reminder job complete. Sent {sent_count} emails.")
    except Exception as e:
        logger.error(f"Trial ending reminder job failed: {e}")


async def send_parent_weekly_summaries_job():
    """Send weekly progress summaries to all parent emails (runs every Sunday)"""
    if not RESEND_API_KEY:
        logger.warning("RESEND_API_KEY not set, skipping parent weekly summaries")
        return
    
    logger.info("Running parent weekly summary job...")
    
    try:
        # Get all active parent links (now email-based, no account needed)
        parent_links = await db.parent_links.find({'status': 'active'}).to_list(1000)
        
        # Group by parent email (in case one parent has multiple students)
        parents_students = {}
        for link in parent_links:
            parent_email = link.get('parent_email')
            if not parent_email:
                continue
            if parent_email not in parents_students:
                parents_students[parent_email] = []
            parents_students[parent_email].append({
                'student_id': link['student_id'],
                'student_username': link.get('student_username')
            })
        
        sent_count = 0
        # Use Eastern Time for date calculations since sessions are logged with Eastern dates
        from utils.timezone import get_today_eastern
        today = get_today_eastern()
        week_start = (today - timedelta(days=7)).isoformat()
        
        for parent_email, students in parents_students.items():
            students_html = ""
            for student_info in students:
                student_id = student_info['student_id']
                student = await db.users.find_one({'id': student_id}, {'_id': 0, 'password': 0})
                if not student:
                    continue
                
                sessions = await db.daily_sessions.find({
                    'user_id': student_id,
                    'date': {'$gte': week_start}
                }).to_list(100)
                
                unique_days = len(set(s['date'] for s in sessions))
                total_minutes = sum(s.get('minutes_spent', 30) for s in sessions)
                consistency_pct = round((unique_days / 7) * 100, 1)
                
                # Determine consistency rating
                if consistency_pct >= 85:
                    rating = "ELITE"
                    rating_color = "#22c55e"
                    rating_emoji = "🏆"
                elif consistency_pct >= 70:
                    rating = "STRONG"
                    rating_color = "#10b981"
                    rating_emoji = "💪"
                elif consistency_pct >= 50:
                    rating = "BUILDING"
                    rating_color = "#f59e0b"
                    rating_emoji = "📈"
                elif consistency_pct >= 25:
                    rating = "DEVELOPING"
                    rating_color = "#f97316"
                    rating_emoji = "🌱"
                else:
                    rating = "NEEDS FOCUS"
                    rating_color = "#ef4444"
                    rating_emoji = "🎯"
                
                streak_color = "#f97316" if student.get('current_streak', 0) >= 7 else "#10b981"
                
                students_html += f"""
                <div style="padding: 15px; background: #27272a; border-radius: 8px; margin: 10px 0;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                        <div style="font-size: 18px; font-weight: bold; color: white;">{student.get('username', 'Student')}</div>
                        <div style="background: {rating_color}20; color: {rating_color}; padding: 4px 10px; border-radius: 12px; font-size: 11px; font-weight: bold;">
                            {rating_emoji} {rating}
                        </div>
                    </div>
                    <div style="display: flex; justify-content: space-between; flex-wrap: wrap;">
                        <div style="text-align: center; padding: 10px; flex: 1; min-width: 70px;">
                            <div style="font-size: 24px; font-weight: bold; color: {streak_color};">🔥 {student.get('current_streak', 0)}</div>
                            <div style="color: #71717a; font-size: 11px;">Day Streak</div>
                        </div>
                        <div style="text-align: center; padding: 10px; flex: 1; min-width: 70px;">
                            <div style="font-size: 24px; font-weight: bold; color: #10b981;">{len(sessions)}</div>
                            <div style="color: #71717a; font-size: 11px;">Sessions</div>
                        </div>
                        <div style="text-align: center; padding: 10px; flex: 1; min-width: 70px;">
                            <div style="font-size: 24px; font-weight: bold; color: {rating_color};">{consistency_pct}%</div>
                            <div style="color: #71717a; font-size: 11px;">Consistency</div>
                        </div>
                        <div style="text-align: center; padding: 10px; flex: 1; min-width: 70px;">
                            <div style="font-size: 24px; font-weight: bold; color: #a1a1aa;">{total_minutes}</div>
                            <div style="color: #71717a; font-size: 11px;">Minutes</div>
                        </div>
                    </div>
                </div>
                """
            
            if not students_html:
                continue
            
            html = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background: #09090b; color: white;">
                <div style="text-align: center; padding: 20px 0;">
                    <h1 style="color: #10b981; margin: 0; font-size: 24px;">📊 Weekly Progress Report</h1>
                    <p style="color: #71717a; margin-top: 5px;">Here's how your student(s) did this week</p>
                </div>
                <div style="padding: 10px;">
                    {students_html}
                </div>
                <div style="text-align: center; padding: 20px;">
                    <p style="color: #71717a; font-size: 12px;">Edge Mode - 1% Better Every Day</p>
                    <p style="color: #52525b; font-size: 11px; margin-top: 10px;">You're receiving this because a student added you as their parent on Edge Mode.</p>
                </div>
            </div>
            """
            
            try:
                await asyncio.to_thread(resend.Emails.send, {
                    "from": SENDER_EMAIL,
                    "to": [parent_email],
                    "subject": "📊 Your Child's Weekly Progress Report - Edge Mode",
                    "html": html
                })
                sent_count += 1
            except Exception as e:
                logger.error(f"Failed to send weekly summary to parent {parent_email}: {e}")
        
        logger.info(f"Parent weekly summary job complete. Sent {sent_count} emails.")
    except Exception as e:
        logger.error(f"Parent weekly summary job failed: {e}")


async def send_parent_inactivity_alerts_job():
    """Alert parents when their student hasn't logged in for 3+ days"""
    if not RESEND_API_KEY:
        logger.warning("RESEND_API_KEY not set, skipping parent inactivity alerts")
        return
    
    logger.info("Running parent inactivity alert job...")
    
    try:
        # Use Eastern Time since last_log_date is stored in Eastern Time
        from utils.timezone import get_today_eastern
        today_eastern = get_today_eastern()
        three_days_ago = (today_eastern - timedelta(days=3)).isoformat()
        
        parent_links = await db.parent_links.find({'status': 'active'}).to_list(1000)
        
        sent_count = 0
        alerted_pairs = set()
        
        for link in parent_links:
            student_id = link['student_id']
            parent_email = link.get('parent_email')
            pair_key = f"{parent_email}_{student_id}"
            
            if pair_key in alerted_pairs or not parent_email:
                continue
            
            student = await db.users.find_one({'id': student_id}, {'_id': 0, 'password': 0})
            if not student:
                continue
            
            last_log = student.get('last_log_date')
            
            # Compare dates properly - last_log might be date string or datetime string
            if last_log:
                # Handle both date-only strings and datetime strings
                last_log_str = last_log[:10] if len(last_log) > 10 else last_log
                if last_log_str <= three_days_ago:
                    last_log_date = datetime.fromisoformat(last_log_str).date()
                    days_inactive = (today_eastern - last_log_date).days
                    
                    if 3 <= days_inactive <= 7:
                        html = f"""
                        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background: #09090b; color: white;">
                            <div style="text-align: center; padding: 20px 0;">
                                <h1 style="color: #f97316; margin: 0; font-size: 24px;">⚠️ Activity Alert</h1>
                            </div>
                            <div style="padding: 20px; background: #18181b; border-radius: 8px; margin: 20px 0; text-align: center;">
                                <p style="margin: 0; font-size: 18px; color: #a1a1aa;">Heads up!</p>
                                <p style="margin: 15px 0; font-size: 20px;"><strong style="color: #10b981;">{student.get('username', 'Your student')}</strong> hasn't logged a session in</p>
                                <div style="font-size: 48px; font-weight: bold; color: #f97316; margin: 20px 0;">{days_inactive} days</div>
                                <p style="margin: 15px 0; color: #71717a;">A gentle reminder might help them get back on track!</p>
                            </div>
                            <div style="text-align: center; padding: 20px;">
                                <p style="color: #71717a; font-size: 12px;">Edge Mode - 1% Better Every Day</p>
                                <p style="color: #52525b; font-size: 11px; margin-top: 10px;">You're receiving this because {student.get('username')} added you as their parent on Edge Mode.</p>
                            </div>
                        </div>
                        """
                        
                        try:
                            await asyncio.to_thread(resend.Emails.send, {
                                "from": SENDER_EMAIL,
                                "to": [parent_email],
                                "subject": f"⚠️ {student.get('username', 'Your student')} hasn't logged in for {days_inactive} days",
                                "html": html
                            })
                            sent_count += 1
                            alerted_pairs.add(pair_key)
                        except Exception as e:
                            logger.error(f"Failed to send inactivity alert to parent {parent_email}: {e}")
        
        logger.info(f"Parent inactivity alert job complete. Sent {sent_count} emails.")
    except Exception as e:
        logger.error(f"Parent inactivity alert job failed: {e}")



# ============ Morning Reminder Templates ============

MORNING_QUOTES = [
    "Today is a new opportunity to become 1% better than yesterday.",
    "Champions are made in the moments when no one is watching.",
    "Small steps every day lead to massive results over time.",
    "Your future self will thank you for the work you put in today.",
    "Success is the sum of small efforts repeated day in and day out.",
    "The only bad workout is the one that didn't happen.",
    "Discipline is choosing between what you want now and what you want most.",
    "Every expert was once a beginner. Start where you are.",
    "Progress, not perfection. Show up and give your best today.",
    "The harder you work today, the easier it gets tomorrow.",
    "You don't have to be great to start, but you have to start to be great.",
    "The secret of getting ahead is getting started.",
    "What you do today can improve all your tomorrows.",
    "Push yourself because no one else is going to do it for you.",
    "Don't watch the clock; do what it does. Keep going.",
    "Wake up with determination. Go to bed with satisfaction.",
    "Dream big. Start small. Act now.",
    "The pain you feel today will be the strength you feel tomorrow.",
    "Your only limit is your mind.",
    "Believe you can and you're halfway there.",
    "Make today so awesome that yesterday gets jealous.",
    "Be stronger than your excuses.",
    "It's not about being the best. It's about being better than you were yesterday.",
    "The best time to start was yesterday. The next best time is now.",
    "Hustle in silence. Let your success make the noise.",
    "Stay focused and never give up on your dreams.",
    "Great things never come from comfort zones.",
    "Work hard in silence. Let success be your noise.",
    "The difference between ordinary and extraordinary is that little extra.",
    "You are capable of amazing things.",
    "Today's actions become tomorrow's habits.",
    "Rise up, start fresh, and see the bright opportunity in each new day.",
    "Your potential is endless. Go do what you were created to do.",
    "Make each day your masterpiece.",
    "The grind includes Friday, Saturday, and Sunday.",
    "Comfort is the enemy of progress.",
    "Prove them wrong.",
    "Be so good they can't ignore you.",
    "Results happen over time, not overnight. Stay patient and stay focused.",
    "You're not tired, you're uninspired. Find your fire today."
]


def get_morning_reminder_html(username: str, streak: int, quote: str, pillars: list) -> str:
    """Generate HTML for morning reminder email"""
    streak_section = ""
    if streak > 0:
        streak_section = f"""
            <div style="display: inline-block; padding: 10px 20px; background: #27272a; border-radius: 8px; margin: 10px 0;">
                <span style="color: #f97316; font-weight: bold; font-size: 18px;">🔥 {streak}-day streak</span>
            </div>
        """
    
    pillars_section = ""
    if pillars:
        pillar_items = "".join([
            f'<span style="display: inline-block; background: #10b98120; color: #10b981; padding: 4px 10px; border-radius: 4px; margin: 2px; font-size: 12px;">{p}</span>'
            for p in pillars[:3]
        ])
        pillars_section = f"""
            <div style="margin: 15px 0;">
                <p style="color: #71717a; font-size: 12px; margin-bottom: 5px;">Your focus areas today:</p>
                {pillar_items}
            </div>
        """
    
    return f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background: #09090b; color: white;">
        <div style="text-align: center; padding: 20px 0;">
            <h1 style="color: #10b981; margin: 0; font-size: 24px;">☀️ Good Morning, {username}!</h1>
        </div>
        <div style="padding: 20px; background: #18181b; border-radius: 8px; margin: 20px 0; text-align: center;">
            <p style="font-size: 16px; font-style: italic; color: #a1a1aa; margin: 0;">"{quote}"</p>
            {streak_section}
            {pillars_section}
            <p style="margin: 20px 0 10px 0; color: #71717a; font-size: 14px;">Ready to crush it today? 💪</p>
        </div>
        <div style="text-align: center; padding: 20px;">
            <a href="https://edgemodeapp.com/dashboard" style="display: inline-block; background: #10b981; color: white; padding: 12px 24px; text-decoration: none; border-radius: 8px; font-weight: bold;">Log Your Progress</a>
        </div>
        <div style="text-align: center; padding: 10px;">
            <p style="color: #71717a; font-size: 12px;">Edge Mode - 1% Better Every Day</p>
        </div>
    </div>
    """


async def send_morning_reminders_job():
    """Send morning motivational reminder emails to opted-in users"""
    if not RESEND_API_KEY:
        logger.warning("RESEND_API_KEY not set, skipping morning reminders")
        return
    
    logger.info("Running morning reminder job...")
    import random
    
    # Create a unique key for today to prevent duplicate emails
    from utils.timezone import get_today_eastern
    today_eastern = get_today_eastern().isoformat()
    reminder_key = f"morning_{today_eastern}"
    
    try:
        # Find users who have opted into morning reminders and haven't received today's
        users = await db.users.find({
            'morning_reminders': True,
            'is_admin': {'$ne': True},
            'last_morning_reminder': {'$ne': reminder_key}
        }, {'_id': 0, 'id': 1, 'email': 1, 'username': 1, 'current_streak': 1}).to_list(1000)
        
        sent_count = 0
        for user in users:
            # Get user's pillars
            pillars_docs = await db.user_pillars.find({'user_id': user['id']}, {'_id': 0, 'pillar_name': 1}).to_list(5)
            pillar_names = [p['pillar_name'].split('/')[0] for p in pillars_docs]
            
            # Pick a random motivational quote
            quote = random.choice(MORNING_QUOTES)
            
            # Use atomic findOneAndUpdate to prevent duplicates across multiple instances
            result = await db.users.find_one_and_update(
                {
                    'id': user['id'],
                    'last_morning_reminder': {'$ne': reminder_key}
                },
                {'$set': {'last_morning_reminder': reminder_key}},
                return_document=False
            )
            
            # If result is None, another instance already claimed this user
            if result is None:
                logger.debug(f"Skipping morning reminder for {user['email']} - already claimed")
                continue
            
            html = get_morning_reminder_html(
                user.get('username', 'Champion'),
                user.get('current_streak', 0),
                quote,
                pillar_names
            )
            
            try:
                await asyncio.to_thread(resend.Emails.send, {
                    "from": SENDER_EMAIL,
                    "to": [user['email']],
                    "subject": "☀️ Good Morning! Your Daily Motivation - Edge Mode",
                    "html": html
                })
                sent_count += 1
            except Exception as e:
                logger.error(f"Failed to send morning reminder to {user['email']}: {e}")
            
            # Also send push notification if enabled
            if user.get('push_enabled'):
                await send_push(
                    user['id'],
                    "☀️ Good Morning!",
                    quote[:60] + "..." if len(quote) > 60 else quote,
                    "/dashboard",
                    "morning-reminder"
                )
        
        logger.info(f"Morning reminder job complete. Sent {sent_count} emails.")
    except Exception as e:
        logger.error(f"Morning reminder job failed: {e}")


# ============ XP Event Notifications ============

def get_xp_event_started_html(event_name: str, multiplier: float, description: str, icon: str, hours_left: int) -> str:
    """Email template for XP event started"""
    return f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background: linear-gradient(135deg, #1a0033 0%, #09090b 100%); color: white;">
        <div style="text-align: center; padding: 30px 0;">
            <div style="font-size: 60px; margin-bottom: 10px;">{icon}</div>
            <h1 style="color: #fff; margin: 0; font-size: 28px;">{event_name}</h1>
            <p style="color: #a78bfa; font-size: 16px; margin: 10px 0;">IS NOW LIVE!</p>
        </div>
        <div style="padding: 25px; background: linear-gradient(135deg, #7c3aed20 0%, #ec489920 100%); border: 1px solid #7c3aed50; border-radius: 12px; margin: 20px 0; text-align: center;">
            <div style="font-size: 48px; font-weight: bold; color: #a78bfa;">{int(multiplier)}x XP</div>
            <p style="color: #d1d5db; margin: 10px 0 0 0;">{description}</p>
        </div>
        <div style="background: #18181b; border-radius: 8px; padding: 20px; margin: 20px 0;">
            <div style="display: flex; align-items: center; justify-content: center; gap: 10px;">
                <span style="color: #fbbf24; font-size: 24px;">⏰</span>
                <span style="color: #fbbf24; font-size: 18px; font-weight: bold;">{hours_left} hours remaining</span>
            </div>
        </div>
        <div style="text-align: center; padding: 20px;">
            <a href="https://edgemodeapp.com/dashboard" style="display: inline-block; background: linear-gradient(135deg, #7c3aed 0%, #ec4899 100%); color: white; padding: 15px 40px; border-radius: 25px; text-decoration: none; font-weight: bold; font-size: 16px;">Log In & Earn XP!</a>
        </div>
        <div style="text-align: center; padding: 20px;">
            <p style="color: #71717a; font-size: 12px;">Edge Mode - 1% Better Every Day</p>
        </div>
    </div>
    """


def get_xp_event_ending_html(event_name: str, multiplier: float, hours_left: int, icon: str) -> str:
    """Email template for XP event ending soon"""
    return f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background: #09090b; color: white;">
        <div style="text-align: center; padding: 30px 0;">
            <div style="font-size: 40px; margin-bottom: 10px;">⏰</div>
            <h1 style="color: #fbbf24; margin: 0; font-size: 24px;">HURRY! Event Ending Soon!</h1>
        </div>
        <div style="padding: 25px; background: #18181b; border: 1px solid #fbbf24; border-radius: 12px; margin: 20px 0; text-align: center;">
            <div style="font-size: 36px; margin-bottom: 10px;">{icon}</div>
            <div style="font-size: 20px; font-weight: bold; color: white;">{event_name}</div>
            <div style="font-size: 32px; font-weight: bold; color: #a78bfa; margin: 10px 0;">{int(multiplier)}x XP</div>
            <p style="color: #ef4444; font-weight: bold; margin: 15px 0 0 0;">Only {hours_left} hour{'s' if hours_left > 1 else ''} left!</p>
        </div>
        <div style="text-align: center; padding: 20px;">
            <a href="https://edgemodeapp.com/dashboard" style="display: inline-block; background: #fbbf24; color: black; padding: 15px 40px; border-radius: 25px; text-decoration: none; font-weight: bold; font-size: 16px;">Maximize Your XP Now!</a>
        </div>
        <div style="text-align: center; padding: 20px;">
            <p style="color: #71717a; font-size: 12px;">Edge Mode - 1% Better Every Day</p>
        </div>
    </div>
    """


async def send_xp_event_notifications_job():
    """
    Check for XP events that:
    1. Just started (within last hour) - send "event started" notification
    2. Ending soon (1-2 hours left) - send "event ending" reminder
    
    Run this job every 30 minutes.
    """
    if not RESEND_API_KEY:
        logger.warning("Resend API key not configured, skipping XP event notifications")
        return
    
    try:
        now = datetime.now(timezone.utc)
        one_hour_ago = now - timedelta(hours=1)
        
        # Find events that started in the last hour (for "just started" notifications)
        just_started_events = await db.xp_events.find({
            'is_active': True,
            'starts_at': {
                '$gte': one_hour_ago.isoformat(),
                '$lte': now.isoformat()
            },
            'start_notified': {'$ne': True}  # Haven't sent start notification yet
        }, {'_id': 0}).to_list(10)
        
        # Find events ending in 1-2 hours (for "ending soon" notifications)
        one_hour_later = now + timedelta(hours=1)
        two_hours_later = now + timedelta(hours=2)
        
        ending_soon_events = await db.xp_events.find({
            'is_active': True,
            'ends_at': {
                '$gte': one_hour_later.isoformat(),
                '$lte': two_hours_later.isoformat()
            },
            'end_notified': {'$ne': True}  # Haven't sent ending notification yet
        }, {'_id': 0}).to_list(10)
        
        # Get all users who have email notifications enabled (or all users for important events)
        users = await db.users.find(
            {},  # All users for XP events
            {'_id': 0, 'id': 1, 'email': 1, 'username': 1, 'push_enabled': 1}
        ).to_list(10000)
        
        # Send "Event Started" notifications
        for event in just_started_events:
            event_name = event.get('name', 'XP Event')
            multiplier = event.get('multiplier', 2.0)
            description = event.get('description', f'Earn {int(multiplier)}x XP!')
            icon = event.get('icon', '⚡')
            
            # Calculate hours left
            ends_at = datetime.fromisoformat(event['ends_at'].replace('Z', '+00:00'))
            hours_left = max(1, int((ends_at - now).total_seconds() / 3600))
            
            sent_count = 0
            push_count = 0
            
            for user in users:
                # Send email
                try:
                    html = get_xp_event_started_html(event_name, multiplier, description, icon, hours_left)
                    await asyncio.to_thread(resend.Emails.send, {
                        "from": SENDER_EMAIL,
                        "to": [user['email']],
                        "subject": f"{icon} {event_name} - Earn {int(multiplier)}x XP NOW!",
                        "html": html
                    })
                    sent_count += 1
                except Exception as e:
                    logger.error(f"Failed to send XP event email to {user['email']}: {e}")
                
                # Send push notification if enabled
                if user.get('push_enabled'):
                    try:
                        await send_push(
                            user['id'],
                            f"{icon} {event_name} is LIVE!",
                            f"Earn {int(multiplier)}x XP on all activities! Log in now!",
                            "/dashboard",
                            "xp-event-started"
                        )
                        push_count += 1
                    except Exception as e:
                        logger.error(f"Failed to send XP event push to {user['id']}: {e}")
            
            # Mark event as notified
            await db.xp_events.update_one(
                {'id': event['id']},
                {'$set': {'start_notified': True, 'start_notified_at': now.isoformat()}}
            )
            
            logger.info(f"XP Event '{event_name}' started: sent {sent_count} emails, {push_count} push notifications")
        
        # Send "Event Ending Soon" notifications
        for event in ending_soon_events:
            event_name = event.get('name', 'XP Event')
            multiplier = event.get('multiplier', 2.0)
            icon = event.get('icon', '⚡')
            
            # Calculate hours left
            ends_at = datetime.fromisoformat(event['ends_at'].replace('Z', '+00:00'))
            hours_left = max(1, int((ends_at - now).total_seconds() / 3600))
            
            sent_count = 0
            push_count = 0
            
            for user in users:
                # Send email
                try:
                    html = get_xp_event_ending_html(event_name, multiplier, hours_left, icon)
                    await asyncio.to_thread(resend.Emails.send, {
                        "from": SENDER_EMAIL,
                        "to": [user['email']],
                        "subject": f"⏰ HURRY! {event_name} ends in {hours_left} hour{'s' if hours_left > 1 else ''}!",
                        "html": html
                    })
                    sent_count += 1
                except Exception as e:
                    logger.error(f"Failed to send XP event ending email to {user['email']}: {e}")
                
                # Send push notification if enabled
                if user.get('push_enabled'):
                    try:
                        await send_push(
                            user['id'],
                            f"⏰ {event_name} Ending Soon!",
                            f"Only {hours_left} hour{'s' if hours_left > 1 else ''} left! Maximize your XP!",
                            "/dashboard",
                            "xp-event-ending"
                        )
                        push_count += 1
                    except Exception as e:
                        logger.error(f"Failed to send XP event ending push to {user['id']}: {e}")
            
            # Mark event as end-notified
            await db.xp_events.update_one(
                {'id': event['id']},
                {'$set': {'end_notified': True, 'end_notified_at': now.isoformat()}}
            )
            
            logger.info(f"XP Event '{event_name}' ending soon: sent {sent_count} emails, {push_count} push notifications")
        
        logger.info(f"XP event notification job complete. Processed {len(just_started_events)} started events, {len(ending_soon_events)} ending events.")
    except Exception as e:
        logger.error(f"XP event notification job failed: {e}")
