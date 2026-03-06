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

# Common US high schools - seed data for autocomplete
# In production, this would be populated from NCES database
COMMON_SCHOOLS = [
    {"nces_id": "hs_001", "name": "Lincoln High School", "city": "Various", "state": "US", "grades": "9-12"},
    {"nces_id": "hs_002", "name": "Washington High School", "city": "Various", "state": "US", "grades": "9-12"},
    {"nces_id": "hs_003", "name": "Jefferson High School", "city": "Various", "state": "US", "grades": "9-12"},
    {"nces_id": "hs_004", "name": "Roosevelt High School", "city": "Various", "state": "US", "grades": "9-12"},
    {"nces_id": "hs_005", "name": "Kennedy High School", "city": "Various", "state": "US", "grades": "9-12"},
    {"nces_id": "hs_006", "name": "Central High School", "city": "Various", "state": "US", "grades": "9-12"},
    {"nces_id": "hs_007", "name": "West High School", "city": "Various", "state": "US", "grades": "9-12"},
    {"nces_id": "hs_008", "name": "East High School", "city": "Various", "state": "US", "grades": "9-12"},
    {"nces_id": "hs_009", "name": "North High School", "city": "Various", "state": "US", "grades": "9-12"},
    {"nces_id": "hs_010", "name": "South High School", "city": "Various", "state": "US", "grades": "9-12"},
    {"nces_id": "hs_011", "name": "Westview High School", "city": "Various", "state": "US", "grades": "9-12"},
    {"nces_id": "hs_012", "name": "Eastview High School", "city": "Various", "state": "US", "grades": "9-12"},
    {"nces_id": "hs_013", "name": "Lakewood High School", "city": "Various", "state": "US", "grades": "9-12"},
    {"nces_id": "hs_014", "name": "Riverside High School", "city": "Various", "state": "US", "grades": "9-12"},
    {"nces_id": "hs_015", "name": "Mountain View High School", "city": "Various", "state": "US", "grades": "9-12"},
    {"nces_id": "hs_016", "name": "Valley High School", "city": "Various", "state": "US", "grades": "9-12"},
    {"nces_id": "hs_017", "name": "Fairview High School", "city": "Various", "state": "US", "grades": "9-12"},
    {"nces_id": "hs_018", "name": "Hillcrest High School", "city": "Various", "state": "US", "grades": "9-12"},
    {"nces_id": "hs_019", "name": "Oakwood High School", "city": "Various", "state": "US", "grades": "9-12"},
    {"nces_id": "hs_020", "name": "Parkview High School", "city": "Various", "state": "US", "grades": "9-12"},
    {"nces_id": "ms_001", "name": "Lincoln Middle School", "city": "Various", "state": "US", "grades": "6-8"},
    {"nces_id": "ms_002", "name": "Washington Middle School", "city": "Various", "state": "US", "grades": "6-8"},
    {"nces_id": "ms_003", "name": "Jefferson Middle School", "city": "Various", "state": "US", "grades": "6-8"},
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
    
    if not school_name:
        raise HTTPException(status_code=400, detail="School name is required")
    
    # Save school to schools collection if not exists
    existing_school = await db.schools.find_one({"nces_id": nces_id})
    if not existing_school:
        await db.schools.insert_one({
            "nces_id": nces_id or f"custom_{school_name.lower().replace(' ', '_')}",
            "name": school_name,
            "city": school_data.get("city", ""),
            "state": school_data.get("state", ""),
            "grades": school_data.get("grades", "8-12"),
            "created_at": datetime.now(timezone.utc).isoformat()
        })
    
    # Update user's school
    await db.users.update_one(
        {"id": current_user["id"]},
        {"$set": {
            "school_id": nces_id or f"custom_{school_name.lower().replace(' ', '_')}",
            "school_name": school_name
        }}
    )
    
    return {"message": "School updated successfully", "school_name": school_name}


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
    
    # Get all users with schools
    pipeline_consistency = [
        {"$match": {"school_id": {"$exists": True, "$ne": None}}},
        {"$group": {
            "_id": "$school_name",
            "school_id": {"$first": "$school_id"},
            "avg_consistency": {"$avg": "$weekly_consistency"},
            "user_count": {"$sum": 1}
        }},
        {"$match": {"user_count": {"$gte": 1}}},  # At least 1 user (can increase later)
        {"$sort": {"avg_consistency": -1}},
        {"$limit": 10}
    ]
    
    pipeline_performance = [
        {"$match": {"school_id": {"$exists": True, "$ne": None}}},
        {"$group": {
            "_id": "$school_name",
            "school_id": {"$first": "$school_id"},
            "avg_performance": {"$avg": "$performance_index"},
            "user_count": {"$sum": 1}
        }},
        {"$match": {"user_count": {"$gte": 1}}},
        {"$sort": {"avg_performance": -1}},
        {"$limit": 10}
    ]
    
    pipeline_most_users = [
        {"$match": {"school_id": {"$exists": True, "$ne": None}}},
        {"$group": {
            "_id": "$school_name",
            "school_id": {"$first": "$school_id"},
            "user_count": {"$sum": 1}
        }},
        {"$sort": {"user_count": -1}},
        {"$limit": 10}
    ]
    
    try:
        top_consistency = await db.users.aggregate(pipeline_consistency).to_list(10)
        top_performance = await db.users.aggregate(pipeline_performance).to_list(10)
        most_users = await db.users.aggregate(pipeline_most_users).to_list(10)
        
        # Format results
        def format_result(item, rank, metric_name, metric_key):
            return {
                "rank": rank,
                "school_name": item["_id"],
                "school_id": item.get("school_id"),
                metric_name: round(item.get(metric_key, 0) or 0, 1),
                "user_count": item.get("user_count", 0)
            }
        
        return {
            "top_consistency": [
                format_result(item, i+1, "avg_consistency", "avg_consistency")
                for i, item in enumerate(top_consistency)
            ],
            "top_performance": [
                format_result(item, i+1, "avg_performance", "avg_performance")
                for i, item in enumerate(top_performance)
            ],
            "most_users": [
                {"rank": i+1, "school_name": item["_id"], "user_count": item["user_count"]}
                for i, item in enumerate(most_users)
            ],
            "last_updated": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"School leaderboard error: {e}")
        return {
            "top_consistency": [],
            "top_performance": [],
            "most_users": [],
            "last_updated": datetime.now(timezone.utc).isoformat()
        }


@router.get("/my-school-stats")
async def get_my_school_stats(current_user: dict = Depends(get_current_user)):
    """Get stats for the current user's school"""
    school_id = current_user.get("school_id")
    school_name = current_user.get("school_name")
    
    if not school_id:
        return {"has_school": False}
    
    # Get school stats
    pipeline = [
        {"$match": {"school_id": school_id}},
        {"$group": {
            "_id": "$school_id",
            "total_users": {"$sum": 1},
            "avg_consistency": {"$avg": "$weekly_consistency"},
            "avg_performance": {"$avg": "$performance_index"},
            "total_sessions": {"$sum": "$total_sessions_completed"},
            "avg_streak": {"$avg": "$current_streak"}
        }}
    ]
    
    result = await db.users.aggregate(pipeline).to_list(1)
    
    if not result:
        return {
            "has_school": True,
            "school_name": school_name,
            "total_users": 1,
            "avg_consistency": current_user.get("weekly_consistency", 0),
            "avg_performance": current_user.get("performance_index", 0)
        }
    
    stats = result[0]
    return {
        "has_school": True,
        "school_name": school_name,
        "total_users": stats.get("total_users", 0),
        "avg_consistency": round(stats.get("avg_consistency", 0) or 0, 1),
        "avg_performance": round(stats.get("avg_performance", 0) or 0, 1),
        "total_sessions": stats.get("total_sessions", 0),
        "avg_streak": round(stats.get("avg_streak", 0) or 0, 1)
    }
