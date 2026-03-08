"""
Statistics routes for Edge Mode
"""
from fastapi import APIRouter, Depends
from datetime import datetime, timezone, timedelta, date
from typing import Optional

from config import db
from models.schemas import WeeklyStats, DailyComparison, PerformanceHistory, WeeklyReview
from utils.auth import get_current_user
from utils.timezone import get_today_eastern

router = APIRouter(prefix="/stats", tags=["Statistics"])


@router.get("/weekly", response_model=WeeklyStats)
async def get_weekly_stats(current_user: dict = Depends(get_current_user), local_date: str = None):
    user_id = current_user['id']
    if local_date:
        today = date.fromisoformat(local_date)
    else:
        today = get_today_eastern()  # Eastern Time
    week_start = today - timedelta(days=today.weekday())
    
    sessions = await db.daily_sessions.find({
        'user_id': user_id,
        'date': {'$gte': week_start.isoformat()}
    }, {'_id': 0}).to_list(1000)
    
    user_pillars = await db.user_pillars.find({'user_id': user_id}, {'_id': 0}).to_list(100)
    
    unique_days = set(s['date'] for s in sessions)
    days_logged = len(unique_days)
    consistency_pct = (days_logged / 7) * 100
    
    total_sessions = len(sessions)
    total_minutes = sum(s.get('minutes_spent', 30) for s in sessions)
    total_target = sum(p['weekly_target_sessions'] for p in user_pillars)
    target_completion_pct = min((total_sessions / total_target * 100) if total_target > 0 else 0, 100)
    
    performance_index = min((consistency_pct * 0.7) + (target_completion_pct * 0.3), 100)
    
    pillars_data = []
    for pillar in user_pillars:
        pillar_sessions = [s for s in sessions if s['pillar'] == pillar['pillar_name']]
        pillar_count = len(pillar_sessions)
        pillars_data.append({
            'pillar_name': pillar['pillar_name'],
            'sessions_completed': pillar_count,
            'target_sessions': pillar['weekly_target_sessions'],
            'completion_pct': min((pillar_count / pillar['weekly_target_sessions'] * 100) if pillar['weekly_target_sessions'] > 0 else 0, 100)
        })
    
    return WeeklyStats(
        consistency_pct=round(consistency_pct, 1),
        target_completion_pct=round(target_completion_pct, 1),
        performance_index=round(performance_index, 1),
        total_sessions=total_sessions,
        total_minutes=total_minutes,
        days_logged=days_logged,
        pillars_data=pillars_data
    )


@router.get("/comparison", response_model=DailyComparison)
async def get_daily_comparison(current_user: dict = Depends(get_current_user), local_date: str = None):
    user_id = current_user['id']
    if local_date:
        today = date.fromisoformat(local_date)
    else:
        today = get_today_eastern()  # Eastern Time
    yesterday = today - timedelta(days=1)
    
    today_sessions = await db.daily_sessions.find({
        'user_id': user_id,
        'date': today.isoformat()
    }, {'_id': 0}).to_list(100)
    
    yesterday_sessions = await db.daily_sessions.find({
        'user_id': user_id,
        'date': yesterday.isoformat()
    }, {'_id': 0}).to_list(100)
    
    today_count = len(today_sessions)
    yesterday_count = len(yesterday_sessions)
    today_minutes = sum(s.get('minutes_spent', 30) for s in today_sessions)
    yesterday_minutes = sum(s.get('minutes_spent', 30) for s in yesterday_sessions)
    
    improvement_pct = 0
    if yesterday_count > 0:
        improvement_pct = ((today_count - yesterday_count) / yesterday_count) * 100
    elif today_count > 0:
        improvement_pct = 100
    
    return DailyComparison(
        today_sessions=today_count,
        yesterday_sessions=yesterday_count,
        today_minutes=today_minutes,
        yesterday_minutes=yesterday_minutes,
        improvement_pct=round(improvement_pct, 1)
    )


