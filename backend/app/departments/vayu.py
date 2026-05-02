from typing import Dict, Any
from .base_department import BaseDepartment

class VayuDepartment(BaseDepartment):
    def __init__(self):
        super().__init__("VAYU", "Vayu", "communications", "Notifications, broadcasts, messaging")
        self.register_sub_agent("NotificationService", "Notifications", ["alerts", "notifications"])
        self.register_sub_agent("EmailManager", "Email", ["email", "campaigns"])
        self.register_sub_agent("SMSGateway", "SMS", ["sms", "messaging"])
    
    def get_system_prompt(self) -> str:
        return "You are VAYU, the Communications Department. Notifications, broadcasts, messaging handler."
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        response = await self.invoke_ai([{"role": "user", "content": task.get("query", "")}])
        return {"response": response, "status": "completed"}
