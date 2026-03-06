"""
Challenge routes for Edge Mode
"""
from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timezone, timedelta, date
from typing import Optional
import uuid

from config import db, logger, PILLARS
from models.schemas import ChallengeJoin, ChallengeCreate
from utils.auth import get_current_user
from utils.badges import award_badge

router = APIRouter(prefix="/challenges", tags=["Challenges"])


async def calculate_challenge_score(user_id: str, challenge: dict) -> float:
    """Calculate a user's score for a challenge based on metric type"""
    start_date = challenge['start_date']
    end_date = challenge['end_date']
    metric_type = challenge['metric_type']
    pillar = challenge.get('pillar')
    
    query = {
        'user_id': user_id,
        'date': {'$gte': start_date, '$lte': end_date}
    }
    if pillar:
        query['pillar'] = pillar
    
    sessions = await db.daily_sessions.find(query, {'_id': 0}).to_list(1000)
    
    if metric_type == 'pillar_sessions' or metric_type == 'total_sessions':
        return len(sessions)
    elif metric_type == 'pillar_minutes' or metric_type == 'total_minutes':
        return sum(s.get('minutes_spent', 30) for s in sessions)
    elif metric_type == 'consistency':
        unique_days = set(s['date'] for s in sessions)
        start_dt = date.fromisoformat(start_date)
        end_dt = date.fromisoformat(end_date)
        total_days = (end_dt - start_dt).days + 1
        return (len(unique_days) / total_days) * 100
    return 0


async def update_challenge_rankings(challenge_id: str):
    """Update rankings for all participants in a challenge"""
    participants = await db.challenge_participants.find(
        {'challenge_id': challenge_id}
    ).sort('current_score', -1).to_list(1000)
    
    for rank, participant in enumerate(participants, 1):
        await db.challenge_participants.update_one(
            {'id': participant['id']},
            {'$set': {'rank': rank}}
        )


async def create_automated_challenges():
    """Create weekly and monthly challenges automatically"""
    now = datetime.now(timezone.utc)
    today = now.date()
    
    if today.weekday() == 0:  # Monday
        week_start = today
        week_end = today + timedelta(days=6)
        
        for pillar in PILLARS[:3]:
            challenge_id = str(uuid.uuid4())
            pillar_short = pillar.split('/')[0]
            await db.challenges.insert_one({
                'id': challenge_id,
                'name': f'Weekly {pillar_short} Champion',
                'description': f'Log the most {pillar_short.lower()} sessions this week!',
                'challenge_type': 'weekly',
                'metric_type': 'pillar_sessions',
                'pillar': pillar,
                'start_date': week_start.isoformat(),
                'end_date': week_end.isoformat(),
                'status': 'active',
                'created_at': now.isoformat(),
                'created_by': 'system',
                'participant_count': 0
            })
        
        general_challenges = [
            {'name': 'Most Consistent', 'description': 'Achieve the highest consistency % this week', 'metric': 'consistency'},
            {'name': 'Time Warrior', 'description': 'Log the most total minutes this week', 'metric': 'total_minutes'},
        ]
        for gc in general_challenges:
            await db.challenges.insert_one({
                'id': str(uuid.uuid4()),
                'name': f'Weekly {gc["name"]}',
                'description': gc['description'],
                'challenge_type': 'weekly',
                'metric_type': gc['metric'],
                'pillar': None,
                'start_date': week_start.isoformat(),
                'end_date': week_end.isoformat(),
                'status': 'active',
                'created_at': now.isoformat(),
                'created_by': 'system',
                'participant_count': 0
            })
    
    if today.day == 1:
        month_start = today
        if today.month == 12:
            month_end = date(today.year + 1, 1, 1) - timedelta(days=1)
        else:
            month_end = date(today.year, today.month + 1, 1) - timedelta(days=1)
        
        monthly_challenges = [
            {'name': 'Monthly Sessions King', 'description': 'Log the most sessions this month', 'metric': 'total_sessions'},
            {'name': 'Monthly Time Champion', 'description': 'Accumulate the most training minutes this month', 'metric': 'total_minutes'},
            {'name': 'Consistency Master', 'description': 'Achieve the highest consistency % this month', 'metric': 'consistency'},
        ]
        for mc in monthly_challenges:
            await db.challenges.insert_one({
                'id': str(uuid.uuid4()),
                'name': mc['name'],
                'description': mc['description'],
                'challenge_type': 'monthly',
                'metric_type': mc['metric'],
                'pillar': None,
                'start_date': month_start.isoformat(),
                'end_date': month_end.isoformat(),
                'status': 'active',
                'created_at': now.isoformat(),
                'created_by': 'system',
                'participant_count': 0
            })


