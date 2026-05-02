from typing import Dict, Any
from .base_department import BaseDepartment

class DharmaDepartment(BaseDepartment):
    def __init__(self):
        super().__init__("DHARMA", "Dharma", "governance", "Ethics, policies, compliance oversight")
        self.register_sub_agent("PolicyManager", "Policy", ["policy", "governance"])
        self.register_sub_agent("EthicsAdvisor", "Ethics", ["ethics", "conduct"])
        self.register_sub_agent("GovernanceOfficer", "Governance", ["governance", "oversight"])
    
    def get_system_prompt(self) -> str:
        return "You are DHARMA, the Governance Department. Ethics, policies, compliance oversight."
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        response = await self.invoke_ai([{"role": "user", "content": task.get("query", "")}])
        return {"response": response, "status": "completed"}
