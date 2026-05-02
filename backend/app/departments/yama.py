from typing import Dict, Any
from .base_department import BaseDepartment

class YamaDepartment(BaseDepartment):
    def __init__(self):
        super().__init__("YAMA", "Yama", "compliance", "Audits, regulations, policy enforcement")
        self.register_sub_agent("ComplianceOfficer", "Compliance", ["compliance", "audits"])
        self.register_sub_agent("LegalAdvisor", "Legal", ["legal", "contracts"])
        self.register_sub_agent("RegulatoryTracker", "Regulatory", ["regulations", "tracking"])
    
    def get_system_prompt(self) -> str:
        return "You are YAMA, the Compliance Department. Audits, regulations, policy enforcement."
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        response = await self.invoke_ai([{"role": "user", "content": task.get("query", "")}])
        return {"response": response, "status": "completed"}
