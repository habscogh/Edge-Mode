"""
School routes for Edge Mode - School search and leaderboard
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from datetime import datetime, timezone, timedelta
from typing import Optional
import httpx
import asyncio

from config import db, logger
from utils.auth import get_current_user

router = APIRouter(prefix="/schools", tags=["Schools"])

# Common US high schools - seed data with city/state for better identification
# In production, this would be populated from NCES database
COMMON_SCHOOLS = [
    {"nces_id": "hs_001", "name": "Lincoln High School", "city": "San Diego", "state": "CA", "grades": "9-12"},
    {"nces_id": "hs_001b", "name": "Lincoln High School", "city": "Portland", "state": "OR", "grades": "9-12"},
    {"nces_id": "hs_001c", "name": "Lincoln High School", "city": "Philadelphia", "state": "PA", "grades": "9-12"},
    {"nces_id": "hs_001d", "name": "Lincoln High School", "city": "Tallahassee", "state": "FL", "grades": "9-12"},
    {"nces_id": "hs_002", "name": "Washington High School", "city": "San Francisco", "state": "CA", "grades": "9-12"},
    {"nces_id": "hs_002b", "name": "Washington High School", "city": "Kansas City", "state": "KS", "grades": "9-12"},
    {"nces_id": "hs_002c", "name": "Washington High School", "city": "Milwaukee", "state": "WI", "grades": "9-12"},
    {"nces_id": "hs_003", "name": "Jefferson High School", "city": "Los Angeles", "state": "CA", "grades": "9-12"},
    {"nces_id": "hs_003b", "name": "Jefferson High School", "city": "Tampa", "state": "FL", "grades": "9-12"},
    {"nces_id": "hs_003c", "name": "Jefferson High School", "city": "Portland", "state": "OR", "grades": "9-12"},
    {"nces_id": "hs_004", "name": "Roosevelt High School", "city": "Seattle", "state": "WA", "grades": "9-12"},
    {"nces_id": "hs_004b", "name": "Roosevelt High School", "city": "Chicago", "state": "IL", "grades": "9-12"},
    {"nces_id": "hs_004c", "name": "Roosevelt High School", "city": "Fresno", "state": "CA", "grades": "9-12"},
    {"nces_id": "hs_005", "name": "Kennedy High School", "city": "Sacramento", "state": "CA", "grades": "9-12"},
    {"nces_id": "hs_005b", "name": "Kennedy High School", "city": "Cedar Rapids", "state": "IA", "grades": "9-12"},
    {"nces_id": "hs_005c", "name": "Kennedy High School", "city": "Waterbury", "state": "CT", "grades": "9-12"},
    {"nces_id": "hs_006", "name": "Central High School", "city": "Phoenix", "state": "AZ", "grades": "9-12"},
    {"nces_id": "hs_006b", "name": "Central High School", "city": "Philadelphia", "state": "PA", "grades": "9-12"},
    {"nces_id": "hs_006c", "name": "Central High School", "city": "Memphis", "state": "TN", "grades": "9-12"},
    {"nces_id": "hs_006d", "name": "Central High School", "city": "Little Rock", "state": "AR", "grades": "9-12"},
    {"nces_id": "hs_007", "name": "West High School", "city": "Salt Lake City", "state": "UT", "grades": "9-12"},
    {"nces_id": "hs_007b", "name": "West High School", "city": "Torrance", "state": "CA", "grades": "9-12"},
    {"nces_id": "hs_007c", "name": "West High School", "city": "Anchorage", "state": "AK", "grades": "9-12"},
    {"nces_id": "hs_008", "name": "East High School", "city": "Denver", "state": "CO", "grades": "9-12"},
    {"nces_id": "hs_008b", "name": "East High School", "city": "Salt Lake City", "state": "UT", "grades": "9-12"},
    {"nces_id": "hs_008c", "name": "East High School", "city": "Memphis", "state": "TN", "grades": "9-12"},
    {"nces_id": "hs_009", "name": "North High School", "city": "Phoenix", "state": "AZ", "grades": "9-12"},
    {"nces_id": "hs_009b", "name": "North High School", "city": "Minneapolis", "state": "MN", "grades": "9-12"},
    {"nces_id": "hs_009c", "name": "North High School", "city": "Torrance", "state": "CA", "grades": "9-12"},
    {"nces_id": "hs_010", "name": "South High School", "city": "Minneapolis", "state": "MN", "grades": "9-12"},
    {"nces_id": "hs_010b", "name": "South High School", "city": "Denver", "state": "CO", "grades": "9-12"},
    {"nces_id": "hs_010c", "name": "South High School", "city": "Torrance", "state": "CA", "grades": "9-12"},
    {"nces_id": "hs_011", "name": "Westview High School", "city": "San Diego", "state": "CA", "grades": "9-12"},
    {"nces_id": "hs_011b", "name": "Westview High School", "city": "Portland", "state": "OR", "grades": "9-12"},
    {"nces_id": "hs_012", "name": "Eastview High School", "city": "Apple Valley", "state": "MN", "grades": "9-12"},
    {"nces_id": "hs_013", "name": "Lakewood High School", "city": "Lakewood", "state": "CA", "grades": "9-12"},
    {"nces_id": "hs_013b", "name": "Lakewood High School", "city": "Lakewood", "state": "CO", "grades": "9-12"},
    {"nces_id": "hs_013c", "name": "Lakewood High School", "city": "St. Petersburg", "state": "FL", "grades": "9-12"},
    {"nces_id": "hs_014", "name": "Riverside High School", "city": "Durham", "state": "NC", "grades": "9-12"},
    {"nces_id": "hs_014b", "name": "Riverside High School", "city": "Greer", "state": "SC", "grades": "9-12"},
    {"nces_id": "hs_015", "name": "Mountain View High School", "city": "Mountain View", "state": "CA", "grades": "9-12"},
    {"nces_id": "hs_015b", "name": "Mountain View High School", "city": "Mesa", "state": "AZ", "grades": "9-12"},
    {"nces_id": "hs_015c", "name": "Mountain View High School", "city": "Vancouver", "state": "WA", "grades": "9-12"},
    {"nces_id": "hs_016", "name": "Valley High School", "city": "Las Vegas", "state": "NV", "grades": "9-12"},
    {"nces_id": "hs_016b", "name": "Valley High School", "city": "West Des Moines", "state": "IA", "grades": "9-12"},
    {"nces_id": "hs_016c", "name": "Valley High School", "city": "Santa Ana", "state": "CA", "grades": "9-12"},
    {"nces_id": "hs_017", "name": "Fairview High School", "city": "Boulder", "state": "CO", "grades": "9-12"},
    {"nces_id": "hs_017b", "name": "Fairview High School", "city": "Asheville", "state": "NC", "grades": "9-12"},
    {"nces_id": "hs_018", "name": "Hillcrest High School", "city": "Dallas", "state": "TX", "grades": "9-12"},
    {"nces_id": "hs_018b", "name": "Hillcrest High School", "city": "Midvale", "state": "UT", "grades": "9-12"},
    {"nces_id": "hs_019", "name": "Oakwood High School", "city": "Dayton", "state": "OH", "grades": "9-12"},
    {"nces_id": "hs_020", "name": "Parkview High School", "city": "Springfield", "state": "MO", "grades": "9-12"},
    {"nces_id": "hs_020b", "name": "Parkview High School", "city": "Lilburn", "state": "GA", "grades": "9-12"},
    {"nces_id": "ms_001", "name": "Lincoln Middle School", "city": "Santa Monica", "state": "CA", "grades": "6-8"},
    {"nces_id": "ms_002", "name": "Washington Middle School", "city": "Seattle", "state": "WA", "grades": "6-8"},
    {"nces_id": "ms_003", "name": "Jefferson Middle School", "city": "Champaign", "state": "IL", "grades": "6-8"},
]


@router.get("/search")
async def search_schools(
    q: str = Query(..., min_length=2, description="Search query (min 2 characters)"),
    state: Optional[str] = Query(None, max_length=2, description="State code (e.g., CA, TX)")
):
    """
    Search for US schools (grades 8-12) by name.
    Returns matching schools for autocomplete.
    """
    if len(q) < 2:
        return {"schools": []}
    
    query_lower = q.lower()
    
    # First, search common schools list
    matching_schools = [
        school for school in COMMON_SCHOOLS
        if query_lower in school["name"].lower()
    ]
    
    # Then search schools collection in DB (schools added by users)
    try:
        db_schools = await db.schools.find(
            {"name": {"$regex": q, "$options": "i"}},
            {"_id": 0, "nces_id": 1, "name": 1, "city": 1, "state": 1, "grades": 1}
        ).limit(20).to_list(20)
        
        # Add DB schools that aren't duplicates
        existing_names = {s["name"].lower() for s in matching_schools}
        for school in db_schools:
            if school["name"].lower() not in existing_names:
                matching_schools.append(school)
    except Exception as e:
        logger.error(f"School DB search error: {e}")
    
    return {"schools": matching_schools[:20]}


@router.post("/set-school")
async def set_user_school(
    school_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """
    Set the user's school. Creates school in DB if not exists.
    """
    nces_id = school_data.get("nces_id")
    school_name = school_data.get("name")
    city = school_data.get("city", "")
    state = school_data.get("state", "")
    
    if not school_name:
        raise HTTPException(status_code=400, detail="School name is required")
    
    # Create display name with city/state for differentiation
    if city and state and state != "US":
        display_name = f"{school_name} ({city}, {state})"
    else:
        display_name = school_name
    
    # Save school to schools collection if not exists
    existing_school = await db.schools.find_one({"nces_id": nces_id})
    if not existing_school:
        await db.schools.insert_one({
            "nces_id": nces_id or f"custom_{school_name.lower().replace(' ', '_')}",
            "name": school_name,
            "display_name": display_name,
            "city": city,
            "state": state,
            "grades": school_data.get("grades", "8-12"),
            "created_at": datetime.now(timezone.utc).isoformat()
        })
    
    # Update user's school with full display name
    await db.users.update_one(
        {"id": current_user["id"]},
        {"$set": {
            "school_id": nces_id or f"custom_{school_name.lower().replace(' ', '_')}",
            "school_name": display_name,
            "school_base_name": school_name,
            "school_city": city,
            "school_state": state
        }}
    )
    
    return {"message": "School updated successfully", "school_name": display_name}


@router.delete("/remove-school")
async def remove_user_school(current_user: dict = Depends(get_current_user)):
    """Remove school from user's profile"""
    await db.users.update_one(
        {"id": current_user["id"]},
        {"$unset": {"school_id": "", "school_name": ""}}
    )
    return {"message": "School removed from profile"}


