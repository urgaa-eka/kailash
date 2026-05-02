from typing import Dict, Any
from .base_department import BaseDepartment

class AgniDepartment(BaseDepartment):
    def __init__(self):
        super().__init__("AGNI", "Agni", "crisis", "Incident response, escalation, emergency protocols")
        self.register_sub_agent("CrisisManager", "Crisis", ["crisis", "emergency"])
        self.register_sub_agent("EscalationHandler", "Escalation", ["escalation", "priority"])
        self.register_sub_agent("IncidentResponse", "Incidents", ["incidents", "response"])
    
    def get_system_prompt(self) -> str:
        return "You are AGNI, the Crisis Department. Incident response, escalation, emergency protocols."
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        response = await self.invoke_ai([{"role": "user", "content": task.get("query", "")}])
        return {"response": response, "status": "completed"}
