"""
Edge Mode API - Main Server
A mobile-first application to help teens systematically improve themselves.
"""
from fastapi import FastAPI, APIRouter
from starlette.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timezone
import asyncio
import os

# Import configuration and database
from config import db, client, logger, RESEND_API_KEY, STRIPE_API_KEY
import resend

# Import all route modules
from routes import (
    auth,
    users,
    sessions,
    stats,
    badges,
    groups,
    leaderboard,
    coach,
    parent,
    challenges,
    payments,
    admin,
    notifications,
    referral,
    onboarding,
    push,
    schools,
    ambassador,
    reflections,
    streak_recovery,
    engagement
)

# Import scheduler jobs
from utils.scheduler_jobs import (
    send_streak_reminders_job,
    send_weekly_summaries_job,
    send_inactive_reminders_job,
    send_trial_ending_reminders_job,
    send_parent_weekly_summaries_job,
    send_parent_inactivity_alerts_job,
    send_morning_reminders_job
)

# Import challenge functions
from routes.challenges import (
    challenges_daily_job,
    seed_initial_challenges,
    finalize_friend_challenges
)

# Initialize Resend
if RESEND_API_KEY:
    resend.api_key = RESEND_API_KEY

# Initialize FastAPI app
app = FastAPI(
    title="Edge Mode API",
    description="API for the Edge Mode self-improvement app",
    version="2.0.0"
)

# Initialize scheduler
scheduler = AsyncIOScheduler()

# Create main API router with /api prefix
api_router = APIRouter(prefix="/api")

# Include all route modules
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(sessions.router)
api_router.include_router(stats.router)
api_router.include_router(badges.router)
api_router.include_router(groups.router)
api_router.include_router(leaderboard.router)
api_router.include_router(coach.router)
api_router.include_router(parent.router)
api_router.include_router(challenges.router)
api_router.include_router(payments.router)
api_router.include_router(payments.webhook_router)  # Webhook at /api/webhook/stripe
api_router.include_router(admin.router)
api_router.include_router(admin.public_router)  # Public platform stats endpoint
api_router.include_router(notifications.router)
api_router.include_router(referral.router)
api_router.include_router(onboarding.router)
api_router.include_router(push.router)  # Push notifications
api_router.include_router(schools.router)  # School search and leaderboard
api_router.include_router(ambassador.router)  # Founding Ambassador program
api_router.include_router(reflections.router)  # Daily reflections & growth journal
api_router.include_router(streak_recovery.router)  # Streak recovery feature
api_router.include_router(engagement.router)  # XP, Levels, Daily Rewards, Friend Streaks


# Health check endpoints
@api_router.get("/health")
async def health_check():
    """Health check endpoint for deployment"""
    try:
        await asyncio.wait_for(client.admin.command('ping'), timeout=5.0)
        return {"status": "healthy", "database": "connected", "scheduler": scheduler.running}
    except asyncio.TimeoutError:
        logger.warning("Health check: Database ping timed out")
        return {"status": "degraded", "database": "timeout", "scheduler": scheduler.running}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}


@api_router.get("/scheduler/status")
async def get_scheduler_status():
    """Get the status of the email scheduler"""
    from utils.auth import get_current_user
    from fastapi import Depends
    
    jobs = scheduler.get_jobs()
    job_info = []
    for job in jobs:
        job_info.append({
            'id': job.id,
            'next_run': job.next_run_time.isoformat() if job.next_run_time else None
        })
    
    return {
        'scheduler_running': scheduler.running,
        'jobs': job_info,
        'schedule': {
            'morning_reminders': '1:00 PM UTC daily (8:00 AM Eastern)',
            'streak_reminders': '8:00 PM UTC daily (3:00 PM Eastern)',
            'inactive_reminders': '6:00 PM UTC daily (2:00 PM Eastern) - for 3-7 days inactive',
            'trial_ending_reminders': '4:00 PM UTC daily (12:00 PM Eastern) - for users with 1-3 days left',
            'weekly_summary': 'Sunday 2:00 PM UTC (10:00 AM Eastern)',
            'parent_weekly_summaries': 'Sunday 3:00 PM UTC (11:00 AM Eastern)',
            'parent_inactivity_alerts': '7:00 PM UTC daily (3:00 PM Eastern)',
            'challenges_daily': '12:05 AM UTC daily'
        }
    }


# Include the API router
app.include_router(api_router)