async def finalize_completed_challenges():
    """Finalize challenges that have ended and award badges"""
    now = datetime.now(timezone.utc)
    today = now.date().isoformat()
    
    ended_challenges = await db.challenges.find({
        'status': 'active',
        'end_date': {'$lt': today}
    }).to_list(100)
    
    for challenge in ended_challenges:
        await update_challenge_rankings(challenge['id'])
        
        top_participants = await db.challenge_participants.find(
            {'challenge_id': challenge['id']}
        ).sort('current_score', -1).limit(3).to_list(3)
        
        for idx, participant in enumerate(top_participants):
            user_id = participant['user_id']
            
            await award_badge(user_id, 'podium_finish')
            
            if idx == 0 and participant['current_score'] > 0:
                if challenge['challenge_type'] == 'weekly':
                    await award_badge(user_id, 'weekly_champion')
                else:
                    await award_badge(user_id, 'monthly_champion')
                
                wins = await db.challenge_participants.count_documents({
                    'user_id': user_id,
                    'rank': 1
                })
                if wins >= 3:
                    await award_badge(user_id, 'challenge_streak_3')
        
        await db.challenges.update_one(
            {'id': challenge['id']},
            {'$set': {'status': 'completed'}}
        )


async def seed_initial_challenges():
    """Seed initial challenges on first startup"""
    now = datetime.now(timezone.utc)
    today = now.date()
    
    days_since_monday = today.weekday()
    week_start = today - timedelta(days=days_since_monday)
    week_end = week_start + timedelta(days=6)
    
    month_start = today.replace(day=1)
    if today.month == 12:
        month_end = date(today.year + 1, 1, 1) - timedelta(days=1)
    else:
        month_end = date(today.year, today.month + 1, 1) - timedelta(days=1)
    
    challenges = [
        {
            'id': str(uuid.uuid4()),
            'name': 'Weekly Fitness Champion',
            'description': 'Log the most Fitness sessions this week!',
            'challenge_type': 'weekly',
            'metric_type': 'pillar_sessions',
            'pillar': 'Fitness/Training',
            'start_date': week_start.isoformat(),
            'end_date': week_end.isoformat(),
            'status': 'active',
            'created_at': now.isoformat(),
            'created_by': 'system',
            'participant_count': 0
        },
        {
            'id': str(uuid.uuid4()),
            'name': 'Weekly Study Star',
            'description': 'Log the most Study sessions this week!',
            'challenge_type': 'weekly',
            'metric_type': 'pillar_sessions',
            'pillar': 'Study/Academics',
            'start_date': week_start.isoformat(),
            'end_date': week_end.isoformat(),
            'status': 'active',
            'created_at': now.isoformat(),
            'created_by': 'system',
            'participant_count': 0
        },
        {
            'id': str(uuid.uuid4()),
            'name': 'Weekly Most Consistent',
            'description': 'Achieve the highest consistency % this week',
            'challenge_type': 'weekly',
            'metric_type': 'consistency',
            'pillar': None,
            'start_date': week_start.isoformat(),
            'end_date': week_end.isoformat(),
            'status': 'active',
            'created_at': now.isoformat(),
            'created_by': 'system',
            'participant_count': 0
        },
        {
            'id': str(uuid.uuid4()),
            'name': 'Weekly Time Warrior',
            'description': 'Log the most total minutes this week',
            'challenge_type': 'weekly',
            'metric_type': 'total_minutes',
            'pillar': None,
            'start_date': week_start.isoformat(),
            'end_date': week_end.isoformat(),
            'status': 'active',
            'created_at': now.isoformat(),
            'created_by': 'system',
            'participant_count': 0
        },
        {
            'id': str(uuid.uuid4()),
            'name': 'Monthly Sessions King',
            'description': 'Log the most sessions this month',
            'challenge_type': 'monthly',
            'metric_type': 'total_sessions',
            'pillar': None,
            'start_date': month_start.isoformat(),
            'end_date': month_end.isoformat(),
            'status': 'active',
            'created_at': now.isoformat(),
            'created_by': 'system',
            'participant_count': 0
        },
        {
            'id': str(uuid.uuid4()),
            'name': 'Monthly Consistency Master',
            'description': 'Achieve the highest consistency % this month',
            'challenge_type': 'monthly',
            'metric_type': 'consistency',
            'pillar': None,
            'start_date': month_start.isoformat(),
            'end_date': month_end.isoformat(),
            'status': 'active',
            'created_at': now.isoformat(),
            'created_by': 'system',
            'participant_count': 0
        }
    ]
    
    for challenge in challenges:
        await db.challenges.insert_one(challenge)
        logger.info(f"Seeded challenge: {challenge['name']}")
    
    logger.info(f"Successfully seeded {len(challenges)} initial challenges")


