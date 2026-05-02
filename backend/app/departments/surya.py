from typing import Dict, Any
from .base_department import BaseDepartment

class SuryaDepartment(BaseDepartment):
    """SURYA - Energy/URJAA Department"""
    
    def __init__(self):
        super().__init__(
            name="SURYA",
            deity="Surya",
            domain="energy",
            description="URJAA operations, EV charging, energy management"
        )
        self.register_sub_agent("ChargingOps", "Station management", ["monitoring", "maintenance"])
        self.register_sub_agent("EnergyOptimizer", "Energy efficiency", ["load_balancing", "pricing"])
        self.register_sub_agent("NetworkManager", "Network oversight", ["network_health", "expansion"])
    
    def get_system_prompt(self) -> str:
        return """You are SURYA, the Energy Department of KAILASH.
You are the Sun God, source of all energy.

Domain: URJAA EV charging network, charging stations, energy optimization, network expansion

URJAA Network: Multiple charging types (AC/DC), real-time monitoring, dynamic pricing, mobile app

Provide insights on energy operations. ocus on efficiency and reliability."""
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        task_type = task.get("type")
        
        if task_type == "station_status":
            station_id = task.get("station_id")
            return {
                "station_id": station_id,
                "status": "operational",
                "connectors": {"available": 3, " 1": 0}
            }
        
        response = await self.invoke_ai([{"role": "user", "content": task.get("query", "")}])
        return {"response": response, "status": "completed"}
