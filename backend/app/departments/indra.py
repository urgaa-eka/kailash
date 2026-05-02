from typing import Dict, Any
from .base_department import BaseDepartment

class IndraDepartment(BaseDepartment):
    def __init__(self):
        super().__init__("INDRA", "Indra", "leadership", "Strategy, decisions, executive directives")
        self.register_sub_agent("StrategyAdvisor", "Strategy", ["strategy", "planning"])
        self.register_sub_agent("DecisionSupport", "Decisions", ["decisions", "analysis"])
        self.register_sub_agent("ExecutiveAssistant", "Executive", ["executive", "directives"])
    
    def get_system_prompt(self) -> str:
        return "You are INDRA, the Leadership Department. Strategy, decisions, executive directives."
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        response = await self.invoke_ai([{"role": "user", "content": task.get("query", "")}])
        return {"response": response, "status": "completed"}