# Root health check - always returns ok for load balancer
@app.get("/health")
async def root_health_check():
    """Root health check endpoint - always returns ok for load balancer"""
    return {"status": "ok"}


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_scheduler():
    """Start the scheduler when app starts - only if we're the primary worker"""
    import os
    
    # Only start scheduler in the main process to prevent duplicate jobs
    # Check if we're running with multiple workers
    worker_id = os.environ.get('APP_WORKER_ID', '0')
    if worker_id != '0':
        logger.info(f"Worker {worker_id}: Skipping scheduler start (handled by worker 0)")
        return
    
    # Use a database lock to ensure only one scheduler runs across all instances
    lock_doc = await db.scheduler_locks.find_one({'_id': 'streak_scheduler'})
    now = datetime.now(timezone.utc)
    
    # If lock exists and was updated in the last 5 minutes, another instance is running
    if lock_doc and lock_doc.get('updated_at'):
        lock_time = datetime.fromisoformat(lock_doc['updated_at'].replace('Z', '+00:00'))
        if (now - lock_time).total_seconds() < 300:  # 5 minutes
            logger.info("Scheduler lock held by another instance, skipping")
            return
    
    # Acquire the lock
    await db.scheduler_locks.update_one(
        {'_id': 'streak_scheduler'},
        {'$set': {'updated_at': now.isoformat(), 'instance': os.getpid()}},
        upsert=True
    )
    logger.info(f"Acquired scheduler lock for PID {os.getpid()}")
    
    # Seed initial challenges if none exist
    try:
        active_challenges = await db.challenges.count_documents({'status': 'active'})
        if active_challenges == 0:
            logger.info("No active challenges found - seeding initial challenges...")
            await seed_initial_challenges()
    except Exception as e:
        logger.error(f"Failed to seed initial challenges: {e}")
    
    # Streak reminders - daily at 8 PM UTC (3 PM Eastern)
    scheduler.add_job(
        send_streak_reminders_job,
        CronTrigger(hour=20, minute=0),
        id="streak_reminders",
        replace_existing=True
    )
    
    # Weekly summaries - every Sunday at 2 PM UTC (10 AM Eastern)
    scheduler.add_job(
        send_weekly_summaries_job,
        CronTrigger(day_of_week='sun', hour=14, minute=0),
        id="weekly_summaries",
        replace_existing=True
    )
    
    # Inactive user reminders - daily at 6 PM UTC (2 PM Eastern)
    scheduler.add_job(
        send_inactive_reminders_job,
        CronTrigger(hour=18, minute=0),
        id="inactive_reminders",
        replace_existing=True
    )
    
    # Trial ending reminders - daily at 4 PM UTC (12 PM Eastern)
    scheduler.add_job(
        send_trial_ending_reminders_job,
        CronTrigger(hour=16, minute=0),
        id="trial_ending_reminders",
        replace_existing=True
    )
    
    # Parent weekly summaries - every Sunday at 3 PM UTC (11 AM Eastern)
    scheduler.add_job(
        send_parent_weekly_summaries_job,
        CronTrigger(day_of_week='sun', hour=15, minute=0),
        id="parent_weekly_summaries",
        replace_existing=True
    )
    
    # Parent inactivity alerts - daily at 7 PM UTC (3 PM Eastern)
    scheduler.add_job(
        send_parent_inactivity_alerts_job,
        CronTrigger(hour=19, minute=0),
        id="parent_inactivity_alerts",
        replace_existing=True
    )
    
    # Challenges daily job - at 12:05 AM UTC to create new challenges and finalize old ones
    scheduler.add_job(
        challenges_daily_job,
        CronTrigger(hour=0, minute=5),
        id="challenges_daily",
        replace_existing=True
    )
    
    # Morning reminders - daily at 1 PM UTC (8 AM Eastern, 9 AM Central)
    scheduler.add_job(
        send_morning_reminders_job,
        CronTrigger(hour=13, minute=0),
        id="morning_reminders",
        replace_existing=True
    )
    
    # Finalize friend challenges - daily at 12:10 AM UTC
    scheduler.add_job(
        finalize_friend_challenges,
        CronTrigger(hour=0, minute=10),
        id="friend_challenges",
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("Email scheduler started - Morning: 1PM UTC (8AM Eastern), Streak: 8PM UTC, Inactive: 6PM UTC, Trial Ending: 4PM UTC, Weekly: Sun 2PM UTC, Parent Weekly: Sun 3PM UTC, Parent Alerts: 7PM UTC, Challenges: 12:05AM UTC, Friend Challenges: 12:10AM UTC")


@app.on_event("shutdown")
async def shutdown_db_client():
    scheduler.shutdown()
    client.close()