@router.get("/leaderboard")
async def get_school_leaderboard():
    """
    Get school leaderboard data:
    - Top schools by average consistency
    - Top schools by average performance  
    - Schools with most users
    """
    from utils.timezone import get_eastern_date
    from datetime import timedelta
    
    today = get_eastern_date()
    week_start = today - timedelta(days=today.weekday())  # Monday of current week
    
    # Get all users with schools
    users_with_schools = await db.users.find(
        {"school_id": {"$exists": True, "$ne": None}},
        {"_id": 0, "id": 1, "school_name": 1, "school_id": 1, "pillars": 1, "weekly_targets": 1}
    ).to_list(1000)
    
    if not users_with_schools:
        return {
            "top_consistency": [],
            "top_performance": [],
            "most_users": [],
            "last_updated": datetime.now(timezone.utc).isoformat()
        }
    
    # Calculate stats for each user
    school_stats = {}
    
    for user in users_with_schools:
        school_name = user.get("school_name", "Unknown")
        school_id = user.get("school_id")
        user_id = user["id"]
        
        if school_name not in school_stats:
            school_stats[school_name] = {
                "school_id": school_id,
                "users": [],
                "total_consistency": 0,
                "total_performance": 0
            }
        
        # Get this week's sessions for the user
        sessions = await db.daily_sessions.find({
            "user_id": user_id,
            "date": {"$gte": week_start.isoformat()}
        }, {"_id": 0, "date": 1, "pillar": 1}).to_list(100)
        
        # Calculate consistency (days active / 7)
        unique_days = len(set(s["date"] for s in sessions))
        days_in_week = min((today - week_start).days + 1, 7)
        consistency_pct = (unique_days / days_in_week * 100) if days_in_week > 0 else 0
        
        # Calculate target completion
        weekly_targets = user.get("weekly_targets", {})
        pillars = user.get("pillars", [])
        target_completion = 0
        
        if pillars and weekly_targets:
            pillar_session_counts = {}
            for s in sessions:
                pillar = s.get("pillar")
                pillar_session_counts[pillar] = pillar_session_counts.get(pillar, 0) + 1
            
            total_target = sum(weekly_targets.get(p, 3) for p in pillars)
            total_completed = sum(pillar_session_counts.get(p, 0) for p in pillars)
            target_completion = min((total_completed / total_target * 100) if total_target > 0 else 0, 100)
        
        # Performance index = 70% consistency + 30% target completion
        performance_index = min((consistency_pct * 0.7) + (target_completion * 0.3), 100)
        
        school_stats[school_name]["users"].append(user_id)
        school_stats[school_name]["total_consistency"] += consistency_pct
        school_stats[school_name]["total_performance"] += performance_index
    
    # Calculate averages and format results
    consistency_list = []
    performance_list = []
    user_count_list = []
    
    for school_name, data in school_stats.items():
        user_count = len(data["users"])
        avg_consistency = data["total_consistency"] / user_count if user_count > 0 else 0
        avg_performance = data["total_performance"] / user_count if user_count > 0 else 0
        
        consistency_list.append({
            "school_name": school_name,
            "school_id": data["school_id"],
            "avg_consistency": round(avg_consistency, 1),
            "user_count": user_count
        })
        
        performance_list.append({
            "school_name": school_name,
            "school_id": data["school_id"],
            "avg_performance": round(avg_performance, 1),
            "user_count": user_count
        })
        
        user_count_list.append({
            "school_name": school_name,
            "user_count": user_count
        })
    
    # Sort and rank
    consistency_list.sort(key=lambda x: x["avg_consistency"], reverse=True)
    performance_list.sort(key=lambda x: x["avg_performance"], reverse=True)
    user_count_list.sort(key=lambda x: x["user_count"], reverse=True)
    
    # Add ranks
    for i, item in enumerate(consistency_list[:10]):
        item["rank"] = i + 1
    for i, item in enumerate(performance_list[:10]):
        item["rank"] = i + 1
    for i, item in enumerate(user_count_list[:10]):
        item["rank"] = i + 1
    
    return {
        "top_consistency": consistency_list[:10],
        "top_performance": performance_list[:10],
        "most_users": user_count_list[:10],
        "last_updated": datetime.now(timezone.utc).isoformat()
    }


