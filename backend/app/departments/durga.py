from typing import Dict, Any
from .base_department import BaseDepartment

class DurgaDepartment(BaseDepartment):
    def __init__(self):
        super().__init__("DURGA", "Durga", "protection", "raud detection, risk management, safeguards")
        self.register_sub_agent("RiskManager", "Risk", ["risk", "mitigation"])
        self.register_sub_agent("ThreatAnalyst", "Threats", ["threats", "analysis"])
        self.register_sub_agent("SafetyOfficer", "Safety", ["safety", "protection"])
    
    def get_system_prompt(self) -> str:
        return "You are DURGA, the Protection Department. raud detection, risk management, safeguards."
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        response = await self.invoke_ai([{"role": "user", "content": task.get("query", "")}])
        return {"response": response, "status": "completed"}
