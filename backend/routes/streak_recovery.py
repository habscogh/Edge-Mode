"""
Streak Recovery feature for Edge Mode
Allows users to pay to recover a broken streak
"""
from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel
from typing import Optional
import uuid

from config import db, logger, STRIPE_API_KEY
from utils.auth import get_current_user
from utils.timezone import get_today_eastern

router = APIRouter(prefix="/streak-recovery", tags=["Streak Recovery"])

# Pricing for streak recovery (in cents)
RECOVERY_PRICE_CENTS = 299  # $2.99

class RecoveryEligibility(BaseModel):
    eligible: bool
    reason: Optional[str] = None
    previous_streak: int = 0
    days_since_broken: int = 0
    recovery_price: float = 2.99
    recovery_window_days: int = 7


class RecoveryCheckoutResponse(BaseModel):
    url: str
    session_id: str


@router.get("/eligibility", response_model=RecoveryEligibility)
async def check_recovery_eligibility(current_user: dict = Depends(get_current_user)):
    """
    Check if user is eligible for streak recovery.
    Eligibility rules:
    - User must have had a streak of at least 3 days
    - Streak must have been broken within the last 7 days
    - User hasn't already recovered this streak
    """
    user_id = current_user['id']
    
    # Get user's streak history
    user = await db.users.find_one({'id': user_id}, {'_id': 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    current_streak = user.get('current_streak', 0)
    last_log_date_str = user.get('last_log_date')
    longest_streak = user.get('longest_streak', 0)
    
    # Check if there's a saved broken streak to recover
    broken_streak_data = user.get('broken_streak_data')
    
    if broken_streak_data:
        # User has a recoverable streak
        broken_date = datetime.fromisoformat(broken_streak_data['broken_date']).date()
        today = get_today_eastern()
        days_since = (today - broken_date).days
        
        if days_since <= 7:
            return RecoveryEligibility(
                eligible=True,
                previous_streak=broken_streak_data['previous_streak'],
                days_since_broken=days_since,
                recovery_price=RECOVERY_PRICE_CENTS / 100,
                recovery_window_days=7 - days_since
            )
        else:
            # Recovery window expired
            # Clear the broken streak data
            await db.users.update_one(
                {'id': user_id},
                {'$unset': {'broken_streak_data': ''}}
            )
            return RecoveryEligibility(
                eligible=False,
                reason="Recovery window has expired (7 days)",
                previous_streak=broken_streak_data['previous_streak'],
                days_since_broken=days_since
            )
    
    # Check if streak was recently broken
    if last_log_date_str and current_streak <= 1:
        last_log_date = datetime.fromisoformat(last_log_date_str).date()
        today = get_today_eastern()
        days_since_log = (today - last_log_date).days
        
        # If they logged yesterday or today, streak isn't broken yet
        if days_since_log <= 1:
            return RecoveryEligibility(
                eligible=False,
                reason="Your streak is not broken yet! Keep logging to maintain it.",
                previous_streak=current_streak
            )
        
        # Streak is broken - check if the previous streak was worth recovering
        # We need to check their streak history
        if longest_streak >= 3:
            # Their longest streak was worth recovering
            # But we don't know their actual streak before it broke
            # This is a limitation - in production, you'd track this better
            return RecoveryEligibility(
                eligible=False,
                reason="Unable to determine previous streak. Start a new streak!",
                previous_streak=0
            )
    
    return RecoveryEligibility(
        eligible=False,
        reason="No broken streak to recover. Keep your current streak going!",
        previous_streak=current_streak
    )


@router.post("/create-checkout")
async def create_recovery_checkout(
    origin_url: str = "https://edgemodeapp.com",
    current_user: dict = Depends(get_current_user)
):
    """Create a Stripe checkout session for streak recovery"""
    from emergentintegrations.llm.stripe import create_checkout_session
    
    user_id = current_user['id']
    
    # Check eligibility first
    eligibility = await check_recovery_eligibility(current_user)
    if not eligibility.eligible:
        raise HTTPException(status_code=400, detail=eligibility.reason or "Not eligible for streak recovery")
    
    # Create a recovery record
    recovery_id = str(uuid.uuid4())
    await db.streak_recoveries.insert_one({
        'id': recovery_id,
        'user_id': user_id,
        'previous_streak': eligibility.previous_streak,
        'status': 'pending',
        'created_at': datetime.now(timezone.utc).isoformat(),
        'amount_cents': RECOVERY_PRICE_CENTS
    })
    
    try:
        # Create Stripe checkout session
        checkout = create_checkout_session(
            stripe_api_key=STRIPE_API_KEY,
            price_cents=RECOVERY_PRICE_CENTS,
            product_name=f"Streak Recovery - Restore {eligibility.previous_streak} Day Streak",
            success_url=f"{origin_url}/streak-recovery/success?recovery_id={recovery_id}",
            cancel_url=f"{origin_url}/dashboard",
            mode="payment",  # One-time payment, not subscription
            metadata={
                'user_id': user_id,
                'recovery_id': recovery_id,
                'previous_streak': str(eligibility.previous_streak)
            }
        )
        
        # Update recovery with session ID
        await db.streak_recoveries.update_one(
            {'id': recovery_id},
            {'$set': {'stripe_session_id': checkout.id}}
        )
        
        return RecoveryCheckoutResponse(url=checkout.url, session_id=checkout.id)
        
    except Exception as e:
        logger.error(f"Failed to create streak recovery checkout: {e}")
        # Clean up the pending recovery
        await db.streak_recoveries.delete_one({'id': recovery_id})
        raise HTTPException(status_code=500, detail="Failed to create checkout session")


@router.get("/status/{recovery_id}")
async def get_recovery_status(recovery_id: str, current_user: dict = Depends(get_current_user)):
    """Check the status of a streak recovery"""
    from emergentintegrations.llm.stripe import get_checkout_session
    
    recovery = await db.streak_recoveries.find_one(
        {'id': recovery_id, 'user_id': current_user['id']},
        {'_id': 0}
    )
    
    if not recovery:
        raise HTTPException(status_code=404, detail="Recovery not found")
    
    if recovery.get('status') == 'completed':
        return {
            'status': 'completed',
            'recovered_streak': recovery.get('previous_streak', 0),
            'message': 'Your streak has been restored!'
        }
    
    # Check Stripe session status
    session_id = recovery.get('stripe_session_id')
    if session_id:
        try:
            session = get_checkout_session(STRIPE_API_KEY, session_id)
            
            if session.payment_status == 'paid' and recovery.get('status') != 'completed':
                # Process the recovery
                await process_streak_recovery(current_user['id'], recovery_id, recovery.get('previous_streak', 0))
                return {
                    'status': 'completed',
                    'recovered_streak': recovery.get('previous_streak', 0),
                    'message': 'Your streak has been restored!'
                }
            
            return {
                'status': 'pending' if session.payment_status == 'unpaid' else session.payment_status,
                'message': 'Payment is being processed...'
            }
        except Exception as e:
            logger.error(f"Failed to check recovery status: {e}")
    
    return {
        'status': recovery.get('status', 'unknown'),
        'message': 'Checking payment status...'
    }


async def process_streak_recovery(user_id: str, recovery_id: str, previous_streak: int):
    """Process a successful streak recovery payment"""
    today = get_today_eastern()
    
    # Restore the user's streak
    await db.users.update_one(
        {'id': user_id},
        {
            '$set': {
                'current_streak': previous_streak,
                'last_log_date': today.isoformat(),
                # Clear the broken streak data
            },
            '$unset': {'broken_streak_data': ''}
        }
    )
    
    # Update the recovery record
    await db.streak_recoveries.update_one(
        {'id': recovery_id},
        {'$set': {
            'status': 'completed',
            'completed_at': datetime.now(timezone.utc).isoformat()
        }}
    )
    
    # Log the recovery for analytics
    await db.streak_recovery_logs.insert_one({
        'user_id': user_id,
        'recovery_id': recovery_id,
        'previous_streak': previous_streak,
        'recovered_at': datetime.now(timezone.utc).isoformat()
    })
    
    logger.info(f"User {user_id} recovered {previous_streak}-day streak via recovery_id {recovery_id}")


@router.get("/history")
async def get_recovery_history(current_user: dict = Depends(get_current_user)):
    """Get user's streak recovery history"""
    recoveries = await db.streak_recoveries.find(
        {'user_id': current_user['id']},
        {'_id': 0}
    ).sort('created_at', -1).to_list(10)
    
    return {'recoveries': recoveries}
