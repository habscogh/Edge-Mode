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
    
    streak_milestones = [
        (7, 'streak_7'),
        (14, 'streak_14'),
        (21, 'streak_21'),
        (30, 'streak_30'),
        (45, 'streak_45'),
        (60, 'streak_60'),
        (90, 'streak_90'),
        (120, 'streak_120'),
        (180, 'streak_180'),
        (365, 'streak_365'),
    ]
    
    for days, badge_id in streak_milestones:
        if max_streak >= days:
            badge = await award_badge(user_id, badge_id)
            if badge:
                newly_earned.append(badge)
    
    # Check Session milestones
    session_milestones = [
        (100, 'sessions_100'),
        (250, 'sessions_250'),
        (500, 'sessions_500'),
        (1000, 'sessions_1000'),
    ]
    
    for count, badge_id in session_milestones:
        if total_sessions >= count:
            badge = await award_badge(user_id, badge_id)
            if badge:
                newly_earned.append(badge)
    
    # Check Hours milestones
    hours_milestones = [
        (50, 'hours_50'),
        (100, 'hours_100'),
        (250, 'hours_250'),
        (500, 'hours_500'),
        (1000, 'hours_1000'),
    ]
    
    for hours, badge_id in hours_milestones:
        if total_hours >= hours:
            badge = await award_badge(user_id, badge_id)
            if badge:
                newly_earned.append(badge)
    
    # Check Perfect Week (logged every day for 7 consecutive days)
    if current_streak >= 7:
        badge = await award_badge(user_id, 'perfect_week')
        if badge:
            newly_earned.append(badge)
    
    # Check Perfect Month (30+ day streak)
    if current_streak >= 30:
        badge = await award_badge(user_id, 'perfect_month')
        if badge:
            newly_earned.append(badge)
    
    # Check Perfect Quarter (90+ day streak)
    if current_streak >= 90:
        badge = await award_badge(user_id, 'perfect_quarter')
        if badge:
            newly_earned.append(badge)
    
    # Check OG Member (6+ months since signup)
    created_at = user.get('created_at')
    if created_at:
        try:
            signup_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            days_since_signup = (now - signup_date).days
            
            if days_since_signup >= 180:  # 6 months
                badge = await award_badge(user_id, 'og_member')
                if badge:
                    newly_earned.append(badge)
            
            if days_since_signup >= 365:  # 1 year
                badge = await award_badge(user_id, 'founding_year')
                if badge:
                    newly_earned.append(badge)
        except:
            pass
    
    # Check Challenge win badges
    challenge_wins = await db.user_badges.count_documents({
        'user_id': user_id,
        'badge_id': {'$in': ['weekly_champion', 'monthly_champion']}
    })
    
    if challenge_wins >= 5:
        badge = await award_badge(user_id, 'challenge_streak_5')
        if badge:
            newly_earned.append(badge)
    
    if challenge_wins >= 10:
        badge = await award_badge(user_id, 'challenge_streak_10')
        if badge:
            newly_earned.append(badge)
    
    # Check Referral badges
    referral_count = user.get('referral_count', 0)
    
    if referral_count >= 5:
        badge = await award_badge(user_id, 'referral_5')
        if badge:
            newly_earned.append(badge)
    
    if referral_count >= 10:
        badge = await award_badge(user_id, 'referral_10')
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