async def challenges_daily_job():
    """Daily job to manage challenges - create new ones and finalize completed ones"""
    await create_automated_challenges()
    await finalize_completed_challenges()
    logger.info("Challenges daily job completed")


# ============ Challenge Routes ============

@router.get("")
async def get_challenges(status: Optional[str] = None, challenge_type: Optional[str] = None, current_user: dict = Depends(get_current_user)):
    """Get all challenges, optionally filtered by status and type"""
    query = {}
    if status:
        query['status'] = status
    if challenge_type:
        query['challenge_type'] = challenge_type
    
    challenges = await db.challenges.find(query, {'_id': 0}).sort('created_at', -1).to_list(50)
    
    for challenge in challenges:
        participation = await db.challenge_participants.find_one({
            'challenge_id': challenge['id'],
            'user_id': current_user['id']
        }, {'_id': 0})
        challenge['is_participating'] = participation is not None
        if participation:
            challenge['user_rank'] = participation.get('rank', 0)
            challenge['user_score'] = participation.get('current_score', 0)
    
    return challenges


@router.get("/my")
async def get_my_challenges(current_user: dict = Depends(get_current_user)):
    """Get challenges the current user is participating in"""
    participations = await db.challenge_participants.find(
        {'user_id': current_user['id']},
        {'_id': 0}
    ).to_list(50)
    
    challenge_ids = [p['challenge_id'] for p in participations]
    challenges = await db.challenges.find(
        {'id': {'$in': challenge_ids}},
        {'_id': 0}
    ).to_list(50)
    
    for challenge in challenges:
        participation = next((p for p in participations if p['challenge_id'] == challenge['id']), None)
        if participation:
            challenge['user_rank'] = participation.get('rank', 0)
            challenge['user_score'] = participation.get('current_score', 0)
        challenge['is_participating'] = True
    
    return challenges


@router.get("/{challenge_id}")
async def get_challenge(challenge_id: str, current_user: dict = Depends(get_current_user)):
    """Get a specific challenge with details"""
    challenge = await db.challenges.find_one({'id': challenge_id}, {'_id': 0})
    if not challenge:
        raise HTTPException(status_code=404, detail='Challenge not found')
    
    participation = await db.challenge_participants.find_one({
        'challenge_id': challenge_id,
        'user_id': current_user['id']
    }, {'_id': 0})
    challenge['is_participating'] = participation is not None
    if participation:
        challenge['user_rank'] = participation.get('rank', 0)
        challenge['user_score'] = participation.get('current_score', 0)
    
    return challenge


@router.post("/join")
async def join_challenge(join_data: ChallengeJoin, current_user: dict = Depends(get_current_user)):
    """Join a challenge"""
    challenge = await db.challenges.find_one({'id': join_data.challenge_id}, {'_id': 0})
    if not challenge:
        raise HTTPException(status_code=404, detail='Challenge not found')
    
    if challenge['status'] != 'active':
        raise HTTPException(status_code=400, detail='This challenge is no longer accepting participants')
    
    existing = await db.challenge_participants.find_one({
        'challenge_id': join_data.challenge_id,
        'user_id': current_user['id']
    })
    if existing:
        raise HTTPException(status_code=400, detail='You have already joined this challenge')
    
    initial_score = await calculate_challenge_score(current_user['id'], challenge)
    
    participant_doc = {
        'id': str(uuid.uuid4()),
        'challenge_id': join_data.challenge_id,
        'user_id': current_user['id'],
        'username': current_user.get('username'),
        'joined_at': datetime.now(timezone.utc).isoformat(),
        'current_score': initial_score,
        'rank': 0
    }
    await db.challenge_participants.insert_one(participant_doc)
    
    await db.challenges.update_one(
        {'id': join_data.challenge_id},
        {'$inc': {'participant_count': 1}}
    )
    
    await update_challenge_rankings(join_data.challenge_id)
    
    updated_participant = await db.challenge_participants.find_one(
        {'id': participant_doc['id']},
        {'_id': 0}
    )
    
    return {'message': 'Successfully joined challenge', 'participant': updated_participant}


