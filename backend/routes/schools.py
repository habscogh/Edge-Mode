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

# Cache for school search results (simple in-memory cache)
school_cache = {}
CACHE_TTL = 3600  # 1 hour

async def search_schools_urban_institute(query: str, state: Optional[str] = None):
    """
    Search US schools using Urban Institute Education Data Portal API
    Filters for grades 8-12 (middle/high schools)
    """
    cache_key = f"{query}_{state}"
    
    # Check cache
    if cache_key in school_cache:
        cached_data, cached_time = school_cache[cache_key]
        if (datetime.now() - cached_time).seconds < CACHE_TTL:
            return cached_data
    
    try:
        # Urban Institute API for school directory
        # Filter for schools that have grades 8-12
        base_url = "https://educationdata.urban.org/api/v1/schools/ccd/directory"
        
        # Get latest year available
        year = 2022  # Latest stable year in the API
        
        params = {
            "year": year,
            "school_name": query,
        }
        
        if state:
            params["state_location"] = state.upper()
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(base_url, params=params)
            
            if response.status_code != 200:
                logger.error(f"Urban Institute API error: {response.status_code}")
                return []
            
            data = response.json()
            results = data.get("results", [])
            
            # Filter for schools with grades 8-12
            filtered_schools = []
            for school in results[:50]:  # Limit to 50 results
                # Check if school has any grades 8-12
                lowest_grade = school.get("lowest_grade_offered", 0)
                highest_grade = school.get("highest_grade_offered", 0)
                
                # We want schools that include grades 8-12
                # Grade codes: 8=8th grade, 9-12 are high school
                if highest_grade >= 8:
                    filtered_schools.append({
                        "nces_id": school.get("ncessch"),
                        "name": school.get("school_name", "").title(),
                        "city": school.get("city_location", "").title(),
                        "state": school.get("state_location", ""),
                        "zip": school.get("zip_location", ""),
                        "grades": f"{lowest_grade}-{highest_grade}",
                        "school_type": school.get("school_type", ""),
                    })
            
            # Cache results
            school_cache[cache_key] = (filtered_schools, datetime.now())
            
            return filtered_schools[:20]  # Return top 20 matches
            
    except Exception as e:
        logger.error(f"School search error: {e}")
        return []


# Fallback: Use a static list of popular schools if API fails
FALLBACK_SCHOOLS = [
    {"nces_id": "fallback_1", "name": "Lincoln High School", "city": "Various", "state": "US", "grades": "9-12"},
    {"nces_id": "fallback_2", "name": "Washington High School", "city": "Various", "state": "US", "grades": "9-12"},
    {"nces_id": "fallback_3", "name": "Jefferson High School", "city": "Various", "state": "US", "grades": "9-12"},
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
    
    # Try Urban Institute API first
    schools = await search_schools_urban_institute(q, state)
    
    # If API fails or returns nothing, search local database
    if not schools:
        # Search our own database of schools that users have selected
        local_schools = await db.schools.find(
            {"name": {"$regex": q, "$options": "i"}},
            {"_id": 0, "nces_id": 1, "name": 1, "city": 1, "state": 1, "grades": 1}
        ).limit(20).to_list(20)
        
        if local_schools:
            schools = local_schools
    
    return {"schools": schools}


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
