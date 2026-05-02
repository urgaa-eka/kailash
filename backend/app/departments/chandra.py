from typing import Dict, Any
from .base_department import BaseDepartment

class ChandraDepartment(BaseDepartment):
    def __init__(self):
        super().__init__("CHANDRA", "Chandra", "customer", "Support, feedback, satisfaction management")
        self.register_sub_agent("SupportAgent", "Support", ["support", "tickets"])
        self.register_sub_agent("eedbackManager", "eedback", ["feedback", "surveys"])
        self.register_sub_agent("ExperienceOptimizer", "Experience", ["cx", "satisfaction"])
    
    def get_system_prompt(self) -> str:
        return "You are CHANDRA, the Customer Department. Support, feedback, satisfaction management."
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        response = await self.invoke_ai([{"role": "user", "content": task.get("query", "")}])
        return {"response": response, "status": "completed"}