@router.post("/leave/{challenge_id}")
async def leave_challenge(challenge_id: str, current_user: dict = Depends(get_current_user)):
    """Leave a challenge"""
    challenge = await db.challenges.find_one({'id': challenge_id}, {'_id': 0})
    if not challenge:
        raise HTTPException(status_code=404, detail='Challenge not found')
    
    participation = await db.challenge_participants.find_one({
        'challenge_id': challenge_id,
        'user_id': current_user['id']
    })
    if not participation:
        raise HTTPException(status_code=400, detail='You are not in this challenge')
    
    await db.challenge_participants.delete_one({'id': participation['id']})
    
    await db.challenges.update_one(
        {'id': challenge_id},
        {'$inc': {'participant_count': -1}}
    )
    
    await update_challenge_rankings(challenge_id)
    
    return {'message': 'Successfully left challenge'}


@router.get("/{challenge_id}/leaderboard")
async def get_challenge_leaderboard(challenge_id: str, current_user: dict = Depends(get_current_user)):
    """Get the leaderboard for a specific challenge"""
    challenge = await db.challenges.find_one({'id': challenge_id}, {'_id': 0})
    if not challenge:
        raise HTTPException(status_code=404, detail='Challenge not found')
    
    participants = await db.challenge_participants.find({'challenge_id': challenge_id}).to_list(1000)
    
    for participant in participants:
        new_score = await calculate_challenge_score(participant['user_id'], challenge)
        await db.challenge_participants.update_one(
            {'id': participant['id']},
            {'$set': {'current_score': new_score}}
        )
    
    await update_challenge_rankings(challenge_id)
    
    leaderboard = await db.challenge_participants.find(
        {'challenge_id': challenge_id},
        {'_id': 0}
    ).sort('rank', 1).to_list(100)
    
    user_participant = next((p for p in leaderboard if p['user_id'] == current_user['id']), None)
    
    return {
        'challenge': challenge,
        'leaderboard': leaderboard,
        'user_participating': user_participant is not None,
        'user_rank': user_participant['rank'] if user_participant else None,
        'user_score': user_participant['current_score'] if user_participant else None
    }


@router.post("/admin/create")
async def admin_create_challenge(challenge_data: ChallengeCreate, current_user: dict = Depends(get_current_user)):
    """Admin endpoint to create a custom challenge"""
    if current_user['email'] != 'admin@edgemodeapp.com':
        raise HTTPException(status_code=403, detail='Admin access required')
    
    now = datetime.now(timezone.utc)
    today = now.date()
    
    if challenge_data.challenge_type == 'weekly':
        days_until_monday = (7 - today.weekday()) % 7
        if days_until_monday == 0:
            days_until_monday = 7
        start_date = today + timedelta(days=days_until_monday)
        end_date = start_date + timedelta(days=6)
    else:
        if today.month == 12:
            start_date = date(today.year + 1, 1, 1)
        else:
            start_date = date(today.year, today.month + 1, 1)
        if start_date.month == 12:
            end_date = date(start_date.year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(start_date.year, start_date.month + 1, 1) - timedelta(days=1)
    
    challenge_doc = {
        'id': str(uuid.uuid4()),
        'name': challenge_data.name,
        'description': challenge_data.description,
        'challenge_type': challenge_data.challenge_type,
        'metric_type': challenge_data.metric_type,
        'pillar': challenge_data.pillar,
        'start_date': start_date.isoformat(),
        'end_date': end_date.isoformat(),
        'status': 'upcoming',
        'created_at': now.isoformat(),
        'created_by': current_user['id'],
        'participant_count': 0
    }
    
    await db.challenges.insert_one(challenge_doc)
    return {'message': 'Challenge created', 'challenge': {k: v for k, v in challenge_doc.items() if k != '_id'}}
