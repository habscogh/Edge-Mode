"""
Group management routes for Edge Mode
"""
from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timezone, timedelta
from typing import List
import uuid

from config import db
from models.schemas import Group, GroupCreate, GroupJoin, TransferOwnership
from utils.auth import get_current_user, generate_invite_code

router = APIRouter(prefix="/groups", tags=["Groups"])


@router.get("", response_model=List[Group])
async def get_user_groups(current_user: dict = Depends(get_current_user)):
    groups = await db.groups.find(
        {'members': current_user['id']},
        {'_id': 0}
    ).to_list(100)
    return [Group(**g) for g in groups]


@router.post("", response_model=Group)
async def create_group(group_data: GroupCreate, current_user: dict = Depends(get_current_user)):
    group_doc = {
        'id': str(uuid.uuid4()),
        'name': group_data.name,
        'type': group_data.type,
        'created_by': current_user['id'],
        'members': [current_user['id']],
        'created_at': datetime.now(timezone.utc).isoformat(),
        'invite_code': generate_invite_code(),
        'coach_id': current_user['id'] if group_data.is_coach else None
    }
    await db.groups.insert_one(group_doc)
    return Group(**group_doc)


@router.post("/join")
async def join_group(join_data: GroupJoin, current_user: dict = Depends(get_current_user)):
    group = await db.groups.find_one({'invite_code': join_data.invite_code}, {'_id': 0})
    if not group:
        raise HTTPException(status_code=404, detail='Invalid invite code')
    
    if current_user['id'] in group['members']:
        return {'message': 'Already a member', 'group': group}
    
    await db.groups.update_one(
        {'id': group['id']},
        {'$push': {'members': current_user['id']}}
    )
    
    group['members'].append(current_user['id'])
    return {'message': 'Joined successfully', 'group': group}


@router.post("/{group_id}/leave")
async def leave_group(group_id: str, current_user: dict = Depends(get_current_user)):
    group = await db.groups.find_one({'id': group_id}, {'_id': 0})
    if not group:
        raise HTTPException(status_code=404, detail='Group not found')
    
    if group['created_by'] == current_user['id'] and len(group['members']) > 1:
        raise HTTPException(status_code=400, detail='Transfer ownership before leaving')
    
    if current_user['id'] not in group['members']:
        raise HTTPException(status_code=400, detail='Not a member of this group')
    
    await db.groups.update_one(
        {'id': group_id},
        {'$pull': {'members': current_user['id']}}
    )
    
    if group['created_by'] == current_user['id'] and len(group['members']) == 1:
        await db.groups.delete_one({'id': group_id})
        return {'message': 'Group deleted (you were the only member)'}
    
    return {'message': 'Left group successfully'}


@router.post("/{group_id}/transfer")
async def transfer_ownership(group_id: str, transfer_data: TransferOwnership, current_user: dict = Depends(get_current_user)):
    group = await db.groups.find_one({'id': group_id}, {'_id': 0})
    if not group:
        raise HTTPException(status_code=404, detail='Group not found')
    
    if group['created_by'] != current_user['id']:
        raise HTTPException(status_code=403, detail='Only the group creator can transfer ownership')
    
    if transfer_data.new_owner_id not in group['members']:
        raise HTTPException(status_code=400, detail='New owner must be a member of the group')
    
    if transfer_data.new_owner_id == current_user['id']:
        raise HTTPException(status_code=400, detail='You are already the owner')
    
    await db.groups.update_one(
        {'id': group_id},
        {'$set': {'created_by': transfer_data.new_owner_id}}
    )
    
    new_owner = await db.users.find_one({'id': transfer_data.new_owner_id}, {'_id': 0, 'password': 0})
    
    return {
        'message': f'Ownership transferred to {new_owner.get("username", "user")}',
        'new_owner': new_owner.get('username')
    }


@router.get("/{group_id}/leaderboard")
async def get_group_leaderboard(group_id: str, current_user: dict = Depends(get_current_user)):
    group = await db.groups.find_one({'id': group_id}, {'_id': 0})
    if not group or current_user['id'] not in group['members']:
        raise HTTPException(status_code=404, detail='Group not found')
    
    member_ids = group['members']
    today = datetime.now(timezone.utc).date()
    week_start = today - timedelta(days=today.weekday())
    
    users = await db.users.find({'id': {'$in': member_ids}}, {'_id': 0, 'password': 0}).to_list(100)
    users_by_id = {user['id']: user for user in users}
    
    all_sessions = await db.daily_sessions.find({
        'user_id': {'$in': member_ids},
        'date': {'$gte': week_start.isoformat()}
    }, {'_id': 0}).to_list(5000)
    sessions_by_user = {}
    for session in all_sessions:
        sessions_by_user.setdefault(session['user_id'], []).append(session)
    
    all_pillars = await db.user_pillars.find({'user_id': {'$in': member_ids}}, {'_id': 0}).to_list(500)
    pillars_by_user = {}
    for pillar in all_pillars:
        pillars_by_user.setdefault(pillar['user_id'], []).append(pillar)
    
    leaderboard = []
    for member_id in member_ids:
        user = users_by_id.get(member_id)
        if not user:
            continue
        
        sessions = sessions_by_user.get(member_id, [])
        user_pillars = pillars_by_user.get(member_id, [])
        
        unique_days = set(s['date'] for s in sessions)
        days_logged = len(unique_days)
        consistency_pct = (days_logged / 7) * 100
        
        total_sessions = len(sessions)
        total_target = sum(p['weekly_target_sessions'] for p in user_pillars)
        target_completion_pct = min((total_sessions / total_target * 100) if total_target > 0 else 0, 100)
        
        performance_index = min((consistency_pct * 0.7) + (target_completion_pct * 0.3), 100)
        
        leaderboard.append({
            'user_id': user['id'],
            'username': user.get('username') or user.get('name'),
            'consistency_pct': round(consistency_pct, 1),
            'performance_index': round(performance_index, 1),
            'current_streak': user.get('current_streak', 0),
            'total_sessions': total_sessions
        })
    
    leaderboard.sort(key=lambda x: x['performance_index'], reverse=True)
    return leaderboard
