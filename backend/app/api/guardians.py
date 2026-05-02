from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any

from ..api.deps import get_current_active_user
from ..models.user import User
from ..guardians.shiv import shiv_guardian
from ..guardians.parvati import parvati_guardian

router = APIRouter(prefix="/guardians", tags=["Guardians"])

@router.get("/status")
async def get_guardians_status(current_user: User = Depends(get_current_active_user)):
    """Get status of all three guardians"""
    return {
        "SHIV": await shiv_guardian.heartbeat(),
        "PARVATI": await parvati_guardian.heartbeat(),
        "GANESHA": {"guardian": "GANESHA", "status": "active"}
    }

@router.get("/shiv/monitor")
async def shiv_monitor(current_user: User = Depends(get_current_active_user)):
    """Get SHIV security monitoring status"""
    return await shiv_guardian.monitor()

@router.get("/shiv/report")
async def shiv_report(current_user: User = Depends(get_current_active_user)):
    """Get SHIV security report"""
    return await shiv_guardian.report()

@router.get("/parvati/monitor")
async def parvati_monitor(current_user: User = Depends(get_current_active_user)):
    """Get PARVATI workload monitoring"""
    return await parvati_guardian.monitor()

@router.get("/parvati/report")
async def parvati_report(current_user: User = Depends(get_current_active_user)):
    """Get PARVATI workload report"""
    return await parvati_guardian.report()

@router.post("/shiv/block-ip")
async def block_ip(ip: str, duration: int = 3, current_user: User = Depends(get_current_active_user)):
    """Manually block an IP address"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    await shiv_guardian.intervene({"type": "brute_force", "ip": ip})
    return {"message": f"IP {ip} blocked for {duration} seconds"}
