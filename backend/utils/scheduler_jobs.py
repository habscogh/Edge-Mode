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
    now = datetime.now(timezone.utc)
    week_start = (now - timedelta(days=7)).isoformat()
    
    try:
        users = await db.users.find({
            'weekly_summary': {'$ne': False}
        }, {'_id': 0, 'id': 1, 'email': 1, 'username': 1}).to_list(1000)
        
        sent_count = 0
        for user in users:
            sessions = await db.daily_sessions.find({
                'user_id': user['id'],
                'timestamp': {'$gte': week_start}
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
            
            html = get_weekly_summary_html(user.get('username', 'User'), stats)
            
            try:
                await asyncio.to_thread(resend.Emails.send, {
                    "from": SENDER_EMAIL,
                    "to": [user['email']],
                    "subject": "📊 Your Weekly Summary - Edge Mode",
                    "html": html
                })
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
        users = await db.users.find({
            'streak_reminders': {'$ne': False}
        }, {'_id': 0, 'id': 1, 'email': 1, 'username': 1, 'last_log_date': 1}).to_list(1000)
        
        sent_count = 0
        for user in users:
            last_log = user.get('last_log_date')
            
            if last_log and last_log <= two_days_ago:
                last_log_date = datetime.fromisoformat(last_log).date()
                days_inactive = (now.date() - last_log_date).days
                
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
        # Exclude paid subscribers (is_trial=False means they paid)
        users = await db.users.find({
            'is_trial': True,
            'trial_ends_at': {'$exists': True},
            'streak_reminders': {'$ne': False},
            '$or': [
                {'subscription_active': {'$exists': False}},
                {'subscription_active': True}  # Trial users have subscription_active=True during trial
            ]
        }, {'_id': 0}).to_list(1000)
        
        sent_count = 0
        for user in users:
            # Double-check: skip if user has paid (is_trial should be False for paid users)
            if user.get('is_trial') == False:
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
    """Send weekly progress summaries to all parents (runs every Sunday)"""
    if not RESEND_API_KEY:
        logger.warning("RESEND_API_KEY not set, skipping parent weekly summaries")
        return
    
    logger.info("Running parent weekly summary job...")
    
    try:
        parent_links = await db.parent_links.find({'status': 'active'}).to_list(1000)
        
        parents_students = {}
        for link in parent_links:
            parent_id = link['parent_id']
            if parent_id not in parents_students:
                parents_students[parent_id] = []
            parents_students[parent_id].append(link['student_id'])
        
        sent_count = 0
        today = datetime.now(timezone.utc).date()
        week_start = today - timedelta(days=7)
        
        for parent_id, student_ids in parents_students.items():
            parent = await db.users.find_one({'id': parent_id}, {'_id': 0})
            if not parent:
                continue
            
            students_html = ""
            for student_id in student_ids:
                student = await db.users.find_one({'id': student_id}, {'_id': 0, 'password': 0})
                if not student:
                    continue
                
                sessions = await db.daily_sessions.find({
                    'user_id': student_id,
                    'date': {'$gte': week_start.isoformat()}
                }).to_list(100)
                
                unique_days = len(set(s['date'] for s in sessions))
                total_minutes = sum(s.get('minutes_spent', 30) for s in sessions)
                consistency_pct = round((unique_days / 7) * 100, 1)
                
                streak_color = "#f97316" if student.get('current_streak', 0) >= 7 else "#10b981"
                
                students_html += f"""
                <div style="padding: 15px; background: #27272a; border-radius: 8px; margin: 10px 0;">
                    <div style="font-size: 18px; font-weight: bold; color: white; margin-bottom: 10px;">{student.get('username', 'Student')}</div>
                    <div style="display: flex; justify-content: space-between; flex-wrap: wrap;">
                        <div style="text-align: center; padding: 10px; flex: 1; min-width: 80px;">
                            <div style="font-size: 24px; font-weight: bold; color: {streak_color};">🔥 {student.get('current_streak', 0)}</div>
                            <div style="color: #71717a; font-size: 11px;">Day Streak</div>
                        </div>
                        <div style="text-align: center; padding: 10px; flex: 1; min-width: 80px;">
                            <div style="font-size: 24px; font-weight: bold; color: #10b981;">{len(sessions)}</div>
                            <div style="color: #71717a; font-size: 11px;">Sessions</div>
                        </div>
                        <div style="text-align: center; padding: 10px; flex: 1; min-width: 80px;">
                            <div style="font-size: 24px; font-weight: bold; color: white;">{consistency_pct}%</div>
                            <div style="color: #71717a; font-size: 11px;">Consistency</div>
                        </div>
                        <div style="text-align: center; padding: 10px; flex: 1; min-width: 80px;">
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
                </div>
            </div>
            """
            
            try:
                await asyncio.to_thread(resend.Emails.send, {
                    "from": SENDER_EMAIL,
                    "to": [parent['email']],
                    "subject": "📊 Your Child's Weekly Progress Report - Edge Mode",
                    "html": html
                })
                sent_count += 1
            except Exception as e:
                logger.error(f"Failed to send weekly summary to parent {parent['email']}: {e}")
        
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
        now = datetime.now(timezone.utc)
        three_days_ago = (now - timedelta(days=3)).date().isoformat()
        
        parent_links = await db.parent_links.find({'status': 'active'}).to_list(1000)
        
        sent_count = 0
        alerted_pairs = set()
        
        for link in parent_links:
            student_id = link['student_id']
            parent_id = link['parent_id']
            pair_key = f"{parent_id}_{student_id}"
            
            if pair_key in alerted_pairs:
                continue
            
            student = await db.users.find_one({'id': student_id}, {'_id': 0, 'password': 0})
            if not student:
                continue
            
            last_log = student.get('last_log_date')
            
            if last_log and last_log <= three_days_ago:
                last_log_date = datetime.fromisoformat(last_log).date()
                days_inactive = (now.date() - last_log_date).days
                
                if 3 <= days_inactive <= 7:
                    parent = await db.users.find_one({'id': parent_id}, {'_id': 0})
                    if not parent:
                        continue
                    
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
                        </div>
                    </div>
                    """
                    
                    try:
                        await asyncio.to_thread(resend.Emails.send, {
                            "from": SENDER_EMAIL,
                            "to": [parent['email']],
                            "subject": f"⚠️ {student.get('username', 'Your student')} hasn't logged in for {days_inactive} days",
                            "html": html
                        })
                        sent_count += 1
                        alerted_pairs.add(pair_key)
                    except Exception as e:
                        logger.error(f"Failed to send inactivity alert to parent {parent['email']}: {e}")
        
        logger.info(f"Parent inactivity alert job complete. Sent {sent_count} emails.")
    except Exception as e:
        logger.error(f"Parent inactivity alert job failed: {e}")
