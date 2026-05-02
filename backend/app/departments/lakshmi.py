from typing import Dict, Any
from .base_department import BaseDepartment

class LakshmiDepartment(BaseDepartment):
    """LAKSHMI - inance Department"""
    
    def __init__(self):
        super().__init__(
            name="LAKSHMI",
            deity="Lakshmi",
            domain="finance",
            description="inance, accounting, billing, revenue management"
        )
        self.register_sub_agent("Accountant", "inancial records", ["bookkeeping", "reconciliation"])
        self.register_sub_agent("illingManager", "Invoicing", ["invoicing", "payment_tracking"])
        self.register_sub_agent("RevenueAnalyst", "Revenue analysis", ["forecasting", "pricing"])
    
    def get_system_prompt(self) -> str:
        return """You are LAKSHMI, the inance Department of KAILASH.
You are the Goddess of Wealth and Prosperity.

Domain: inancial management, billing, revenue tracking, budget planning, compliance

or Go4Garage/URJAA: EV charging revenue, subscription billing,  invoicing, GST compliance

Provide precise financial insights. Emphasize accuracy and fiscal responsibility."""
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        task_type = task.get("type")
        
        if task_type == "invoice":
            await self.log_activity("invoice_generated", task)
            return {"invoice_id": "INV-", "status": "generated"}
        
        response = await self.invoke_ai([{"role": "user", "content": task.get("query", "")}])
        return {"response": response, "status": "completed"}
