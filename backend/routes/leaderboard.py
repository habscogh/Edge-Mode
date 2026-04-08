"""
Leaderboard routes for Edge Mode
"""
from fastapi import APIRouter
from datetime import datetime, timezone, timedelta
from typing import Optional

from config import db

router = APIRouter(prefix="/leaderboard", tags=["Leaderboard"])


@router.get("/global")
async def get_global_leaderboard(age_group: Optional[str] = None):
    query = {'leaderboard_opt_in': True}
    
    if age_group:
        age_ranges = {
            '12-14': (12, 14),
            '15-17': (15, 17),
            '18-19': (18, 19)
        }
        if age_group in age_ranges:
            min_age, max_age = age_ranges[age_group]
            query['age'] = {'$gte': min_age, '$lte': max_age}
    
    users = await db.users.find(query, {'_id': 0, 'password': 0}).to_list(1000)
    user_ids = [user['id'] for user in users]
    
    if not user_ids:
        return []
    
    today = datetime.now(timezone.utc).date()
    week_start = today - timedelta(days=today.weekday())
    last_week_start = week_start - timedelta(days=7)
    last_week_end = week_start - timedelta(days=1)
    
    all_current_sessions = await db.daily_sessions.find({
        'user_id': {'$in': user_ids},
        'date': {'$gte': week_start.isoformat()}
    }, {'_id': 0}).to_list(10000)
    
    all_last_sessions = await db.daily_sessions.find({
        'user_id': {'$in': user_ids},
        'date': {'$gte': last_week_start.isoformat(), '$lte': last_week_end.isoformat()}
    }, {'_id': 0}).to_list(10000)
    
    all_pillars = await db.user_pillars.find({'user_id': {'$in': user_ids}}, {'_id': 0}).to_list(5000)
    
    # Fetch display badges for all users
    display_badges = {}
    for user in users:
        if user.get('display_badge'):
            inv_item = await db.user_inventory.find_one({
                'user_id': user['id'],
                'id': user['display_badge']
            }, {'_id': 0, 'item_id': 1})
            if inv_item:
                shop_item = await db.shop_items.find_one({'id': inv_item['item_id']}, {'_id': 0, 'icon': 1, 'name': 1})
                if shop_item:
                    display_badges[user['id']] = {
                        'icon': shop_item['icon'],
                        'name': shop_item['name']
                    }
    
    current_sessions_by_user = {}
    for session in all_current_sessions:
        current_sessions_by_user.setdefault(session['user_id'], []).append(session)
    
    last_sessions_by_user = {}
    for session in all_last_sessions:
        last_sessions_by_user.setdefault(session['user_id'], []).append(session)
    
    pillars_by_user = {}
    for pillar in all_pillars:
        pillars_by_user.setdefault(pillar['user_id'], []).append(pillar)
    
    leaderboard = []
    for user in users:
        current_sessions = current_sessions_by_user.get(user['id'], [])
        last_sessions = last_sessions_by_user.get(user['id'], [])
        user_pillars = pillars_by_user.get(user['id'], [])
        
        unique_days = set(s['date'] for s in current_sessions)
        days_logged = len(unique_days)
        consistency_pct = (days_logged / 7) * 100
        
        total_sessions = len(current_sessions)
        total_target = sum(p.get('weekly_target_sessions', p.get('weekly_target_minutes', 5)) for p in user_pillars)
        target_completion = min((total_sessions / total_target * 100) if total_target > 0 else 0, 100)
        performance_index = min((consistency_pct * 0.7) + (target_completion * 0.3), 100)
        
        last_total = len(last_sessions)
        improvement_pct = 0
        if last_total > 0:
            improvement_pct = ((total_sessions - last_total) / last_total) * 100
        elif total_sessions > 0:
            improvement_pct = 100
        
        age = user.get('age', 15)
        if age <= 14:
            user_age_group = '12-14'
        elif age <= 17:
            user_age_group = '15-17'
        else:
            user_age_group = '18-19'
        
        # Get display badge for this user
        user_display_badge = display_badges.get(user['id'])
        
        leaderboard.append({
            'username': user.get('username'),
            'consistency_pct': round(consistency_pct, 1),
            'performance_index': round(performance_index, 1),
            'age_group': user_age_group,
            'improvement_pct': round(improvement_pct, 1),
            'is_ambassador': user.get('is_ambassador', False),
            'display_badge': user_display_badge
        })
    
    leaderboard.sort(key=lambda x: x['improvement_pct'], reverse=True)
    return leaderboard[:100]
