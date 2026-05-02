from typing import Dict, Any
from .base_department import BaseDepartment

class VishnuDepartment(BaseDepartment):
    def __init__(self):
        super().__init__("VISHNU", "Vishnu", "quality", "Testing, validation, standards enforcement")
        self.register_sub_agent("QualityAuditor", "Quality", ["quality", "audits"])
        self.register_sub_agent("ProcessReviewer", "Process", ["process", "review"])
        self.register_sub_agent("StandardsEnforcer", "Standards", ["standards", "compliance"])
    
    def get_system_prompt(self) -> str:
        return "You are VISHNU, the Quality Department. Testing, validation, standards enforcement."
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        response = await self.invoke_ai([{"role": "user", "content": task.get("query", "")}])
        return {"response": response, "status": "completed"}
