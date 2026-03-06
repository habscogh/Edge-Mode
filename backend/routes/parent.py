"""
Parent-Student linking routes for Edge Mode
"""
from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timezone, timedelta
import uuid
import asyncio
import os
import resend

from config import db, logger, RESEND_API_KEY, SENDER_EMAIL
from models.schemas import ParentInvite, ParentAccept
from utils.auth import get_current_user, generate_invite_code

router = APIRouter(tags=["Parent"])


# ============ Parent Notification Functions ============

async def send_parent_notification(parent_email: str, subject: str, html: str):
    """Helper function to send email to parent"""
    if not RESEND_API_KEY:
        return
    try:
        await asyncio.to_thread(resend.Emails.send, {
            "from": SENDER_EMAIL,
            "to": [parent_email],
            "subject": subject,
            "html": html
        })
        logger.info(f"Parent notification sent to {parent_email}: {subject}")
    except Exception as e:
        logger.error(f"Failed to send parent notification to {parent_email}: {e}")


async def notify_parents_of_streak_milestone(student_id: str, student_username: str, streak: int):
    """Notify parents when student hits a streak milestone (7, 14, 30 days)"""
    if streak not in [7, 14, 30]:
        return
    
    parent_links = await db.parent_links.find({
        'student_id': student_id,
        'status': 'active'
    }).to_list(10)
    
    for link in parent_links:
        parent = await db.users.find_one({'id': link['parent_id']}, {'_id': 0})
        if not parent:
            continue
        
        milestone_emoji = "🔥" if streak == 7 else "⚡" if streak == 14 else "🏆"
        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background: #09090b; color: white;">
            <div style="text-align: center; padding: 20px 0;">
                <h1 style="color: #10b981; margin: 0; font-size: 28px;">{milestone_emoji} Streak Milestone!</h1>
            </div>
            <div style="padding: 20px; background: #18181b; border-radius: 8px; margin: 20px 0; text-align: center;">
                <p style="margin: 0; font-size: 18px; color: #a1a1aa;">Great news!</p>
                <p style="margin: 15px 0; font-size: 24px;"><strong style="color: #10b981;">{student_username}</strong> just hit a</p>
                <div style="font-size: 48px; font-weight: bold; color: #f97316; margin: 20px 0;">{streak} Day Streak!</div>
                <p style="margin: 15px 0; color: #71717a;">That's {streak} consecutive days of self-improvement. Amazing dedication!</p>
            </div>
            <div style="text-align: center; padding: 20px;">
                <p style="color: #71717a; font-size: 12px;">Edge Mode - 1% Better Every Day</p>
            </div>
        </div>
        """
        await send_parent_notification(
            parent['email'],
            f"🎉 {student_username} hit a {streak}-day streak!",
            html
        )


async def notify_parents_of_new_badge(student_id: str, student_username: str, badge_name: str, badge_icon: str):
    """Notify parents when student earns a new badge"""
    parent_links = await db.parent_links.find({
        'student_id': student_id,
        'status': 'active'
    }).to_list(10)
    
    for link in parent_links:
        parent = await db.users.find_one({'id': link['parent_id']}, {'_id': 0})
        if not parent:
            continue
        
        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background: #09090b; color: white;">
            <div style="text-align: center; padding: 20px 0;">
                <h1 style="color: #10b981; margin: 0; font-size: 28px;">🏅 New Achievement!</h1>
            </div>
            <div style="padding: 20px; background: #18181b; border-radius: 8px; margin: 20px 0; text-align: center;">
                <p style="margin: 0; font-size: 18px; color: #a1a1aa;">Congratulations!</p>
                <p style="margin: 15px 0; font-size: 20px;"><strong style="color: #10b981;">{student_username}</strong> earned a new badge:</p>
                <div style="font-size: 64px; margin: 20px 0;">{badge_icon}</div>
                <div style="font-size: 24px; font-weight: bold; color: white; margin: 10px 0;">{badge_name}</div>
            </div>
            <div style="text-align: center; padding: 20px;">
                <p style="color: #71717a; font-size: 12px;">Edge Mode - 1% Better Every Day</p>
            </div>
        </div>
        """
        await send_parent_notification(
            parent['email'],
            f"🏅 {student_username} earned a new badge: {badge_name}",
            html
        )


# ============ Parent Routes ============

