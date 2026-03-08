"""
Session management routes for Edge Mode
"""
from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timezone, timedelta
from typing import Optional
import asyncio
import uuid

from config import db
from models.schemas import SessionComplete, EditSession, DailySession
from utils.auth import get_current_user
from utils.streaks import update_streak
from utils.badges import check_and_award_badges
from utils.timezone import get_today_string, get_eastern_date_from_datetime

router = APIRouter(prefix="/sessions", tags=["Sessions"])


# Parent notification functions (imported from parent routes later)
async def notify_parents_of_streak_milestone(student_id: str, student_username: str, streak: int):
    """Placeholder - actual implementation in parent routes"""
    from routes.parent import notify_parents_of_streak_milestone as notify
    await notify(student_id, student_username, streak)


async def notify_parents_of_new_badge(student_id: str, student_username: str, badge_name: str, badge_icon: str):
    """Placeholder - actual implementation in parent routes"""
    from routes.parent import notify_parents_of_new_badge as notify
    await notify(student_id, student_username, badge_name, badge_icon)


async def send_badge_push(user_id: str, badge_name: str, badge_icon: str):
    """Send push notification for new badge"""
    try:
        from routes.push import send_push_to_user, PushMessage
        await send_push_to_user(user_id, PushMessage(
            title=f"{badge_icon} New Badge Earned!",
            body=f"Congratulations! You earned the '{badge_name}' badge!",
            url="/achievements",
            tag=f"badge-{badge_name.lower().replace(' ', '-')}"
        ))
    except Exception:
        pass  # Push is non-critical


@router.post("/complete")
async def complete_session(session_data: SessionComplete, current_user: dict = Depends(get_current_user)):
    # Check trial status
    if current_user.get('is_trial') and current_user.get('trial_ends_at'):
        trial_end = datetime.fromisoformat(current_user['trial_ends_at'])
        if datetime.now(timezone.utc) > trial_end:
            raise HTTPException(status_code=403, detail='Trial expired. Please subscribe to continue.')
    
    user_id = current_user['id']
    now = datetime.now(timezone.utc)
    
    # Use client's local date if provided, otherwise use Eastern Time
    if session_data.local_date:
        try:
            datetime.strptime(session_data.local_date, '%Y-%m-%d')
            today = session_data.local_date
        except ValueError:
            today = get_today_string()  # Eastern Time
    else:
        today = get_today_string()  # Eastern Time
    
    user_pillars = await db.user_pillars.find({'user_id': user_id}, {'_id': 0}).to_list(100)
    pillar_names = [p['pillar_name'] for p in user_pillars]
    
    if session_data.pillar not in pillar_names:
        raise HTTPException(status_code=400, detail='Invalid pillar for this user')
    
    session_doc = {
        'id': str(uuid.uuid4()),
        'user_id': user_id,
        'pillar': session_data.pillar,
        'date': today,
        'timestamp': now.isoformat(),
        'minutes_spent': session_data.minutes_spent or 30,
        'note': session_data.note
    }
    await db.daily_sessions.insert_one(session_doc)
    
    # Update streak and last_log_date
    streak_result = await update_streak(user_id, now.isoformat())
    await db.users.update_one(
        {'id': user_id},
        {'$set': {'last_log_date': today}}
    )
    
    # Check for newly earned badges
    new_badges = await check_and_award_badges(user_id)
    
    # Parent notifications (run in background)
    if streak_result:
        current_streak, longest_streak, total_sessions = streak_result
        if current_streak in [7, 14, 30]:
            asyncio.create_task(notify_parents_of_streak_milestone(
                user_id, 
                current_user.get('username', 'Student'), 
                current_streak
            ))
    
    if new_badges:
        for badge in new_badges:
            asyncio.create_task(notify_parents_of_new_badge(
                user_id,
                current_user.get('username', 'Student'),
                badge['name'],
                badge['icon']
            ))
            # Send push notification for badge
            asyncio.create_task(send_badge_push(
                user_id,
                badge['name'],
                badge['icon']
            ))
    
    return {
        'session': DailySession(**session_doc).model_dump(),
        'new_badges': new_badges
    }


@router.put("/edit")
async def edit_session(edit_data: EditSession, current_user: dict = Depends(get_current_user)):
    session = await db.daily_sessions.find_one({'id': edit_data.session_id, 'user_id': current_user['id']}, {'_id': 0})
    if not session:
        raise HTTPException(status_code=404, detail='Session not found')
    
    update_fields = {'minutes_spent': edit_data.minutes_spent}
    if edit_data.pillar:
        update_fields['pillar'] = edit_data.pillar
    if edit_data.note is not None:
        update_fields['note'] = edit_data.note if edit_data.note else None
    
    await db.daily_sessions.update_one(
        {'id': edit_data.session_id},
        {'$set': update_fields}
    )
    
    return {'message': 'Session updated successfully'}


@router.delete("/{session_id}")
async def delete_session(session_id: str, current_user: dict = Depends(get_current_user)):
    result = await db.daily_sessions.delete_one({'id': session_id, 'user_id': current_user['id']})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail='Session not found')
    
    return {'message': 'Session deleted successfully'}


@router.get("/history")
async def get_session_history(current_user: dict = Depends(get_current_user), days: int = 30):
    from utils.timezone import get_today_eastern
    end_date = get_today_eastern()  # Eastern Time
    start_date = end_date - timedelta(days=days)
    
    sessions = await db.daily_sessions.find({
        'user_id': current_user['id'],
        'date': {'$gte': start_date.isoformat()}
    }, {'_id': 0}).sort('date', -1).to_list(1000)
    
    return sessions


@router.get("/today")
async def get_today_sessions(current_user: dict = Depends(get_current_user), local_date: Optional[str] = None):
    if local_date:
        try:
            datetime.strptime(local_date, '%Y-%m-%d')
            today = local_date
        except ValueError:
            today = get_today_string()  # Eastern Time
    else:
        today = get_today_string()  # Eastern Time
    
    sessions = await db.daily_sessions.find({
        'user_id': current_user['id'],
        'date': today
    }, {'_id': 0}).to_list(100)
    return sessions
