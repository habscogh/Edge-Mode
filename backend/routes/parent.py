"""
Parent-Student linking routes for Edge Mode
Simplified flow: Students add parent email, parents receive weekly reports without needing an account
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
    
    # Get all parent links (active ones - now just email-based)
    parent_links = await db.parent_links.find({
        'student_id': student_id,
        'status': 'active'
    }).to_list(10)
    
    for link in parent_links:
        parent_email = link.get('parent_email')
        if not parent_email:
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
                <p style="color: #52525b; font-size: 11px; margin-top: 10px;">You're receiving this because {student_username} added you as a parent on Edge Mode.</p>
            </div>
        </div>
        """
        await send_parent_notification(
            parent_email,
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
        parent_email = link.get('parent_email')
        if not parent_email:
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
                <p style="color: #52525b; font-size: 11px; margin-top: 10px;">You're receiving this because {student_username} added you as a parent on Edge Mode.</p>
            </div>
        </div>
        """
        await send_parent_notification(
            parent_email,
            f"🏅 {student_username} earned a new badge: {badge_name}",
            html
        )


# ============ Parent Routes ============

@router.post("/parent/add")
async def add_parent_email(invite_data: ParentInvite, current_user: dict = Depends(get_current_user)):
    """Student adds a parent's email to receive weekly reports (no account needed for parent)"""
    existing_links = await db.parent_links.count_documents({
        'student_id': current_user['id'],
        'status': 'active'
    })
    
    if existing_links >= 2:
        raise HTTPException(status_code=400, detail='Maximum of 2 parents can be added')
    
    existing_invite = await db.parent_links.find_one({
        'student_id': current_user['id'],
        'parent_email': invite_data.parent_email.lower()
    })
    
    if existing_invite:
        raise HTTPException(status_code=400, detail='This parent email is already added')
    
    link_doc = {
        'id': str(uuid.uuid4()),
        'student_id': current_user['id'],
        'student_username': current_user.get('username'),
        'parent_id': None,  # No account needed
        'parent_email': invite_data.parent_email.lower(),
        'status': 'active',  # Immediately active - no confirmation needed
        'added_at': datetime.now(timezone.utc).isoformat()
    }
    
    await db.parent_links.insert_one(link_doc)
    
    # Send welcome email to parent
    try:
        if RESEND_API_KEY:
            resend.api_key = RESEND_API_KEY
            
            resend.Emails.send({
                "from": "Edge Mode <noreply@edgemodeapp.com>",
                "to": invite_data.parent_email,
                "subject": f"📊 You've been added to track {current_user.get('username')}'s progress on Edge Mode",
                "html": f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background: #09090b; color: white;">
                    <div style="text-align: center; padding: 20px 0;">
                        <h1 style="color: #10b981; margin: 0; font-size: 28px;">📊 Weekly Progress Reports</h1>
                    </div>
                    <div style="padding: 20px; background: #18181b; border-radius: 8px; margin: 20px 0;">
                        <p style="margin: 0; font-size: 16px; color: #a1a1aa;">Hi there!</p>
                        <p style="margin: 15px 0; color: white;"><strong style="color: #10b981;">{current_user.get('username')}</strong> has added you to receive their weekly progress reports from <strong>Edge Mode</strong>.</p>
                        <p style="margin: 15px 0; color: #a1a1aa;">You'll automatically receive:</p>
                        <ul style="color: #a1a1aa; padding-left: 20px;">
                            <li style="margin: 8px 0;">📧 Weekly progress summaries every Sunday</li>
                            <li style="margin: 8px 0;">🔥 Streak milestone celebrations</li>
                            <li style="margin: 8px 0;">🏅 Achievement notifications</li>
                            <li style="margin: 8px 0;">⚠️ Inactivity alerts (if they miss 3+ days)</li>
                        </ul>
                        <p style="margin: 15px 0; color: #71717a; font-size: 14px;">No account creation needed - reports will come directly to this email.</p>
                    </div>
                    <div style="text-align: center; padding: 20px;">
                        <p style="color: #71717a; font-size: 12px;">Edge Mode - 1% Better Every Day</p>
                        <p style="color: #52525b; font-size: 11px; margin-top: 10px;">If you didn't expect this, please ignore this email.</p>
                    </div>
                </div>
                """
            })
            logger.info(f"Parent welcome email sent to {invite_data.parent_email}")
    except Exception as e:
        logger.error(f"Failed to send parent welcome email: {e}")
    
    return {
        'message': f'Parent added successfully. {invite_data.parent_email} will receive weekly reports.',
        'parent_email': invite_data.parent_email
    }


# Keep the old invite endpoint for backwards compatibility but redirect to new flow
@router.post("/parent/invite")
async def invite_parent(invite_data: ParentInvite, current_user: dict = Depends(get_current_user)):
    """Legacy endpoint - now just adds parent email directly"""
    return await add_parent_email(invite_data, current_user)


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
    """Student views their linked parent emails"""
    links = await db.parent_links.find({
        'student_id': current_user['id'],
        'status': 'active'
    }, {'_id': 0}).to_list(10)
    
    parent_list = []
    for link in links:
        parent_list.append({
            'link_id': link['id'],
            'parent_email': link['parent_email'],
            'added_at': link.get('added_at')
        })
    
    return {
        'parents': parent_list,
        'max_parents': 2,
        'slots_remaining': 2 - len(parent_list)
    }


@router.delete("/parent/remove/{link_id}")
async def remove_parent(link_id: str, current_user: dict = Depends(get_current_user)):
    """Student removes a parent from receiving reports"""
    link = await db.parent_links.find_one({'id': link_id})
    
    if not link:
        raise HTTPException(status_code=404, detail='Parent link not found')
    
    if link['student_id'] != current_user['id']:
        raise HTTPException(status_code=403, detail='Not authorized to remove this parent')
    
    await db.parent_links.delete_one({'id': link_id})
    
    return {'message': f"Removed {link['parent_email']} from receiving reports"}
