from typing import Dict, Any
from .base_department import BaseDepartment

class SaraswatiDepartment(BaseDepartment):
    def __init__(self):
        super().__init__("SARASWATI", "Saraswati", "knowledge", "Documentation, training, research")
        self.register_sub_agent("DocumentationWriter", "Documentation", ["docs", "guides"])
        self.register_sub_agent("TrainingManager", "Training", ["courses", "onboarding"])
        self.register_sub_agent("Knowledgease", "Research", ["research", "knowledge_base"])
    
    def get_system_prompt(self) -> str:
        return "You are SARASWATI, the Knowledge Department. Documentation, training, research specialist."
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        response = await self.invoke_ai([{"role": "user", "content": task.get("query", "")}])
        return {"response": response, "status": "completed"}
