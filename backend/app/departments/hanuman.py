from typing import Dict, Any
from .base_department import BaseDepartment

class HanumanDepartment(BaseDepartment):
    def __init__(self):
        super().__init__("HANUMAN", "Hanuman", "execution", "Task completion, delivery, rapid implementation")
        self.register_sub_agent("TaskRunner", "Tasks", ["tasks", "execution"])
        self.register_sub_agent("AutomationEngine", "Automation", ["automation", "scripting"])
        self.register_sub_agent("ScriptExecutor", "Scripts", ["scripts", "deployment"])
    
    def get_system_prompt(self) -> str:
        return "You are HANUMAN, the Execution Department. Task completion, delivery, rapid implementation."
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        response = await self.invoke_ai([{"role": "user", "content": task.get("query", "")}])
        return {"response": response, "status": "completed"}
