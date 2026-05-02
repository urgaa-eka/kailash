from typing import Dict, Any, List
from datetime import datetime
from . import BaseGuardian

class ParvatiGuardian(BaseGuardian):
    """PARVATI - Workload Guardian - PASSIVE OBSERVER MODE"""
    
    def __init__(self):
        super().__init__("PARVATI", "workload")
        self.department_loads = {}
        self.rebalance_threshold = 0.8
    
    async def monitor(self) -> Dict[str, Any]:
        """Monitor workload distribution - PASSIVE OBSERVATION ONLY"""
        from ..core.database import get_mongo_db
        
        db = await get_mongo_db()
        workload_status = []
        
        if db is not None:
            departments = await db.departments.find({"is_active": True}).to_list(100)
            
            for dept in departments:
                dept_id = str(dept.get("id", dept.get("_id", "")))
                
                active_tasks = await db.tasks.count_documents({
                    "department_id": dept_id,
                    "status": {"$in": ["pending", "in_progress"]}
                })
                
                queue_depth = 0  # Redis removed from stack
                
                max_capacity = dept.get("max_concurrent_tasks", 20)
                load = (active_tasks + queue_depth) / max_capacity if max_capacity > 0 else 0
                self.department_loads[dept_id] = load
                
                workload_status.append({
                    "department": dept.get("name", dept_id),
                    "department_id": dept_id,
                    "active_tasks": active_tasks,
                    "queue_depth": queue_depth,
                    "load_percentage": round(load * 100, 2),
                    "status": "overloaded" if load > self.rebalance_threshold else "normal"
                })
        
        return {
            "guardian": "PARVATI",
            "philosophy": "Shakti - Nurturing Observation",
            "mode": "PASSIVE_OBSERVER",
            "departments_monitored": len(workload_status),
            "workload_status": workload_status,
            "imbalance_detected": any(d["load_percentage"] > 80 for d in workload_status),
            "timestamp": datetime.utcnow().isoformat(),
            "note": "PARVATI observes and reports imbalances - rebalancing requires CEO direction"
        }
    
    async def intervene(self, issue: Dict[str, Any]) -> Dict[str, Any]:
        """DISABLED - PARVATI is passive observer"""
        return {
            "action_taken": "DISABLED - PARVATI is passive observer",
            "success": False,
            "note": "Rebalancing must be requested by CEO through GANESHA"
        }
    
    async def report(self) -> Dict[str, Any]:
        """Generate workload report - PASSIVE OBSERVATION ONLY"""
        from ..core.database import get_mongo_db
        
        db = await get_mongo_db()
        total_tasks = 0
        completed_today = 0
        if db is not None:
            total_tasks = await db.tasks.count_documents({"status": {"$ne": "completed"}})
            completed_today = await db.tasks.count_documents({
                "status": "completed",
                "completed_at": {"$gte": datetime.utcnow().replace(hour=0, minute=0, second=0)}
            })
        
        avg_load = sum(self.department_loads.values()) / max(len(self.department_loads), 1)
        
        return {
            "guardian": "PARVATI",
            "philosophy": "Shakti - Nurturing Observation",
            "mode": "PASSIVE_OBSERVER",
            "total_active_tasks": total_tasks,
            "completed_today": completed_today,
            "average_system_load": round(avg_load * 100, 2),
            "department_loads": self.department_loads,
            "note": "PARVATI observes and reports only - does not auto-rebalance"
        }
    
    async def _rebalance_tasks(self, dept_id: str) -> Dict[str, Any]:
        """DISABLED - PARVATI is passive observer, does not auto-rebalance"""
        return {
            "action_taken": "DISABLED - PARVATI is passive observer",
            "success": False,
            "note": "Rebalancing must be requested by CEO through GANESHA"
        }

parvati_guardian = ParvatiGuardian()
