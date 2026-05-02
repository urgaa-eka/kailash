from typing import Dict, Any
from .base_department import BaseDepartment

class VishwakarmaDepartment(BaseDepartment):
    """VISHWAKARMA - Technology Department"""
    
    def __init__(self):
        super().__init__(
            name="VISHWAKARMA",
            deity="Vishwakarma",
            domain="technology",
            description="Technology, development, and IT infrastructure"
        )
        self.register_sub_agent("CodeArchitect", "System design", ["architecture", "design_patterns"])
        self.register_sub_agent("DevOps", "Infrastructure", ["ci_cd", "deployment"])
        self.register_sub_agent("SecurityEngineer", "Security", ["vulnerability_scan", "pen_testing"])
    
    def get_system_prompt(self) -> str:
        return """You are VISHWAKARMA, the Technology Department of KAILASH.
You are the Divine Architect, master of all technical matters.

Domain: Software development, IT infrastructure, DevOps, technical security

or Go4Garage/KAILASH: Python/astAPI backend, React frontend, MongoD/PostgreSQL, Redis

Provide technical guidance with clear rationale. Consider scalability and security."""
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        task_type = task.get("type")
        
        if task_type == "code_review":
            code = task.get("code", "")
            response = await self.invoke_ai([{
                "role": "user",
                "content": f"Review this code:\n{code}\n\nProvide: quality, bugs, security, performance feedback"
            }])
            await self.log_activity("code_review", {"language": task.get("language", "unknown")})
            return {"review": response, "status": "completed"}
        
        response = await self.invoke_ai([{"role": "user", "content": task.get("query", "")}])
        return {"response": response, "status": "completed"}
