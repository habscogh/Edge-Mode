"""
Ambassador routes for Edge Mode - Founding Ambassador program
"""
from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel

from config import db, logger
from utils.auth import get_current_user

router = APIRouter(prefix="/ambassador", tags=["Ambassador"])

# Ambassador activation codes - controlled by admin
# These are the special codes that grant ambassador status
AMBASSADOR_CODES = [
    "EDGEFOUNDER2025",
    "AMBASSADOR1",
    "FOUNDINGMEMBER",
]


class AmbassadorActivation(BaseModel):
    code: str


@router.post("/activate")
async def activate_ambassador(
    data: AmbassadorActivation,
    current_user: dict = Depends(get_current_user)
):
    """
    Activate Founding Ambassador status with a special code.
    Grants:
    - Founding Ambassador title (visible to everyone)
    - 1 year free subscription
    - Special referral tracking
    """
    user_id = current_user["id"]
    
    # Check if already an ambassador
    if current_user.get("is_ambassador"):
        return {
            "success": False,
            "message": "You're already a Founding Ambassador! 🎖️"
        }
    
    # Validate code
    if data.code.upper().strip() not in [c.upper() for c in AMBASSADOR_CODES]:
        raise HTTPException(status_code=400, detail="Invalid ambassador code")
    
    # Calculate 1 year subscription
    now = datetime.now(timezone.utc)
    subscription_end = now + timedelta(days=365)
    
    # Update user with ambassador status
    await db.users.update_one(
        {"id": user_id},
        {
            "$set": {
                "is_ambassador": True,
                "ambassador_since": now.isoformat(),
                "ambassador_code_used": data.code.upper().strip(),
                "subscription_active": True,
                "subscription_end": subscription_end.isoformat(),
                "is_trial": False,  # Not a trial, it's ambassador benefit
            }
        }
    )
    
    logger.info(f"User {user_id} activated as Founding Ambassador with code {data.code}")
    
    return {
        "success": True,
        "message": "🎖️ Welcome, Founding Ambassador! You now have 1 year free access.",
        "subscription_end": subscription_end.isoformat()
    }


@router.get("/stats")
async def get_ambassador_stats(current_user: dict = Depends(get_current_user)):
    """
    Get ambassador-specific stats including referral tracking.
    """
    if not current_user.get("is_ambassador"):
        return {"is_ambassador": False}
    
    user_id = current_user["id"]
    referral_code = current_user.get("referral_code")
    
    # Count total referrals
    total_referrals = await db.referrals.count_documents({"referrer_id": user_id})
    
    # Get referral details with user info
    referrals = await db.referrals.find(
        {"referrer_id": user_id},
        {"_id": 0, "referred_email": 1, "referred_username": 1, "created_at": 1}
    ).sort("created_at", -1).to_list(100)
    
    # Calculate referrals this month
    month_start = datetime.now(timezone.utc).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    monthly_referrals = await db.referrals.count_documents({
        "referrer_id": user_id,
        "created_at": {"$gte": month_start.isoformat()}
    })
    
    # Get subscription end date
    subscription_end = current_user.get("subscription_end")
    ambassador_since = current_user.get("ambassador_since")
    
    return {
        "is_ambassador": True,
        "ambassador_since": ambassador_since,
        "subscription_end": subscription_end,
        "total_referrals": total_referrals,
        "monthly_referrals": monthly_referrals,
        "referrals": referrals,
        "referral_code": referral_code
    }


@router.get("/leaderboard")
async def get_ambassador_leaderboard():
    """
    Get leaderboard of top ambassadors by referrals.
    """
    # Get all ambassadors
    ambassadors = await db.users.find(
        {"is_ambassador": True},
        {"_id": 0, "id": 1, "username": 1, "ambassador_since": 1}
    ).to_list(100)
    
    # Count referrals for each ambassador
    ambassador_stats = []
    for amb in ambassadors:
        referral_count = await db.referrals.count_documents({"referrer_id": amb["id"]})
        ambassador_stats.append({
            "username": amb["username"],
            "ambassador_since": amb.get("ambassador_since"),
            "referral_count": referral_count
        })
    
    # Sort by referral count
    ambassador_stats.sort(key=lambda x: x["referral_count"], reverse=True)
    
    return {
        "ambassadors": ambassador_stats[:20],
        "total_ambassadors": len(ambassadors)
    }
