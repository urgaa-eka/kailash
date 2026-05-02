from typing import Dict, Any
from .base_department import BaseDepartment

class KuberaDepartment(BaseDepartment):
    def __init__(self):
        super().__init__("KUERA", "Kubera", "treasury", "Payments, billing, financial tracking")
        self.register_sub_agent("AssetManager", "Assets", ["assets", "portfolio"])
        self.register_sub_agent("InvestmentAdvisor", "Investments", ["investments", "advisory"])
        self.register_sub_agent("CashlowManager", "Cash flow", ["cashflow", "treasury"])
    
    def get_system_prompt(self) -> str:
        return "You are KUERA, the Treasury Department. Payments, billing, financial tracking."
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        response = await self.invoke_ai([{"role": "user", "content": task.get("query", "")}])
        return {"response": response, "status": "completed"}
