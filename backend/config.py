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
# Try STRIPE_SECRET_KEY first (Emergent platform standard), then STRIPE_API_KEY
_stripe_secret = os.environ.get('STRIPE_SECRET_KEY')
_stripe_api = os.environ.get('STRIPE_API_KEY')

# Prefer live keys over test keys
if _stripe_secret and _stripe_secret.startswith('sk_live_'):
    STRIPE_API_KEY = _stripe_secret
elif _stripe_api and _stripe_api.startswith('sk_live_'):
    STRIPE_API_KEY = _stripe_api
elif _stripe_secret:
    STRIPE_API_KEY = _stripe_secret
elif _stripe_api:
    STRIPE_API_KEY = _stripe_api
else:
    STRIPE_API_KEY = None

# Log Stripe key status (without exposing the key)
_stripe_status = f"Stripe: {'live' if STRIPE_API_KEY and STRIPE_API_KEY.startswith('sk_live_') else 'test' if STRIPE_API_KEY else 'not configured'} mode"

# Push Notification Configuration (VAPID)
VAPID_PUBLIC_KEY = os.environ.get('VAPID_PUBLIC_KEY')
VAPID_PRIVATE_KEY = os.environ.get('VAPID_PRIVATE_KEY')
VAPID_CLAIMS_EMAIL = os.environ.get('VAPID_CLAIMS_EMAIL', 'admin@edgemodeapp.com')

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
    "streak_21": {
        "id": "streak_21",
        "name": "Three Week Titan",
        "description": "Maintain a 21-day streak",
        "icon": "🔥",
        "category": "streak"
    },
    "streak_45": {
        "id": "streak_45",
        "name": "Six Week Superstar",
        "description": "Maintain a 45-day streak",
        "icon": "🔥",
        "category": "streak"
    },
    "streak_120": {
        "id": "streak_120",
        "name": "Four Month Legend",
        "description": "Maintain a 120-day streak",
        "icon": "👑",
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
    },
    "silver_medal": {
        "id": "silver_medal",
        "name": "Silver Medal",
        "description": "Finish 2nd in a challenge",
        "icon": "🥈",
        "category": "challenge"
    },
    "bronze_medal": {
        "id": "bronze_medal",
        "name": "Bronze Medal",
        "description": "Finish 3rd in a challenge",
        "icon": "🥉",
        "category": "challenge"
    },
    # Long-term Streak Badges
    "streak_60": {
        "id": "streak_60",
        "name": "Two Month Titan",
        "description": "Maintain a 60-day streak",
        "icon": "🔥",
        "category": "streak"
    },
    "streak_90": {
        "id": "streak_90",
        "name": "Quarter Master",
        "description": "Maintain a 90-day streak",
        "icon": "🔥",
        "category": "streak"
    },
    "streak_180": {
        "id": "streak_180",
        "name": "Half Year Hero",
        "description": "Maintain a 180-day streak",
        "icon": "⚡",
        "category": "streak"
    },
    "streak_365": {
        "id": "streak_365",
        "name": "Year One Legend",
        "description": "Maintain a full year streak",
        "icon": "👑",
        "category": "streak"
    },
    # Long-term Session Milestones
    "sessions_250": {
        "id": "sessions_250",
        "name": "Quarter Thousand",
        "description": "Complete 250 sessions",
        "icon": "💎",
        "category": "milestone"
    },
    "sessions_500": {
        "id": "sessions_500",
        "name": "Half Thousand",
        "description": "Complete 500 sessions",
        "icon": "🚀",
        "category": "milestone"
    },
    "sessions_1000": {
        "id": "sessions_1000",
        "name": "Thousand Club Elite",
        "description": "Complete 1,000 sessions",
        "icon": "👑",
        "category": "milestone"
    },
    # Long-term Hours Milestones
    "hours_100": {
        "id": "hours_100",
        "name": "100 Hour Club",
        "description": "Log 100+ hours total",
        "icon": "⏱️",
        "category": "milestone"
    },
    "hours_250": {
        "id": "hours_250",
        "name": "250 Hour Grinder",
        "description": "Log 250+ hours total",
        "icon": "💪",
        "category": "milestone"
    },
    "hours_500": {
        "id": "hours_500",
        "name": "500 Hour Warrior",
        "description": "Log 500+ hours total",
        "icon": "🦾",
        "category": "milestone"
    },
    "hours_1000": {
        "id": "hours_1000",
        "name": "1000 Hour Master",
        "description": "Log 1,000+ hours total",
        "icon": "🏛️",
        "category": "milestone"
    },
    # Consistency Milestones
    "perfect_month": {
        "id": "perfect_month",
        "name": "Perfect Month",
        "description": "Log every day for a full month",
        "icon": "📅",
        "category": "consistency"
    },
    "perfect_quarter": {
        "id": "perfect_quarter",
        "name": "Perfect Quarter",
        "description": "Log every day for 3 months straight",
        "icon": "🗓️",
        "category": "consistency"
    },
    # Challenge Mastery
    "challenge_streak_5": {
        "id": "challenge_streak_5",
        "name": "Challenge Dominator",
        "description": "Win 5 challenges",
        "icon": "🏆",
        "category": "challenge"
    },
    "challenge_streak_10": {
        "id": "challenge_streak_10",
        "name": "Challenge Legend",
        "description": "Win 10 challenges",
        "icon": "👑",
        "category": "challenge"
    },
    # Referral Badges
    "referral_5": {
        "id": "referral_5",
        "name": "Friend Magnet",
        "description": "Refer 5 friends to Edge Mode",
        "icon": "🤝",
        "category": "social"
    },
    "referral_10": {
        "id": "referral_10",
        "name": "Community Builder",
        "description": "Refer 10 friends to Edge Mode",
        "icon": "👥",
        "category": "social"
    },
    # Special Long-term
    "og_member": {
        "id": "og_member",
        "name": "OG Member",
        "description": "Active member for 6+ months",
        "icon": "🎖️",
        "category": "special"
    },
    "founding_year": {
        "id": "founding_year",
        "name": "Founding Year",
        "description": "Active member for 1+ year",
        "icon": "⭐",
        "category": "special"
    },
    # Friend Challenges
    "friend_challenger": {
        "id": "friend_challenger",
        "name": "Friend Challenger",
        "description": "Complete your first 1v1 friend challenge",
        "icon": "🤝",
        "category": "social"
    },
    "friend_wins_3": {
        "id": "friend_wins_3",
        "name": "Friendly Rival",
        "description": "Win 3 friend challenges",
        "icon": "🏅",
        "category": "social"
    },
    "friend_wins_10": {
        "id": "friend_wins_10",
        "name": "Champion Friend",
        "description": "Win 10 friend challenges",
        "icon": "🏆",
        "category": "social"
    }
}

