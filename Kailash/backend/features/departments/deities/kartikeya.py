from typing import Any

from backend.features.departments.deities.base_department import BaseDepartment


class KartikeyaDepartment(BaseDepartment):
    def __init__(self):
        super().__init__("KARTIKEYA", "Kartikeya", "operations", "Workflows, processes, operational execution")
        self.register_sub_agent("OperationsManager", "Operations", ["operations", "workflows"])
        self.register_sub_agent("TaskExecutor", "Execution", ["execution", "tasks"])
        self.register_sub_agent("WorkflowOptimizer", "Workflows", ["optimization", "efficiency"])

    def get_system_prompt(self) -> str:
        return "You are KARTIKEYA, the Operations Department. Workflows, processes, operational execution."

    async def process_task(self, task: dict[str, Any]) -> dict[str, Any]:
        response = await self.invoke_ai([{"role": "user", "content": task.get("query", "")}])
        return {"response": response, "status": "completed"}
