"""Automobile Industry API Router"""

from fastapi import APIRouter, Query, HTTPException, Depends
from typing import Optional, List, Dict, Any
from .pricing_engine import pricing_engine
from .market_data import market_data_collector
from .gst_integration import gst_software_client
from ..api.deps import get_current_active_user
from ..models.user import User

router = APIRouter(prefix="/automobile", tags=["Automobile Industry Module"])

@router.get("/pricing/uniform")
async def get_uniform_price(
    service_type: str = Query(..., description="Service type (e.g., oil_change)"),
    vehicle_type: str = Query(..., description="Vehicle type (e.g., sedan, suv)"),
    region: Optional[str] = Query(None, description="Region filter"),
    current_user: User = Depends(get_current_active_user)
):
    """Get uniform price for a service using Market + GST data fusion"""
    result = await pricing_engine.calculate_uniform_price(service_type, vehicle_type, region)
    
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return result

@router.get("/pricing/table/{vehicle_type}")
async def get_pricing_table(
    vehicle_type: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get complete pricing table for a vehicle type"""
    pricing = await pricing_engine.get_service_pricing_table(vehicle_type)
    
    return {
        "vehicle_type": vehicle_type,
        "services": len(pricing),
        "pricing": pricing
    }

@router.get("/pricing/trends/{service_type}")
async def get_pricing_trends(
    service_type: str,
    days: int = Query(default=30, ge=7, le=365, description="Days to analyze"),
    current_user: User = Depends(get_current_active_user)
):
    """Get pricing trends for a service over time"""
    result = await pricing_engine.analyze_pricing_trends(service_type, days)
    
    if "error" in result:
        raise HTTPException(status_code=404, detail=result.get("error", "Insufficient data"))
    
    return result

@router.get("/market/insights/{vehicle_type}")
async def get_market_insights(
    vehicle_type: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get aggregated market insights for a vehicle type"""
    return await market_data_collector.get_market_insights(vehicle_type)

@router.post("/market/update")
async def update_market_data(
    data: List[Dict[str, Any]],
    current_user: User = Depends(get_current_active_user)
):
    """Bulk update market pricing data"""
    result = await market_data_collector.update_market_data(data)
    return result

@router.post("/market/sample-data")
async def add_sample_market_data(
    current_user: User = Depends(get_current_active_user)
):
    """Add sample market data for testing"""
    result = await market_data_collector.add_sample_data()
    return result

@router.post("/gst/sync")
async def sync_gst_data(
    days: int = Query(default=30, ge=1, le=90, description="Days to sync"),
    current_user: User = Depends(get_current_active_user)
):
    """Sync job cards from external GST software"""
    result = await gst_software_client.sync_job_cards(days)
    return result

@router.get("/gst/analysis")
async def get_job_card_analysis(
    service_type: Optional[str] = Query(None, description="Filter by service type"),
    vehicle_type: Optional[str] = Query(None, description="Filter by vehicle type"),
    current_user: User = Depends(get_current_active_user)
):
    """Analyze job card data with optional filters"""
    filters = {}
    if service_type:
        filters["service_type"] = service_type
    if vehicle_type:
        filters["vehicle_type"] = vehicle_type
    
    return await gst_software_client.analyze_job_cards(filters)

@router.post("/gst/sample-data")
async def add_sample_job_cards(
    current_user: User = Depends(get_current_active_user)
):
    """Add sample job card data for testing"""
    result = await gst_software_client.add_sample_job_cards()
    return result

@router.get("/health")
async def automobile_module_health():
    """Health check for automobile module"""
    return {
        "module": "Automobile Industry",
        "status": "operational",
        "features": [
            "Uniform Pricing Engine",
            "Market Data Collection",
            "GST Software Integration",
            "Pricing Trends Analysis"
        ],
        "version": "2.0.0"
    }