@router.post("/parent/invite")
async def invite_parent(invite_data: ParentInvite, current_user: dict = Depends(get_current_user)):
    """Student invites a parent via email"""
    existing_links = await db.parent_links.count_documents({
        'student_id': current_user['id'],
        'status': {'$in': ['pending', 'active']}
    })
    
    if existing_links >= 2:
        raise HTTPException(status_code=400, detail='Maximum of 2 parents can be linked')
    
    existing_invite = await db.parent_links.find_one({
        'student_id': current_user['id'],
        'parent_email': invite_data.parent_email.lower()
    })
    
    if existing_invite:
        if existing_invite['status'] == 'active':
            raise HTTPException(status_code=400, detail='This parent is already linked')
        else:
            raise HTTPException(status_code=400, detail='Invitation already sent to this email')
    
    invite_code = f"PARENT-{generate_invite_code()}"
    
    link_doc = {
        'id': str(uuid.uuid4()),
        'student_id': current_user['id'],
        'student_username': current_user.get('username'),
        'parent_id': None,
        'parent_email': invite_data.parent_email.lower(),
        'status': 'pending',
        'invite_code': invite_code,
        'invited_at': datetime.now(timezone.utc).isoformat(),
        'accepted_at': None
    }
    
    await db.parent_links.insert_one(link_doc)
    
    try:
        if RESEND_API_KEY:
            resend.api_key = RESEND_API_KEY
            
            resend.Emails.send({
                "from": "Edge Mode <noreply@edgemodeapp.com>",
                "to": invite_data.parent_email,
                "subject": f"{current_user.get('username')} invited you to track their progress on Edge Mode",
                "html": f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <h2 style="color: #10b981;">You've Been Invited! 🎉</h2>
                    <p><strong>{current_user.get('username')}</strong> wants you to track their self-improvement journey on Edge Mode.</p>
                    <p>As a parent, you'll be able to:</p>
                    <ul>
                        <li>View their progress, streaks, and achievements</li>
                        <li>Receive notifications about milestones</li>
                        <li>See their weekly consistency and performance</li>
                    </ul>
                    <p>To accept this invitation, create an account or log in and use this code:</p>
                    <div style="background: #f0fdf4; padding: 20px; border-radius: 8px; text-align: center; margin: 20px 0;">
                        <span style="font-size: 24px; font-weight: bold; color: #10b981; letter-spacing: 2px;">{invite_code}</span>
                    </div>
                    <p style="color: #666;">This invitation was sent by {current_user.get('username')} from Edge Mode.</p>
                </div>
                """
            })
            logger.info(f"Parent invitation email sent to {invite_data.parent_email}")
    except Exception as e:
        logger.error(f"Failed to send parent invitation email: {e}")
    
    return {
        'message': 'Invitation sent successfully',
        'invite_code': invite_code,
        'parent_email': invite_data.parent_email
    }


@router.post("/parent/accept")
async def accept_parent_invite(accept_data: ParentAccept, current_user: dict = Depends(get_current_user)):
    """Parent accepts an invitation using invite code"""
    link = await db.parent_links.find_one({
        'invite_code': accept_data.invite_code,
        'status': 'pending'
    })
    
    if not link:
        raise HTTPException(status_code=404, detail='Invalid or expired invite code')
    
    await db.parent_links.update_one(
        {'id': link['id']},
        {
            '$set': {
                'parent_id': current_user['id'],
                'status': 'active',
                'accepted_at': datetime.now(timezone.utc).isoformat()
            }
        }
    )
    
    await db.users.update_one(
        {'id': current_user['id']},
        {'$set': {'is_parent': True}}
    )
    
    student = await db.users.find_one({'id': link['student_id']}, {'_id': 0, 'password': 0})
    
    return {
        'message': f'Successfully linked to {link["student_username"]}',
        'student': {
            'id': student['id'],
            'username': student.get('username')
        }
    }


@router.get("/parent/linked-students")
async def get_linked_students(current_user: dict = Depends(get_current_user)):
    """Get all students linked to this parent"""
    links = await db.parent_links.find({
        'parent_id': current_user['id'],
        'status': 'active'
    }, {'_id': 0}).to_list(10)
    
    if not links:
        return {'students': []}
    
    student_ids = [link['student_id'] for link in links]
    students = await db.users.find(
        {'id': {'$in': student_ids}},
        {'_id': 0, 'password': 0}
    ).to_list(10)
    
    return {'students': students, 'links': links}


@router.get("/parent/student/{student_id}/dashboard")
async def get_student_dashboard_for_parent(student_id: str, current_user: dict = Depends(get_current_user)):
    """Parent views their linked student's dashboard"""
    link = await db.parent_links.find_one({
        'parent_id': current_user['id'],
        'student_id': student_id,
        'status': 'active'
    })
    
    if not link:
        raise HTTPException(status_code=403, detail='You are not linked to this student')
    
    student = await db.users.find_one({'id': student_id}, {'_id': 0, 'password': 0})
    if not student:
        raise HTTPException(status_code=404, detail='Student not found')
    
    today = datetime.now(timezone.utc).date()
    week_start = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)
    
    sessions = await db.daily_sessions.find({
        'user_id': student_id,
        'date': {'$gte': month_start.isoformat()}
    }, {'_id': 0}).to_list(1000)
    
    week_sessions = [s for s in sessions if s['date'] >= week_start.isoformat()]
    
    pillars = await db.user_pillars.find({'user_id': student_id}, {'_id': 0}).to_list(20)
    badges = await db.user_badges.find({'user_id': student_id}, {'_id': 0}).to_list(100)
    
    unique_days = set(s['date'] for s in week_sessions)
    consistency_pct = (len(unique_days) / 7) * 100
    
    total_target = sum(p.get('weekly_target_sessions', 0) for p in pillars)
    target_completion = min((len(week_sessions) / total_target * 100) if total_target > 0 else 0, 100)
    performance_index = min((consistency_pct * 0.7) + (target_completion * 0.3), 100)
    
    pillar_stats = []
    for pillar in pillars:
        pillar_week_sessions = [s for s in week_sessions if s['pillar'] == pillar['pillar_name']]
        pillar_stats.append({
            'pillar_name': pillar['pillar_name'],
            'sessions_this_week': len(pillar_week_sessions),
            'target': pillar.get('weekly_target_sessions', 0),
            'minutes': sum(s.get('minutes_spent', 30) for s in pillar_week_sessions)
        })
    
    return {
        'student': {
            'id': student['id'],
            'username': student.get('username'),
            'age': student.get('age'),
            'current_streak': student.get('current_streak', 0),
            'longest_streak': student.get('longest_streak', 0)
        },
        'weekly_stats': {
            'sessions': len(week_sessions),
            'consistency_pct': round(consistency_pct, 1),
            'performance_index': round(performance_index, 1),
            'days_active': len(unique_days)
        },
        'monthly_stats': {
            'total_sessions': len(sessions),
            'total_minutes': sum(s.get('minutes_spent', 30) for s in sessions)
        },
        'pillars': pillar_stats,
        'badges_earned': len(badges),
        'recent_sessions': sessions[:10]
    }


@router.get("/student/linked-parents")
async def get_linked_parents(current_user: dict = Depends(get_current_user)):
    """Student views their linked parents"""
    links = await db.parent_links.find({
        'student_id': current_user['id']
    }, {'_id': 0}).to_list(10)
    
    active_links = []
    pending_links = []
    
    for link in links:
        if link['status'] == 'active' and link.get('parent_id'):
            parent = await db.users.find_one({'id': link['parent_id']}, {'_id': 0, 'password': 0})
            if parent:
                active_links.append({
                    'link_id': link['id'],
                    'parent_email': link['parent_email'],
                    'parent_username': parent.get('username'),
                    'linked_at': link.get('accepted_at')
                })
        elif link['status'] == 'pending':
            pending_links.append({
                'link_id': link['id'],
                'parent_email': link['parent_email'],
                'invited_at': link['invited_at']
            })
    
    return {
        'active_parents': active_links,
        'pending_invites': pending_links,
        'max_parents': 2,
        'slots_remaining': 2 - len(active_links) - len(pending_links)
    }


@router.delete("/parent/unlink/{link_id}")
async def unlink_parent(link_id: str, current_user: dict = Depends(get_current_user)):
    """Student or parent can unlink the relationship"""
    link = await db.parent_links.find_one({'id': link_id})
    
    if not link:
        raise HTTPException(status_code=404, detail='Link not found')
    
    if link['student_id'] != current_user['id'] and link.get('parent_id') != current_user['id']:
        raise HTTPException(status_code=403, detail='Not authorized to unlink')
    
    await db.parent_links.delete_one({'id': link_id})
    
    return {'message': 'Successfully unlinked'}
