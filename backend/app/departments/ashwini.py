from typing import Dict, Any
from .base_department import BaseDepartment

class AshwiniDepartment(BaseDepartment):
    def __init__(self):
        super().__init__("ASHWINI", "Ashwini Kumaras", "health", "System health, monitoring, diagnostics")
        self.register_sub_agent("HealthMonitor", "Health", ["health", "monitoring"])
        self.register_sub_agent("DiagnosticsEngine", "Diagnostics", ["diagnostics", "troubleshooting"])
        self.register_sub_agent("PerformanceTracker", "Performance", ["performance", "metrics"])
    
    def get_system_prompt(self) -> str:
        return "You are ASHWINI, the Health Department. System health, monitoring, diagnostics."
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        response = await self.invoke_ai([{"role": "user", "content": task.get("query", "")}])
        return {"response": response, "status": "completed"}
