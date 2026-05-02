"""Live Data API endpoints for real-time external API connections."""
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Optional
from datetime import datetime, timezone

from ..api.deps import get_current_user
from ..services.live_api_connector import get_connector
from ..core.mongodb import MongoD

router = APIRouter(prefix="/api/live-data", tags=["Live Data"])


@router.get("/department/{department_name}")
async def get_department_live_data(
    department_name: str,
    current_user: dict = Depends(get_current_user)
):
    """Fetch live data from external APIs for a specific department."""
    connector = get_connector()
    data = await connector.fetch_department_live_data(department_name)
    return data


@router.get("/rbi")
async def get_rbi_data(current_user: dict = Depends(get_current_user)):
    """Fetch RBI monetary policy data."""
    connector = get_connector()
    return await connector.fetch_rbi_policy_data()


@router.get("/gst")
async def get_gst_data(current_user: dict = Depends(get_current_user)):
    """Fetch GST compliance updates."""
    connector = get_connector()
    return await connector.fetch_gst_updates()


@router.get("/stripe")
async def get_stripe_data(current_user: dict = Depends(get_current_user)):
    """Fetch Stripe payment analytics."""
    connector = get_connector()
    return await connector.fetch_stripe_data()


@router.get("/weather/{city}")
async def get_weather_data(
    city: str = "Mumbai",
    current_user: dict = Depends(get_current_user)
):
    """Fetch weather data for energy forecasting."""
    connector = get_connector()
    return await connector.fetch_weather_data(city)


@router.get("/security/cve")
async def get_cve_data(current_user: dict = Depends(get_current_user)):
    """Fetch latest CVE vulnerabilities."""
    connector = get_connector()
    return await connector.fetch_security_vulnerabilities()


@router.get("/github/trends")
async def get_github_trends(current_user: dict = Depends(get_current_user)):
    """Fetch GitHub trending repositories."""
    connector = get_connector()
    return await connector.fetch_github_trends()


@router.get("/economic/{country}")
async def get_economic_indicators(
    country: str = "IN",
    current_user: dict = Depends(get_current_user)
):
    """Fetch economic indicators from World Bank."""
    connector = get_connector()
    return await connector.fetch_economic_indicators(country)


@router.post("/refresh-all")
async def refresh_all_live_data(
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Trigger a refresh of all live data sources and store in database."""
    
    async def refresh_and_store():
        connector = get_connector()
        db = MongoD.get_database()
        
        departments = [
            "lakshmi", "vishwakarma", "indra", "surya", "agni", 
            "tvashta", "kartikeya", "kubera", "yama"
        ]
        
        for dept in departments:
            try:
                data = await connector.fetch_department_live_data(dept)
                
                # Store in database
                await db.live_data_cache.update_one(
                    {"department": dept},
                    {
                        "$set": {
                            "department": dept,
                            "data": data,
                            "last_updated": datetime.now(timezone.utc).isoformat()
                        }
                    },
                    upsert=True
                )
            except Exception as e:
                print(f"Error refreshing {dept}: {e}")
    
    background_tasks.add_task(refresh_and_store)
    
    return {
        "status": "success",
        "message": "Live data refresh started in background"
    }


@router.get("/cached/{department_name}")
async def get_cached_live_data(
    department_name: str,
    current_user: dict = Depends(get_current_user)
):
    """Get cached live data for a department."""
    db = MongoD.get_database()
    
    cached = await db.live_data_cache.find_one(
        {"department": department_name.lower()},
        {"_id": 0}
    )
    
    if not cached:
        # Fetch fresh if not cached
        connector = get_connector()
        data = await connector.fetch_department_live_data(department_name)
        return {"data": data, "cached": False}
    
    return {"data": cached.get("data"), "cached": True, "last_updated": cached.get("last_updated")}
