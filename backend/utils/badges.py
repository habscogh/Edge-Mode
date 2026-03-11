"""
Badge checking and awarding utilities for Edge Mode
"""
import uuid
from datetime import datetime, timezone, timedelta
from typing import List, Optional

from config import db, BADGES, logger


async def award_badge(user_id: str, badge_id: str, send_notification: bool = True) -> dict:
    """Award a badge to a user if they don't already have it"""
    existing = await db.user_badges.find_one({
        'user_id': user_id,
        'badge_id': badge_id
    })
    
    if existing:
        return None
    
    badge_info = BADGES.get(badge_id)
    if not badge_info:
        logger.warning(f"Unknown badge_id: {badge_id}")
        return None
    
    badge_doc = {
        'id': str(uuid.uuid4()),
        'user_id': user_id,
        'badge_id': badge_id,
        'earned_at': datetime.now(timezone.utc).isoformat()
    }
    await db.user_badges.insert_one(badge_doc)
    
    logger.info(f"Badge '{badge_id}' awarded to user {user_id}")
    
    # Send push notification for new badge
    if send_notification:
        try:
            from routes.push import send_badge_earned_push
            await send_badge_earned_push(
                user_id, 
                badge_info['name'], 
                badge_info['icon'], 
                badge_info['description']
            )
        except Exception as e:
            logger.error(f"Failed to send badge push notification: {e}")
    
    return {**badge_info, 'earned_at': badge_doc['earned_at']}


async def check_and_award_badges(user_id: str) -> List[dict]:
    """Check all badge conditions and award any newly earned badges"""
    user = await db.users.find_one({'id': user_id}, {'_id': 0})
    if not user:
        return []
    
    newly_earned = []
    now = datetime.now(timezone.utc)
    
    all_sessions = await db.daily_sessions.find({'user_id': user_id}, {'_id': 0}).to_list(10000)
    total_sessions = len(all_sessions)
    total_minutes = sum(s.get('minutes_spent', 0) for s in all_sessions)
    total_hours = total_minutes / 60
    
    # Check First Session badge
    if total_sessions >= 1:
        badge = await award_badge(user_id, 'first_session')
        if badge:
            newly_earned.append(badge)
    
    # Check Streak badges
    current_streak = user.get('current_streak', 0)
    longest_streak = user.get('longest_streak', 0)
    max_streak = max(current_streak, longest_streak)
    
    if max_streak >= 7:
        badge = await award_badge(user_id, 'streak_7')
        if badge:
            newly_earned.append(badge)
    
    if max_streak >= 14:
        badge = await award_badge(user_id, 'streak_14')
        if badge:
            newly_earned.append(badge)
    
    if max_streak >= 30:
        badge = await award_badge(user_id, 'streak_30')
        if badge:
            newly_earned.append(badge)
    
    # Check Century Club (100 sessions)
    if total_sessions >= 100:
        badge = await award_badge(user_id, 'sessions_100')
        if badge:
            newly_earned.append(badge)
    
    # Check 50 Hour Club
    if total_hours >= 50:
        badge = await award_badge(user_id, 'hours_50')
        if badge:
            newly_earned.append(badge)
    
    # Check Perfect Week (logged every day for 7 consecutive days)
    if current_streak >= 7:
        badge = await award_badge(user_id, 'perfect_week')
        if badge:
            newly_earned.append(badge)
    
    # Check Pillar Master (hit target on all pillars in current week)
    user_pillars = await db.user_pillars.find({'user_id': user_id}, {'_id': 0}).to_list(100)
    if user_pillars:
        week_start = now.date() - timedelta(days=now.weekday())
        week_sessions = await db.daily_sessions.find({
            'user_id': user_id,
            'date': {'$gte': week_start.isoformat()}
        }, {'_id': 0}).to_list(1000)
        
        all_targets_met = True
        for pillar in user_pillars:
            pillar_sessions = [s for s in week_sessions if s['pillar'] == pillar['pillar_name']]
            if len(pillar_sessions) < pillar['weekly_target_sessions']:
                all_targets_met = False
                break
        
        if all_targets_met:
            badge = await award_badge(user_id, 'pillar_master')
            if badge:
                newly_earned.append(badge)
    
    return newly_earned