@router.get("/my-school-stats")
async def get_my_school_stats(current_user: dict = Depends(get_current_user)):
    """Get stats for the current user's school"""
    from utils.timezone import get_eastern_date
    from datetime import timedelta
    
    school_id = current_user.get("school_id")
    school_name = current_user.get("school_name")
    
    if not school_id:
        return {"has_school": False}
    
    today = get_eastern_date()
    week_start = today - timedelta(days=today.weekday())
    
    # Get all users at this school
    school_users = await db.users.find(
        {"school_id": school_id},
        {"_id": 0, "id": 1, "pillars": 1, "weekly_targets": 1, "current_streak": 1}
    ).to_list(1000)
    
    if not school_users:
        return {
            "has_school": True,
            "school_name": school_name,
            "total_users": 1,
            "avg_consistency": 0,
            "avg_performance": 0
        }
    
    total_consistency = 0
    total_performance = 0
    total_sessions = 0
    total_streak = 0
    
    for user in school_users:
        user_id = user["id"]
        
        # Get this week's sessions
        sessions = await db.daily_sessions.find({
            "user_id": user_id,
            "date": {"$gte": week_start.isoformat()}
        }, {"_id": 0, "date": 1, "pillar": 1}).to_list(100)
        
        total_sessions += len(sessions)
        total_streak += user.get("current_streak", 0)
        
        # Calculate consistency
        unique_days = len(set(s["date"] for s in sessions))
        days_in_week = min((today - week_start).days + 1, 7)
        consistency_pct = (unique_days / days_in_week * 100) if days_in_week > 0 else 0
        
        # Calculate target completion
        weekly_targets = user.get("weekly_targets", {})
        pillars = user.get("pillars", [])
        target_completion = 0
        
        if pillars and weekly_targets:
            pillar_session_counts = {}
            for s in sessions:
                pillar = s.get("pillar")
                pillar_session_counts[pillar] = pillar_session_counts.get(pillar, 0) + 1
            
            total_target = sum(weekly_targets.get(p, 3) for p in pillars)
            total_completed = sum(pillar_session_counts.get(p, 0) for p in pillars)
            target_completion = min((total_completed / total_target * 100) if total_target > 0 else 0, 100)
        
        performance_index = min((consistency_pct * 0.7) + (target_completion * 0.3), 100)
        
        total_consistency += consistency_pct
        total_performance += performance_index
    
    user_count = len(school_users)
    
    return {
        "has_school": True,
        "school_name": school_name,
        "total_users": user_count,
        "avg_consistency": round(total_consistency / user_count, 1) if user_count > 0 else 0,
        "avg_performance": round(total_performance / user_count, 1) if user_count > 0 else 0,
        "total_sessions": total_sessions,
        "avg_streak": round(total_streak / user_count, 1) if user_count > 0 else 0
    }
