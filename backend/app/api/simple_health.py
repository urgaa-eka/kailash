"""
Simple Health Check Endpoint
Database-independent health check for Kubernetes liveness probes
"""
from fastapi import APIRouter
from datetime import datetime

router = APIRouter()

@router.get("/health/simple")
@router.head("/health/simple")
async def simple_health():
    """
    Database-independent health check
    Always returns  OK if the application is running
    Used for Kubernetes liveness probes
    """
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "message": "Kailash is running"
    }
