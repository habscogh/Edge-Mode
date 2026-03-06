"""
Configuration and shared dependencies for Edge Mode backend
"""
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from pathlib import Path
import os
import logging

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB Configuration
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(
    mongo_url,
    serverSelectionTimeoutMS=30000,
    connectTimeoutMS=20000,
    socketTimeoutMS=20000,
    retryWrites=True,
    retryReads=True
)
db = client[os.environ['DB_NAME']]

# JWT Configuration
JWT_SECRET = os.environ.get('JWT_SECRET', 'forge-secret-key-change-in-production')
JWT_ALGORITHM = 'HS256'

# Email Configuration
RESEND_API_KEY = os.environ.get('RESEND_API_KEY')
SENDER_EMAIL = os.environ.get('SENDER_EMAIL', 'noreply@edgemodeapp.com')

# Stripe Configuration
STRIPE_API_KEY = os.environ.get('STRIPE_API_KEY')

# Admin Configuration
ADMIN_EMAILS = ['admin@edgemodeapp.com']

# Subscription Prices
SUBSCRIPTION_PRICES = {
    'monthly': 4.99,
    'yearly': 49.99
}

# Valid Coach Special Codes
VALID_COACH_CODES = {'EDGE30', 'COACH2024', 'TEAMEDGE', 'PROMO30'}

# Available Pillars
PILLARS = [
    "Fitness/Training",
    "Sports Practice",
    "Study/Academics",
    "Skill Development",
    "Reading/Learning",
    "Personal Project",
    "Discipline Habits"
]

# Badge Definitions
BADGES = {
    "first_session": {
        "id": "first_session",
        "name": "First Step",
        "description": "Log your first session",
        "icon": "🏆",
        "category": "milestone"
    },
    "streak_7": {
        "id": "streak_7",
        "name": "Week Warrior",
        "description": "Maintain a 7-day streak",
        "icon": "🔥",
        "category": "streak"
    },
    "streak_14": {
        "id": "streak_14",
        "name": "Fortnight Fighter",
        "description": "Maintain a 14-day streak",
        "icon": "🔥",
        "category": "streak"
    },
    "streak_30": {
        "id": "streak_30",
        "name": "Monthly Master",
        "description": "Maintain a 30-day streak",
        "icon": "🔥",
        "category": "streak"
    },
    "sessions_100": {
        "id": "sessions_100",
        "name": "Century Club",
        "description": "Complete 100 sessions",
        "icon": "💯",
        "category": "milestone"
    },
    "hours_50": {
        "id": "hours_50",
        "name": "50 Hour Club",
        "description": "Log 50+ hours total",
        "icon": "⏱️",
        "category": "milestone"
    },
    "perfect_week": {
        "id": "perfect_week",
        "name": "Perfect Week",
        "description": "Log every day for a week",
        "icon": "✨",
        "category": "consistency"
    },
    "pillar_master": {
        "id": "pillar_master",
        "name": "Pillar Master",
        "description": "Hit target on all pillars in a week",
        "icon": "🎯",
        "category": "mastery"
    },
    "weekly_champion": {
        "id": "weekly_champion",
        "name": "Weekly Champion",
        "description": "Win a weekly challenge",
        "icon": "🏅",
        "category": "challenge"
    },
    "monthly_champion": {
        "id": "monthly_champion",
        "name": "Monthly Champion",
        "description": "Win a monthly challenge",
        "icon": "🥇",
        "category": "challenge"
    },
    "challenge_streak_3": {
        "id": "challenge_streak_3",
        "name": "Challenge Streak",
        "description": "Win 3 challenges",
        "icon": "🏆",
        "category": "challenge"
    },
    "podium_finish": {
        "id": "podium_finish",
        "name": "Podium Finish",
        "description": "Finish in top 3 of a challenge",
        "icon": "🎖️",
        "category": "challenge"
    }
}

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