# ============ XP & Leveling System ============
# XP rewards for various actions
XP_REWARDS = {
    'daily_login': 10,
    'log_session': 25,
    'streak_day': 5,  # Bonus per streak day
    'earn_badge': 50,
    'complete_challenge': 100,
    'win_friend_challenge': 75,
    'first_session_of_day': 15,
    'weekly_target_met': 50,
}

# Level thresholds (cumulative XP needed for each level)
LEVEL_THRESHOLDS = [
    0,      # Level 1
    100,    # Level 2
    250,    # Level 3
    500,    # Level 4
    800,    # Level 5
    1200,   # Level 6
    1700,   # Level 7
    2300,   # Level 8
    3000,   # Level 9
    4000,   # Level 10
    5200,   # Level 11
    6600,   # Level 12
    8200,   # Level 13
    10000,  # Level 14
    12500,  # Level 15
    15500,  # Level 16
    19000,  # Level 17
    23000,  # Level 18
    27500,  # Level 19
    32500,  # Level 20
    40000,  # Level 21+
]

LEVEL_TITLES = {
    1: "Rookie",
    5: "Rising Star",
    10: "Achiever",
    15: "Champion",
    20: "Legend",
    25: "Elite",
}

# Daily login streak bonuses (coins) - adjusted for balanced economy
LOGIN_STREAK_BONUSES = {
    1: 1,    # Day 1
    2: 1,    # Day 2
    3: 2,    # Day 3
    4: 2,    # Day 4
    5: 3,    # Day 5
    6: 3,    # Day 6
    7: 5,    # Day 7 (weekly bonus!)
}


# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
