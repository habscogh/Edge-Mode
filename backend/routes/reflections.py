"""
Daily Reflections & Growth Journal routes for Edge Mode
"""
from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timezone, timedelta
from typing import Optional, List
import uuid
import random

from config import db
from utils.auth import get_current_user
from utils.timezone import get_today_string, get_today_eastern
from pydantic import BaseModel

router = APIRouter(prefix="/reflections", tags=["Reflections"])

# Reflection prompts - rotated daily
REFLECTION_PROMPTS = [
    "What did you learn today?",
    "How do you feel after this session?",
    "What's one thing you're proud of today?",
    "What will you do differently tomorrow?",
    "What motivated you to show up today?",
    "What was the hardest part? How did you push through?",
    "What's your next goal?",
    "How are you better than yesterday?",
    "What would you tell your past self about today?",
    "What small win are you celebrating?",
    "What habit is becoming easier?",
    "Who or what inspired you today?",
    "What did you discover about yourself?",
    "How did you stay focused?",
    "What are you grateful for right now?",
]


class ReflectionCreate(BaseModel):
    prompt: str
    response: str
    session_id: Optional[str] = None
    mood: Optional[str] = None  # Optional mood: "great", "good", "okay", "tough"


class ReflectionResponse(BaseModel):
    id: str
    user_id: str
    prompt: str
    response: str
    session_id: Optional[str] = None
    mood: Optional[str] = None
    created_at: str
    date: str


@router.get("/prompt")
async def get_daily_prompt(current_user: dict = Depends(get_current_user)):
    """Get today's reflection prompt - consistent per day for each user"""
    today = datetime.now(timezone.utc).date()
    # Use user_id + date as seed for consistent daily prompt per user
    seed = hash(f"{current_user['id']}-{today.isoformat()}")
    random.seed(seed)
    prompt = random.choice(REFLECTION_PROMPTS)
    random.seed()  # Reset seed
    
    return {"prompt": prompt, "date": today.isoformat()}


@router.post("/")
async def create_reflection(
    reflection_data: ReflectionCreate,
    current_user: dict = Depends(get_current_user)
):
    """Save a new reflection"""
    now = datetime.now(timezone.utc)
    today = now.date().isoformat()
    
    reflection_doc = {
        'id': str(uuid.uuid4()),
        'user_id': current_user['id'],
        'prompt': reflection_data.prompt,
        'response': reflection_data.response,
        'session_id': reflection_data.session_id,
        'mood': reflection_data.mood,
        'created_at': now.isoformat(),
        'date': today
    }
    
    await db.reflections.insert_one(reflection_doc)
    
    # Update user's reflection streak
    await update_reflection_streak(current_user['id'], today)
    
    return ReflectionResponse(**{k: v for k, v in reflection_doc.items() if k != '_id'})


async def update_reflection_streak(user_id: str, today: str):
    """Update the user's reflection streak"""
    user = await db.users.find_one({'id': user_id}, {'_id': 0})
    if not user:
        return
    
    yesterday = (datetime.fromisoformat(today) - timedelta(days=1)).date().isoformat()
    last_reflection_date = user.get('last_reflection_date')
    current_reflection_streak = user.get('reflection_streak', 0)
    
    if last_reflection_date == today:
        # Already reflected today
        return
    elif last_reflection_date == yesterday:
        # Continuing streak
        new_streak = current_reflection_streak + 1
    else:
        # Streak broken or first reflection
        new_streak = 1
    
    longest_reflection_streak = max(user.get('longest_reflection_streak', 0), new_streak)
    
    await db.users.update_one(
        {'id': user_id},
        {'$set': {
            'last_reflection_date': today,
            'reflection_streak': new_streak,
            'longest_reflection_streak': longest_reflection_streak
        }}
    )


@router.get("/")
async def get_reflections(
    current_user: dict = Depends(get_current_user),
    limit: int = 30,
    offset: int = 0
):
    """Get user's reflection history (paginated)"""
    reflections = await db.reflections.find(
        {'user_id': current_user['id']},
        {'_id': 0}
    ).sort('created_at', -1).skip(offset).limit(limit).to_list(limit)
    
    total = await db.reflections.count_documents({'user_id': current_user['id']})
    
    return {
        "reflections": reflections,
        "total": total,
        "has_more": offset + len(reflections) < total
    }


@router.get("/stats")
async def get_reflection_stats(current_user: dict = Depends(get_current_user)):
    """Get user's reflection statistics"""
    user = await db.users.find_one({'id': current_user['id']}, {'_id': 0})
    total_reflections = await db.reflections.count_documents({'user_id': current_user['id']})
    
    # Get mood distribution
    mood_pipeline = [
        {'$match': {'user_id': current_user['id'], 'mood': {'$ne': None}}},
        {'$group': {'_id': '$mood', 'count': {'$sum': 1}}}
    ]
    mood_results = await db.reflections.aggregate(mood_pipeline).to_list(10)
    mood_distribution = {item['_id']: item['count'] for item in mood_results}
    
    # Get reflections per week (last 4 weeks)
    four_weeks_ago = (datetime.now(timezone.utc) - timedelta(weeks=4)).date().isoformat()
    recent_reflections = await db.reflections.count_documents({
        'user_id': current_user['id'],
        'date': {'$gte': four_weeks_ago}
    })
    
    return {
        "total_reflections": total_reflections,
        "current_streak": user.get('reflection_streak', 0),
        "longest_streak": user.get('longest_reflection_streak', 0),
        "mood_distribution": mood_distribution,
        "reflections_last_4_weeks": recent_reflections
    }


@router.get("/today")
async def get_today_reflection(current_user: dict = Depends(get_current_user)):
    """Check if user has reflected today"""
    today = datetime.now(timezone.utc).date().isoformat()
    
    reflection = await db.reflections.find_one(
        {'user_id': current_user['id'], 'date': today},
        {'_id': 0}
    )
    
    return {
        "has_reflected_today": reflection is not None,
        "reflection": reflection
    }
