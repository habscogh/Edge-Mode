"""
Onboarding and general routes for Edge Mode
"""
from fastapi import APIRouter, HTTPException, Depends
import uuid

from config import db, PILLARS
from models.schemas import OnboardingComplete
from utils.auth import get_current_user

router = APIRouter(tags=["Onboarding"])


@router.get("/pillars")
async def get_available_pillars():
    return {'pillars': PILLARS}


@router.post("/onboarding/complete")
async def complete_onboarding(data: OnboardingComplete, current_user: dict = Depends(get_current_user)):
    user_id = current_user['id']
    
    existing = await db.user_pillars.find({'user_id': user_id}, {'_id': 0}).to_list(100)
    if existing:
        raise HTTPException(status_code=400, detail='Onboarding already completed')
    
    for pillar_setup in data.pillars:
        pillar_doc = {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'pillar_name': pillar_setup.pillar_name,
            'weekly_target_sessions': pillar_setup.weekly_target_sessions
        }
        await db.user_pillars.insert_one(pillar_doc)
    
    return {'message': 'Onboarding complete'}


@router.get("/team/{team_code}")
async def get_team_info(team_code: str):
    """Get team info for players joining via invite link (public endpoint)"""
    team = await db.groups.find_one({'invite_code': team_code}, {'_id': 0})
    if not team:
        raise HTTPException(status_code=404, detail='Team not found')
    
    coach = await db.users.find_one({'id': team['coach_id']}, {'_id': 0, 'password': 0})
    
    return {
        'team_name': team['name'],
        'coach_name': coach.get('name', 'Coach') if coach else 'Coach',
        'member_count': len(team.get('members', [])) - 1,
        'has_extended_trial': team.get('has_extended_trial', False),
        'trial_days': 30 if team.get('has_extended_trial') else 14
    }
