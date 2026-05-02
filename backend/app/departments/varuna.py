from typing import Dict, Any
from .base_department import BaseDepartment

class VarunaDepartment(BaseDepartment):
    """VARUNA - Customer Success Department"""
    
    def __init__(self):
        super().__init__(
            "VARUNA", 
            "Varuna", 
            "customer_success", 
            "Customer experience, support, and retention"
        )
        self.register_sub_agent("CustomerAdvocate", "Customer Advocacy", ["customer_success", "experience"])
        self.register_sub_agent("SupportSpecialist", "Support", ["support", "tickets", "resolution"])
        self.register_sub_agent("RetentionExpert", "Retention", ["retention", "loyalty", "satisfaction"])
    
    def get_system_prompt(self) -> str:
        return """You are VARUNA, the Customer Success Department of KAILASH.
You are the Lord of Waters, ensuring smooth flow of customer relationships.

Domain: Customer experience, support, retention, satisfaction
Responsibilities:
- Customer support and ticket resolution
- Customer experience optimization
- Retention strategies and loyalty programs
- Customer feedback analysis
- Satisfaction tracking and improvement

For Go4Garage/Kailash: Handle customer inquiries about EV charging, resolve issues, 
maintain high satisfaction scores, and ensure customer retention."""
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        response = await self.invoke_ai([{"role": "user", "content": task.get("query", "")}])
        return {"response": response, "status": "completed"}
    
    def get_system_prompt(self) -> str:
        return "You are VARUNA, the Data Department. Analytics, reporting, data governance."
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        response = await self.invoke_ai([{"role": "user", "content": task.get("query", "")}])
        return {"response": response, "status": "completed"}
