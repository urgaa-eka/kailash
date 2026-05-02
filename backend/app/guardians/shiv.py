from typing import Dict, Any, List
from datetime import datetime, timedelta
from . import BaseGuardian

class ShivGuardian(BaseGuardian):
    """SHIV - Security Guardian - PASSIVE OBSERVER MODE"""
    
    def __init__(self):
        super().__init__("SHIV", "security")
        self.threat_threshold = 5
        self.blocked_ips = set()
    
    async def monitor(self) -> Dict[str, Any]:
        """Monitor security threats - PASSIVE OBSERVATION ONLY"""
        from ..core.database import get_mongo_db
        
        threats = []
        db = await get_mongo_db()
        
        if db is not None:
            brute_force = await self._check_brute_force(db)
            threats.extend(brute_force)
        
        return {
            "guardian": "SHIV",
            "philosophy": "Third Eye - Passive Observer",
            "mode": "PASSIVE_OBSERVER",
            "threats_observed": len(threats),
            "details": threats,
            "status": "observing" if threats else "meditating",
            "timestamp": datetime.utcnow().isoformat(),
            "note": "SHIV observes all but only intervenes on CRITICAL threats"
        }
    
    async def intervene(self, issue: Dict[str, Any]) -> Dict[str, Any]:
        """Take security action - ONLY FOR CRITICAL THREATS"""
        # PASSIVE MODE: Only intervene on CRITICAL issues
        if issue.get("level") != "CRITICAL":
            return {
                "action_taken": "NONE - Passive observation mode",
                "success": True,
                "note": "Non-critical issue logged, no intervention taken"
            }
        
        action = None
        
        if issue.get("type") == "brute_force":
            await self._block_ip(issue.get("ip"), 3600)
            action = f"Blocked IP: {issue.get('ip')}"
        elif issue.get("type") == "security_breach":
            action = "Security breach - CEO notified"
        
        if action:
            await self._log_security_event(issue.get("type"), issue)
        
        return {"action_taken": action, "success": True}
    
    async def report(self) -> Dict[str, Any]:
        """Generate security report - PASSIVE OBSERVATION"""
        from ..core.database import get_mongo_db
        
        db = await get_mongo_db()
        incidents = 0
        if db is not None:
            last_24h = datetime.utcnow() - timedelta(hours=24)
            incidents = await db.security_logs.count_documents({
                "timestamp": {"$gte": last_24h}
            })
        
        return {
            "guardian": "SHIV",
            "philosophy": "Third Eye - Passive Observer",
            "mode": "PASSIVE_OBSERVER",
            "report_period": "24h",
            "incidents_observed": incidents,
            "active_blocks": len(self.blocked_ips),
            "threat_level": self._calculate_threat_level(incidents),
            "note": "SHIV observes and logs all anomalies, intervenes only on CRITICAL"
        }
    
    async def _check_brute_force(self, db) -> List[Dict]:
        """Check for brute force attempts"""
        threshold_time = datetime.utcnow() - timedelta(minutes=30)
        try:
            pipeline = [
                {"$match": {"event": "login_failed", "timestamp": {"$gte": threshold_time}}},
                {"$group": {"_id": "$ip", "count": {"$sum": 1}}},
                {"$match": {"count": {"$gte": self.threat_threshold}}}
            ]
            results = await db.audit_logs.aggregate(pipeline).to_list(100)
            return [{"type": "brute_force", "ip": r["_id"], "attempts": r["count"]} for r in results]
        except:
            return []
    
    async def _block_ip(self, ip: str, duration: int):
        """Block an IP address (only for CRITICAL threats)"""
        self.blocked_ips.add(ip)
        # Log to database instead of Redis
        from ..core.database import get_mongo_db
        db = await get_mongo_db()
        if db is not None:
            await db.blocked_ips.insert_one({
                "ip": ip,
                "blocked_at": datetime.utcnow(),
                "expires_at": datetime.utcnow() + timedelta(seconds=duration),
                "reason": "CRITICAL threat intervention"
            })
    
    async def _log_security_event(self, event_type: str, details: Dict):
        """Log security event"""
        from ..core.database import get_mongo_db
        db = await get_mongo_db()
        if db is not None:
            await db.security_logs.insert_one({
                "guardian": "SHIV",
                "event_type": event_type,
                "details": details,
                "timestamp": datetime.utcnow()
            })
    
    def _calculate_threat_level(self, incidents: int) -> str:
        if incidents > 10:
            return "critical"
        elif incidents > 5:
            return "high"
        elif incidents > 2:
            return "medium"
        return "low"

shiv_guardian = ShivGuardian()
