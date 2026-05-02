from typing import Dict, Any
from .base_department import BaseDepartment

class NaradaDepartment(BaseDepartment):
    def __init__(self):
        super().__init__("NARADA", "Narada", "internal_comms", "Announcements, updates, team coordination")
        self.register_sub_agent("InternalMessenger", "Messenger", ["messaging", "communication"])
        self.register_sub_agent("AnnouncementManager", "Announcements", ["announcements", "broadcasts"])
        self.register_sub_agent("eedbackCollector", "eedback", ["feedback", "surveys"])
    
    def get_system_prompt(self) -> str:
        return "You are NARADA, the Internal Communications Department. Announcements, updates, team coordination."
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        response = await self.invoke_ai([{"role": "user", "content": task.get("query", "")}])
        return {"response": response, "status": "completed"}