@router.get("/history", response_model=PerformanceHistory)
async def get_performance_history(current_user: dict = Depends(get_current_user), days: int = 30, local_date: str = None):
    user_id = current_user['id']
    if local_date:
        end_date = date.fromisoformat(local_date)
    else:
        end_date = datetime.now(timezone.utc).date()
    start_date = end_date - timedelta(days=days-1)
    
    user_pillars = await db.user_pillars.find({'user_id': user_id}, {'_id': 0}).to_list(100)
    total_target = sum(p['weekly_target_sessions'] for p in user_pillars)
    
    dates = []
    scores = []
    
    for i in range(days):
        current_date = start_date + timedelta(days=i)
        week_start = current_date - timedelta(days=current_date.weekday())
        week_end = week_start + timedelta(days=6)
        
        sessions = await db.daily_sessions.find({
            'user_id': user_id,
            'date': {'$gte': week_start.isoformat(), '$lte': week_end.isoformat()}
        }, {'_id': 0}).to_list(1000)
        
        unique_days = set(s['date'] for s in sessions)
        days_logged = len(unique_days)
        consistency_pct = (days_logged / 7) * 100
        
        total_sessions = len(sessions)
        target_completion_pct = min((total_sessions / total_target * 100) if total_target > 0 else 0, 100)
        
        performance_index = min((consistency_pct * 0.7) + (target_completion_pct * 0.3), 100)
        
        dates.append(current_date.isoformat())
        scores.append(round(performance_index, 1))
    
    return PerformanceHistory(dates=dates, scores=scores)


@router.get("/weekly-review", response_model=WeeklyReview)
async def get_weekly_review(current_user: dict = Depends(get_current_user), local_date: str = None):
    user_id = current_user['id']
    if local_date:
        today = date.fromisoformat(local_date)
    else:
        today = datetime.now(timezone.utc).date()
    current_week_start = today - timedelta(days=today.weekday())
    last_week_start = current_week_start - timedelta(days=7)
    last_week_end = current_week_start - timedelta(days=1)
    
    current_sessions = await db.daily_sessions.find({
        'user_id': user_id,
        'date': {'$gte': current_week_start.isoformat()}
    }, {'_id': 0}).to_list(1000)
    
    last_sessions = await db.daily_sessions.find({
        'user_id': user_id,
        'date': {'$gte': last_week_start.isoformat(), '$lte': last_week_end.isoformat()}
    }, {'_id': 0}).to_list(1000)
    
    user_pillars = await db.user_pillars.find({'user_id': user_id}, {'_id': 0}).to_list(100)
    
    improved_pillars = []
    dropped_pillars = []
    
    for pillar in user_pillars:
        current_count = len([s for s in current_sessions if s['pillar'] == pillar['pillar_name']])
        last_count = len([s for s in last_sessions if s['pillar'] == pillar['pillar_name']])
        change = current_count - last_count
        
        if change > 0:
            improved_pillars.append({
                'pillar_name': pillar['pillar_name'],
                'change': change,
                'current_sessions': current_count
            })
        elif change < 0:
            dropped_pillars.append({
                'pillar_name': pillar['pillar_name'],
                'change': abs(change),
                'current_sessions': current_count
            })
    
    current_daily_avg = len(current_sessions) / max(len(set(s['date'] for s in current_sessions)), 1)
    last_daily_avg = len(last_sessions) / max(len(set(s['date'] for s in last_sessions)), 1)
    avg_change = 0
    if last_daily_avg > 0:
        avg_change = ((current_daily_avg - last_daily_avg) / last_daily_avg) * 100
    
    unique_days = set(s['date'] for s in current_sessions)
    consistency_pct = (len(unique_days) / 7) * 100
    
    total_target = sum(p['weekly_target_sessions'] for p in user_pillars)
    target_completion = min((len(current_sessions) / total_target * 100) if total_target > 0 else 0, 100)
    performance_index = min((consistency_pct * 0.7) + (target_completion * 0.3), 100)
    
    return WeeklyReview(
        week_start=current_week_start.isoformat(),
        week_end=today.isoformat(),
        improved_pillars=improved_pillars,
        dropped_pillars=dropped_pillars,
        average_daily_output_change=round(avg_change, 1),
        total_sessions=len(current_sessions),
        consistency_pct=round(consistency_pct, 1),
        performance_index=round(performance_index, 1)
    )
