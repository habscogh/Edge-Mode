"""
Pydantic models/schemas for Edge Mode API
"""
from pydantic import BaseModel, Field, EmailStr, ConfigDict, validator
from typing import List, Optional, Dict


# ============ Auth Models ============
class UserRegister(BaseModel):
    email: EmailStr
    username: str
    password: str
    age: int
    referral_code: Optional[str] = None

    @validator('age')
    def validate_age(cls, v):
        if v < 12 or v > 19:
            raise ValueError('Age must be between 12 and 19')
        return v

    @validator('username')
    def validate_username(cls, v):
        if len(v) < 3:
            raise ValueError('Username must be at least 3 characters')
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class CoachRegister(BaseModel):
    email: EmailStr
    password: str
    name: str
    team_name: str
    special_code: Optional[str] = None


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str


class PasswordChange(BaseModel):
    current_password: str
    new_password: str


class EmailChange(BaseModel):
    new_email: EmailStr
    password: str


# ============ User Models ============
class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    email: str
    username: Optional[str] = None
    name: Optional[str] = None
    age: Optional[int] = None
    join_date: str
    current_streak: int = 0
    longest_streak: int = 0
    subscription_active: bool = False
    trial_ends_at: Optional[str] = None
    is_trial: bool = False
    last_log_date: Optional[str] = None
    leaderboard_opt_in: bool = False
    total_sessions_completed: int = 0
    is_coach: bool = False
    team_id: Optional[str] = None
    joined_via_coach: bool = False
    has_extended_trial: bool = False


class CoachProfile(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    email: str
    name: str
    team_name: str
    team_id: str
    invite_link: str
    special_code: Optional[str] = None
    has_extended_trial: bool = False
    created_at: str


# ============ Pillar Models ============
class UserPillar(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    user_id: str
    pillar_name: str
    weekly_target_sessions: int


class PillarSetup(BaseModel):
    pillar_name: str
    weekly_target_sessions: int


class PillarAdd(BaseModel):
    pillar_name: str
    weekly_target_sessions: int = 3


class PillarUpdate(BaseModel):
    weekly_target_sessions: int


# ============ Onboarding Models ============
class OnboardingComplete(BaseModel):
    pillars: List[PillarSetup]

    @validator('pillars')
    def validate_pillars(cls, v):
        from config import PILLARS
        if len(v) < 3 or len(v) > 5:
            raise ValueError('Must select between 3 and 5 pillars')
        for pillar in v:
            if pillar.pillar_name not in PILLARS:
                raise ValueError(f'Invalid pillar: {pillar.pillar_name}')
        return v


# ============ Session Models ============
class DailySession(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    user_id: str
    pillar: str
    date: str
    timestamp: str
    minutes_spent: int = 0
    note: Optional[str] = None


class SessionComplete(BaseModel):
    pillar: str
    minutes_spent: Optional[int] = 30
    note: Optional[str] = None
    local_date: Optional[str] = None


class DeleteSession(BaseModel):
    session_id: str


class EditSession(BaseModel):
    session_id: str
    minutes_spent: int
    pillar: Optional[str] = None
    note: Optional[str] = None


# ============ Stats Models ============
class WeeklyStats(BaseModel):
    consistency_pct: float
    target_completion_pct: float
    performance_index: float
    total_sessions: int
    total_minutes: int
    days_logged: int
    pillars_data: List[dict]


class DailyComparison(BaseModel):
    today_sessions: int
    yesterday_sessions: int
    today_minutes: int
    yesterday_minutes: int
    improvement_pct: float


class PerformanceHistory(BaseModel):
    dates: List[str]
    scores: List[float]


class WeeklyReview(BaseModel):
    week_start: str
    week_end: str
    improved_pillars: List[dict]
    dropped_pillars: List[dict]
    average_daily_output_change: float
    total_sessions: int
    consistency_pct: float
    performance_index: float


# ============ Group Models ============
class Group(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    name: str
    type: str
    created_by: str
    members: List[str]
    created_at: str
    invite_code: str
    coach_id: Optional[str] = None


class GroupCreate(BaseModel):
    name: str
    type: str = "private"
    is_coach: bool = False


class GroupJoin(BaseModel):
    invite_code: str


class TransferOwnership(BaseModel):
    new_owner_id: str


# ============ Leaderboard Models ============
class LeaderboardEntry(BaseModel):
    username: str
    consistency_pct: float
    performance_index: float
    age_group: str
    improvement_pct: float


# ============ Parent Models ============
class ParentLink(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    student_id: str
    student_username: str
    parent_id: Optional[str] = None
    parent_email: str
    status: str
    invited_at: str
    accepted_at: Optional[str] = None


class ParentInvite(BaseModel):
    parent_email: EmailStr


class ParentAccept(BaseModel):
    invite_code: str


# ============ Challenge Models ============
class Challenge(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    name: str
    description: str
    challenge_type: str
    metric_type: str
    pillar: Optional[str] = None
    start_date: str
    end_date: str
    status: str
    created_at: str
    created_by: str
    participant_count: int = 0


class ChallengeParticipant(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    challenge_id: str
    user_id: str
    username: str
    joined_at: str
    current_score: float = 0
    rank: int = 0


class ChallengeJoin(BaseModel):
    challenge_id: str


class ChallengeCreate(BaseModel):
    name: str
    description: str
    challenge_type: str
    metric_type: str
    pillar: Optional[str] = None


class FriendChallengeCreate(BaseModel):
    friend_email: EmailStr
    name: str
    goal_type: str  # 'sessions', 'minutes', 'consistency'
    goal_value: int  # Target value (e.g., 10 sessions, 300 minutes)
    duration_days: int = 7  # Default 1 week
    pillar: Optional[str] = None  # Optional specific pillar


class FriendChallengeResponse(BaseModel):
    challenge_id: str
    action: str  # 'accept' or 'decline'


# ============ Payment Models ============
class CreateCheckoutRequest(BaseModel):
    origin_url: str
    plan: str = 'monthly'


# ============ Notification Models ============
class EmailSettings(BaseModel):
    streak_reminders: bool = True
    weekly_summary: bool = True
    morning_reminders: bool = False


class NotificationSettingsUpdate(BaseModel):
    streak_reminders: Optional[bool] = None
    weekly_summary: Optional[bool] = None
    morning_reminders: Optional[bool] = None
    morning_reminder_time: Optional[str] = None  # e.g., "08:00"


# ============ Referral Models ============
class EmailInvite(BaseModel):
    friend_email: EmailStr
    friend_name: Optional[str] = None


class PlayerJoinTeam(BaseModel):
    team_code: str
