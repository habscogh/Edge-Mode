"""
Coach dashboard routes for Edge Mode
"""
from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timezone, timedelta

from config import db
from utils.auth import get_current_user

router = APIRouter(prefix="/coach", tags=["Coach"])


@router.get("/dashboard")
async def get_coach_home_dashboard(current_user: dict = Depends(get_current_user)):
    """Get coach's home dashboard with team overview"""
    if not current_user.get('is_coach'):
        raise HTTPException(status_code=403, detail='Coach access required')
    
    team_id = current_user.get('team_id')
    if not team_id:
        raise HTTPException(status_code=404, detail='No team found for this coach')
    
    team = await db.groups.find_one({'id': team_id}, {'_id': 0})
    if not team:
        raise HTTPException(status_code=404, detail='Team not found')
    
    player_ids = [m for m in team.get('members', []) if m != current_user['id']]
    
    today = datetime.now(timezone.utc).date()
    week_start = today - timedelta(days=today.weekday())
    
    total_sessions_this_week = 0
    active_players = 0
    
    for player_id in player_ids:
        sessions = await db.daily_sessions.find({
            'user_id': player_id,
            'date': {'$gte': week_start.isoformat()}
        }).to_list(100)
        total_sessions_this_week += len(sessions)
        if sessions:
            active_players += 1
    
    return {
        'team': {
            'id': team['id'],
            'name': team['name'],
            'invite_code': team['invite_code'],
            'invite_link': f"/join/{team['invite_code']}",
            'has_extended_trial': team.get('has_extended_trial', False)
        },
        'stats': {
            'total_players': len(player_ids),
            'active_players_this_week': active_players,
            'total_sessions_this_week': total_sessions_this_week
        },
        'coach': {
            'name': current_user.get('name'),
            'email': current_user.get('email')
        }
    }


@router.get("/groups/{group_id}/dashboard")
async def get_coach_group_dashboard(group_id: str, current_user: dict = Depends(get_current_user)):
    """Get detailed stats for all players in a group (coach view only)"""
    group = await db.groups.find_one({'id': group_id}, {'_id': 0})
    if not group:
        raise HTTPException(status_code=404, detail='Group not found')
    
    if group.get('coach_id') != current_user['id']:
        raise HTTPException(status_code=403, detail='Only the coach can access this dashboard')
    
    member_ids = [m for m in group['members'] if m != current_user['id']]
    
    if not member_ids:
        return {
            'group': group,
            'players': [],
            'team_stats': {
                'total_players': 0,
                'avg_consistency': 0,
                'avg_performance': 0,
                'total_sessions_this_week': 0
            }
        }
    
    today = datetime.now(timezone.utc).date()
    week_start = today - timedelta(days=today.weekday())
    
    users = await db.users.find({'id': {'$in': member_ids}}, {'_id': 0, 'password': 0}).to_list(100)
    users_by_id = {u['id']: u for u in users}
    
    all_sessions = await db.daily_sessions.find({
        'user_id': {'$in': member_ids},
        'date': {'$gte': week_start.isoformat()}
    }, {'_id': 0}).to_list(5000)
    sessions_by_user = {}
    for s in all_sessions:
        sessions_by_user.setdefault(s['user_id'], []).append(s)
    
    all_pillars = await db.user_pillars.find({'user_id': {'$in': member_ids}}, {'_id': 0}).to_list(500)
    pillars_by_user = {}
    for p in all_pillars:
        pillars_by_user.setdefault(p['user_id'], []).append(p)
    
    players = []
    total_consistency = 0
    total_performance = 0
    total_sessions = 0
    
    for member_id in member_ids:
        user = users_by_id.get(member_id)
        if not user:
            continue
        
        sessions = sessions_by_user.get(member_id, [])
        pillars = pillars_by_user.get(member_id, [])
        
        unique_days = set(s['date'] for s in sessions)
        consistency_pct = (len(unique_days) / 7) * 100
        
        total_target = sum(p.get('weekly_target_sessions', 0) for p in pillars)
        target_completion = min((len(sessions) / total_target * 100) if total_target > 0 else 0, 100)
        performance_index = min((consistency_pct * 0.7) + (target_completion * 0.3), 100)
        
        pillar_stats = []
        for pillar in pillars:
            pillar_sessions = [s for s in sessions if s['pillar'] == pillar['pillar_name']]
            pillar_stats.append({
                'pillar_name': pillar['pillar_name'],
                'sessions': len(pillar_sessions),
                'target': pillar.get('weekly_target_sessions', 0),
                'minutes': sum(s.get('minutes_spent', 30) for s in pillar_sessions)
            })
        
        players.append({
            'id': member_id,
            'username': user.get('username'),
            'age': user.get('age'),
            'current_streak': user.get('current_streak', 0),
            'sessions_this_week': len(sessions),
            'consistency_pct': round(consistency_pct, 1),
            'performance_index': round(performance_index, 1),
            'pillar_breakdown': pillar_stats,
            'last_active': max([s['date'] for s in sessions]) if sessions else None
        })
        
        total_consistency += consistency_pct
        total_performance += performance_index
        total_sessions += len(sessions)
    
    players.sort(key=lambda x: x['performance_index'], reverse=True)
    
    return {
        'group': group,
        'players': players,
        'team_stats': {
            'total_players': len(players),
            'avg_consistency': round(total_consistency / len(players), 1) if players else 0,
            'avg_performance': round(total_performance / len(players), 1) if players else 0,
            'total_sessions_this_week': total_sessions
        }
    }


@router.get("/groups/{group_id}/player/{player_id}")
async def get_player_details(group_id: str, player_id: str, current_user: dict = Depends(get_current_user)):
    """Get detailed stats for a specific player (coach view only)"""
    group = await db.groups.find_one({'id': group_id}, {'_id': 0})
    if not group:
        raise HTTPException(status_code=404, detail='Group not found')
    
    if group.get('coach_id') != current_user['id']:
        raise HTTPException(status_code=403, detail='Only the coach can access player details')
    
    if player_id not in group['members']:
        raise HTTPException(status_code=404, detail='Player not in this group')
    
    player = await db.users.find_one({'id': player_id}, {'_id': 0, 'password': 0})
    if not player:
        raise HTTPException(status_code=404, detail='Player not found')
    
    today = datetime.now(timezone.utc).date()
    
    start_date = (today - timedelta(days=30)).isoformat()
    sessions = await db.daily_sessions.find({
        'user_id': player_id,
        'date': {'$gte': start_date}
    }, {'_id': 0}).sort('date', -1).to_list(1000)
    
    pillars = await db.user_pillars.find({'user_id': player_id}, {'_id': 0}).to_list(20)
    badges = await db.user_badges.find({'user_id': player_id}, {'_id': 0}).to_list(100)
    
    week_start = today - timedelta(days=today.weekday())
    week_sessions = [s for s in sessions if s['date'] >= week_start.isoformat()]
    
    unique_days = set(s['date'] for s in week_sessions)
    consistency_pct = (len(unique_days) / 7) * 100
    
    return {
        'player': {
            'id': player['id'],
            'username': player.get('username'),
            'age': player.get('age'),
            'current_streak': player.get('current_streak', 0),
            'longest_streak': player.get('longest_streak', 0)
        },
        'pillars': pillars,
        'recent_sessions': sessions[:50],
        'weekly_stats': {
            'sessions': len(week_sessions),
            'consistency_pct': round(consistency_pct, 1),
            'unique_days': len(unique_days),
            'minutes': sum(s.get('minutes_spent', 30) for s in week_sessions)
        },
        'badges_earned': len(badges)
    }
