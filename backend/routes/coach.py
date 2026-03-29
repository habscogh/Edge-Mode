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
    
    # Identify inactive players (no sessions in 3+ days)
    inactive_players = []
    for player in players:
        if player['last_active']:
            last_active_date = datetime.fromisoformat(player['last_active']).date()
            days_inactive = (today - last_active_date).days
            if days_inactive >= 3:
                inactive_players.append({
                    'id': player['id'],
                    'username': player['username'],
                    'days_inactive': days_inactive
                })
        else:
            inactive_players.append({
                'id': player['id'],
                'username': player['username'],
                'days_inactive': 999
            })
    
    return {
        'group': group,
        'players': players,
        'team_stats': {
            'total_players': len(players),
            'avg_consistency': round(total_consistency / len(players), 1) if players else 0,
            'avg_performance': round(total_performance / len(players), 1) if players else 0,
            'total_sessions_this_week': total_sessions,
            'inactive_count': len(inactive_players)
        },
        'inactive_players': inactive_players
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



# Try to import resend for email sending
try:
    import resend
    import os
    resend.api_key = os.environ.get('RESEND_API_KEY')
    RESEND_AVAILABLE = bool(resend.api_key)
except ImportError:
    RESEND_AVAILABLE = False


@router.post("/bulk-invite")
async def send_bulk_invites(
    emails: list[str],
    custom_message: str = "",
    current_user: dict = Depends(get_current_user)
):
    """Send team invitations to multiple email addresses"""
    if not current_user.get('is_coach'):
        raise HTTPException(status_code=403, detail='Coach access required')
    
    team_id = current_user.get('team_id')
    if not team_id:
        raise HTTPException(status_code=404, detail='No team found for this coach')
    
    team = await db.groups.find_one({'id': team_id}, {'_id': 0})
    if not team:
        raise HTTPException(status_code=404, detail='Team not found')
    
    if not RESEND_AVAILABLE:
        raise HTTPException(status_code=503, detail='Email service not available')
    
    # Validate and clean emails
    import re
    email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    valid_emails = []
    invalid_emails = []
    
    for email in emails:
        email = email.strip().lower()
        if email and email_pattern.match(email):
            # Check if already a member
            existing_user = await db.users.find_one({'email': email})
            if existing_user and existing_user.get('id') in team.get('members', []):
                invalid_emails.append({'email': email, 'reason': 'Already a team member'})
            else:
                valid_emails.append(email)
        elif email:
            invalid_emails.append({'email': email, 'reason': 'Invalid email format'})
    
    if not valid_emails:
        return {
            'success': False,
            'message': 'No valid emails to send',
            'sent': 0,
            'failed': len(invalid_emails),
            'invalid_emails': invalid_emails
        }
    
    # Send invitations
    coach_name = current_user.get('name') or current_user.get('username') or 'Your Coach'
    team_name = team.get('name', 'the team')
    invite_code = team.get('invite_code')
    invite_link = f"https://edgemodeapp.com/join/{invite_code}"
    
    sent_count = 0
    failed_emails = []
    
    for email in valid_emails:
        try:
            resend.Emails.send({
                "from": "Edge Mode <noreply@edgemodeapp.com>",
                "to": email,
                "subject": f"🏆 {coach_name} invited you to join {team_name} on Edge Mode!",
                "html": f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h1 style="color: #22c55e; margin-bottom: 20px;">You're Invited! 🎯</h1>
                    
                    <p style="font-size: 16px; color: #333; line-height: 1.6;">
                        <strong>{coach_name}</strong> has invited you to join <strong>{team_name}</strong> on Edge Mode - 
                        the app that helps you become 1% better every day!
                    </p>
                    
                    {f'<p style="font-size: 14px; color: #666; background: #f5f5f5; padding: 15px; border-radius: 8px; margin: 20px 0;"><em>"{custom_message}"</em></p>' if custom_message else ''}
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{invite_link}" style="background: #22c55e; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-weight: bold; font-size: 16px;">
                            Join {team_name}
                        </a>
                    </div>
                    
                    <p style="font-size: 14px; color: #666;">
                        Or use invite code: <strong style="color: #22c55e;">{invite_code}</strong>
                    </p>
                    
                    <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                    
                    <p style="font-size: 12px; color: #999;">
                        Edge Mode helps teens track their self-improvement journey across fitness, study, creativity, and more.
                        Join thousands of users building better habits together!
                    </p>
                </div>
                """
            })
            sent_count += 1
            
            # Log the invitation
            await db.team_invitations.insert_one({
                'team_id': team_id,
                'coach_id': current_user['id'],
                'email': email,
                'sent_at': datetime.now(timezone.utc).isoformat(),
                'status': 'sent'
            })
            
        except Exception as e:
            failed_emails.append({'email': email, 'reason': str(e)})
    
    return {
        'success': sent_count > 0,
        'message': f'Sent {sent_count} invitation{"s" if sent_count != 1 else ""}',
        'sent': sent_count,
        'failed': len(failed_emails) + len(invalid_emails),
        'failed_emails': failed_emails,
        'invalid_emails': invalid_emails
    }


@router.get("/invitations")
async def get_invitation_history(current_user: dict = Depends(get_current_user)):
    """Get history of sent invitations"""
    if not current_user.get('is_coach'):
        raise HTTPException(status_code=403, detail='Coach access required')
    
    team_id = current_user.get('team_id')
    if not team_id:
        return {'invitations': []}
    
    invitations = await db.team_invitations.find(
        {'team_id': team_id},
        {'_id': 0}
    ).sort('sent_at', -1).to_list(100)
    
    # Check which invitations resulted in signups
    for inv in invitations:
        user = await db.users.find_one({'email': inv['email']}, {'_id': 0, 'id': 1, 'username': 1})
        if user:
            inv['joined'] = True
            inv['username'] = user.get('username')
        else:
            inv['joined'] = False
    
    return {'invitations': invitations}


@router.post("/groups/{group_id}/bulk-message")
async def send_bulk_message(
    group_id: str,
    message: str,
    subject: str = "Message from your Coach",
    current_user: dict = Depends(get_current_user)
):
    """Send an email message to all players in the team"""
    group = await db.groups.find_one({'id': group_id}, {'_id': 0})
    if not group:
        raise HTTPException(status_code=404, detail='Group not found')
    
    if group.get('coach_id') != current_user['id']:
        raise HTTPException(status_code=403, detail='Only the coach can send team messages')
    
    if not message or len(message.strip()) < 10:
        raise HTTPException(status_code=400, detail='Message must be at least 10 characters')
    
    if not RESEND_AVAILABLE:
        raise HTTPException(status_code=503, detail='Email service not available')
    
    # Get all player emails (exclude coach)
    member_ids = [m for m in group.get('members', []) if m != current_user['id']]
    
    if not member_ids:
        raise HTTPException(status_code=400, detail='No players in team to message')
    
    players = await db.users.find({'id': {'$in': member_ids}}, {'_id': 0, 'id': 1, 'email': 1, 'username': 1}).to_list(100)
    
    coach_name = current_user.get('name') or current_user.get('username', 'Your Coach')
    team_name = group.get('name', 'your team')
    
    sent_count = 0
    failed = []
    
    for player in players:
        try:
            resend.Emails.send({
                "from": "Edge Mode <noreply@edgemodeapp.com>",
                "to": player['email'],
                "subject": f"[{team_name}] {subject}",
                "html": f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <div style="background: #10b981; padding: 20px; text-align: center; border-radius: 8px 8px 0 0;">
                        <h2 style="color: white; margin: 0;">Message from {coach_name}</h2>
                    </div>
                    <div style="background: #18181b; padding: 30px; color: #fafafa;">
                        <p style="white-space: pre-wrap; line-height: 1.6;">{message}</p>
                    </div>
                    <div style="background: #09090b; padding: 20px; text-align: center; border-radius: 0 0 8px 8px;">
                        <p style="color: #71717a; margin: 0;">
                            This message was sent via Edge Mode.<br/>
                            <a href="https://edgemodeapp.com/dashboard" style="color: #10b981;">Log your progress today</a>
                        </p>
                    </div>
                </div>
                """
            })
            sent_count += 1
        except Exception as e:
            failed.append(player.get('email'))
    
    # Log the message
    await db.coach_messages.insert_one({
        'id': str(uuid.uuid4()),
        'group_id': group_id,
        'coach_id': current_user['id'],
        'subject': subject,
        'message': message,
        'sent_to': len(players),
        'sent_count': sent_count,
        'failed': failed,
        'sent_at': datetime.now(timezone.utc).isoformat()
    })
    
    return {
        'message': f'Message sent to {sent_count} player(s)',
        'sent_count': sent_count,
        'failed_count': len(failed)
    }


@router.get("/groups/{group_id}/messages")
async def get_message_history(group_id: str, current_user: dict = Depends(get_current_user)):
    """Get history of messages sent to the team"""
    group = await db.groups.find_one({'id': group_id}, {'_id': 0})
    if not group:
        raise HTTPException(status_code=404, detail='Group not found')
    
    if group.get('coach_id') != current_user['id']:
        raise HTTPException(status_code=403, detail='Only the coach can view message history')
    
    messages = await db.coach_messages.find(
        {'group_id': group_id},
        {'_id': 0}
    ).sort('sent_at', -1).to_list(50)
    
    return {'messages': messages}


@router.post("/resend-invitation")
async def resend_invitation(
    email: str,
    custom_message: str = "",
    current_user: dict = Depends(get_current_user)
):
    """Resend invitation to a specific email"""
    if not current_user.get('is_coach'):
        raise HTTPException(status_code=403, detail='Coach access required')
    
    team_id = current_user.get('team_id')
    if not team_id:
        raise HTTPException(status_code=404, detail='No team found')
    
    team = await db.groups.find_one({'id': team_id}, {'_id': 0})
    if not team:
        raise HTTPException(status_code=404, detail='Team not found')
    
    if not RESEND_AVAILABLE:
        raise HTTPException(status_code=503, detail='Email service not available')
    
    # Check if already joined
    existing_user = await db.users.find_one({'email': email.lower()})
    if existing_user and existing_user.get('id') in team.get('members', []):
        raise HTTPException(status_code=400, detail='This person has already joined the team')
    
    coach_name = current_user.get('name') or current_user.get('username') or 'Your Coach'
    team_name = team.get('name', 'the team')
    invite_code = team.get('invite_code')
    invite_link = f"https://edgemodeapp.com/join/{invite_code}"
    
    try:
        resend.Emails.send({
            "from": "Edge Mode <noreply@edgemodeapp.com>",
            "to": email.lower(),
            "subject": f"🔔 Reminder: {coach_name} is waiting for you on {team_name}!",
            "html": f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                <h1 style="color: #22c55e; margin-bottom: 20px;">Don't Miss Out! 🎯</h1>
                
                <p style="font-size: 16px; color: #333; line-height: 1.6;">
                    <strong>{coach_name}</strong> is still waiting for you to join <strong>{team_name}</strong> on Edge Mode!
                </p>
                
                <p style="font-size: 14px; color: #666; line-height: 1.6;">
                    Your teammates are already tracking their progress and crushing their goals. 
                    Don't get left behind!
                </p>
                
                {f'<p style="font-size: 14px; color: #666; background: #f5f5f5; padding: 15px; border-radius: 8px; margin: 20px 0;"><em>"{custom_message}"</em></p>' if custom_message else ''}
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{invite_link}" style="background: #22c55e; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-weight: bold; font-size: 16px;">
                        Join {team_name} Now
                    </a>
                </div>
                
                <p style="font-size: 14px; color: #666;">
                    Or use invite code: <strong style="color: #22c55e;">{invite_code}</strong>
                </p>
                
                <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                
                <p style="font-size: 12px; color: #999;">
                    Edge Mode helps teens track their self-improvement journey. 
                    Join thousands building better habits together!
                </p>
            </div>
            """
        })
        
        # Update invitation record
        await db.team_invitations.update_one(
            {'team_id': team_id, 'email': email.lower()},
            {
                '$set': {
                    'last_resent_at': datetime.now(timezone.utc).isoformat(),
                    'resend_count': 1
                },
                '$inc': {'resend_count': 1}
            },
            upsert=True
        )
        
        # If no record exists, create one
        existing_inv = await db.team_invitations.find_one({'team_id': team_id, 'email': email.lower()})
        if not existing_inv:
            await db.team_invitations.insert_one({
                'team_id': team_id,
                'coach_id': current_user['id'],
                'email': email.lower(),
                'sent_at': datetime.now(timezone.utc).isoformat(),
                'status': 'sent',
                'resend_count': 1
            })
        
        return {'success': True, 'message': f'Reminder sent to {email}'}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Failed to send email: {str(e)}')
