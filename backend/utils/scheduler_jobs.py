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
    """Send streak reminder emails to users who haven't logged today"""
    if not RESEND_API_KEY:
        logger.warning("RESEND_API_KEY not set, skipping streak reminders")
        return
    
    logger.info("Running streak reminder job...")
    today = datetime.now(timezone.utc).date().isoformat()
    
    try:
        users = await db.users.find({
            'streak_reminders': {'$ne': False},
            'current_streak': {'$gt': 0}
        }, {'_id': 0, 'id': 1, 'email': 1, 'username': 1, 'current_streak': 1}).to_list(1000)
        
        sent_count = 0
        for user in users:
            session_today = await db.daily_sessions.find_one({
                'user_id': user['id'],
                'date': today
            })
            
            if not session_today:
                html = get_streak_reminder_html(
                    user.get('username', 'User'),
                    user.get('current_streak', 0)
                )
                
                # Send email
                try:
                    await asyncio.to_thread(resend.Emails.send, {
                        "from": SENDER_EMAIL,
                        "to": [user['email']],
                        "subject": "🔥 Don't Break Your Streak! - Edge Mode",
                        "html": html
                    })
                    sent_count += 1
                except Exception as e:
                    logger.error(f"Failed to send streak reminder to {user['email']}: {e}")
                
                # Send push notification
                if user.get('push_enabled'):
                    await send_push(
                        user['id'],
                        "🔥 Don't Break Your Streak!",
                        f"You're on a {user.get('current_streak', 0)}-day streak! Log a session today.",
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
        users = await db.users.find({
            'weekly_summary': {'$ne': False},
            # Skip users who already received this week's summary
            'last_weekly_summary': {'$ne': week_key}
        }, {'_id': 0, 'id': 1, 'email': 1, 'username': 1}).to_list(1000)
        
        sent_count = 0
        for user in users:
            # Query by date field (YYYY-MM-DD format) - dates are stored in Eastern Time
            sessions = await db.daily_sessions.find({
                'user_id': user['id'],
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
            
            html = get_weekly_summary_html(user.get('username', 'User'), stats)
            
            try:
                await asyncio.to_thread(resend.Emails.send, {
                    "from": SENDER_EMAIL,
                    "to": [user['email']],
                    "subject": "📊 Your Weekly Summary - Edge Mode",
                    "html": html
                })
                
                # Mark user as having received this week's summary
                await db.users.update_one(
                    {'id': user['id']},
                    {'$set': {'last_weekly_summary': week_key}}
                )
                
                sent_count += 1
            except Exception as e:
                logger.error(f"Failed to send weekly summary to {user['email']}: {e}")
        
        logger.info(f"Weekly summary job complete. Sent {sent_count} emails.")
    except Exception as e:
        logger.error(f"Weekly summary job failed: {e}")


async def send_inactive_reminders_job():
    """Send reminder emails to users who haven't logged in 2+ days"""
    if not RESEND_API_KEY:
        logger.warning("RESEND_API_KEY not set, skipping inactive reminders")
        return
    
    logger.info("Running inactive user reminder job...")
    now = datetime.now(timezone.utc)
    two_days_ago = (now - timedelta(days=2)).date().isoformat()
    
    try:
        # Only send to trial users OR users who opted in to reminders
        # Exclude admin users and paid subscribers who haven't explicitly opted in
        users = await db.users.find({
            'streak_reminders': {'$ne': False},
            'is_admin': {'$ne': True}  # Don't send to admins
        }, {'_id': 0, 'id': 1, 'email': 1, 'username': 1, 'last_log_date': 1, 'is_trial': 1, 'subscription_active': 1}).to_list(1000)
        
        sent_count = 0
        for user in users:
            last_log = user.get('last_log_date')
            
            # Skip if no last_log_date recorded
            if not last_log:
                continue
            
            # Check if user is inactive
            if last_log <= two_days_ago:
                last_log_date = datetime.fromisoformat(last_log).date()
                days_inactive = (now.date() - last_log_date).days
                
                # Only send if 2-7 days inactive
                if 2 <= days_inactive <= 7:
                    html = get_inactive_reminder_html(
                        user.get('username', 'User'),
                        days_inactive
                    )
                    
                    # Send email
                    try:
                        await asyncio.to_thread(resend.Emails.send, {
                            "from": SENDER_EMAIL,
                            "to": [user['email']],
                            "subject": "👋 We Miss You! - Edge Mode",
                            "html": html
                        })
                        sent_count += 1
                    except Exception as e:
                        logger.error(f"Failed to send inactive reminder to {user['email']}: {e}")
                    
                    # Send push notification
                    if user.get('push_enabled'):
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
    "The harder you work today, the easier it gets tomorrow."
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
    
    try:
        # Find users who have opted into morning reminders
        users = await db.users.find({
            'morning_reminders': True,
            'is_admin': {'$ne': True}
        }, {'_id': 0, 'id': 1, 'email': 1, 'username': 1, 'current_streak': 1}).to_list(1000)
        
        sent_count = 0
        for user in users:
            # Get user's pillars
            pillars_docs = await db.user_pillars.find({'user_id': user['id']}, {'_id': 0, 'pillar_name': 1}).to_list(5)
            pillar_names = [p['pillar_name'].split('/')[0] for p in pillars_docs]
            
            # Pick a random motivational quote
            quote = random.choice(MORNING_QUOTES)
            
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
