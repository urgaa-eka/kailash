from typing import Dict, Any
from .base_department import BaseDepartment

class BrihaspatiDepartment(BaseDepartment):
    """BRIHASPATI - Analytics & Insights Department"""
    
    def __init__(self):
        super().__init__(
            "BRIHASPATI", 
            "Brihaspati", 
            "analytics", 
            "Data analysis, reporting, business metrics"
        )
        self.register_sub_agent("BusinessAnalyst", "Analytics", ["analytics", "metrics"])
        self.register_sub_agent("DataScientist", "Data Science", ["data", "insights"])
        self.register_sub_agent("ReportGenerator", "Reporting", ["reports", "dashboards"])
    
    def get_system_prompt(self) -> str:
        return """You are BRIHASPATI, the Analytics & Insights Department of KAILASH.
You are the Divine Teacher, providing wisdom through data analysis.

Domain: Data analysis, reporting, metrics, business intelligence
Responsibilities:
- Business metrics tracking and analysis
- Report generation and dashboards
- Data-driven insights and recommendations
- KPI monitoring
- Trend analysis and forecasting

For Go4Garage/Kailash: Analyze EV charging usage patterns, generate performance 
reports, track business metrics, and provide data-driven recommendations."""
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        response = await self.invoke_ai([{"role": "user", "content": task.get("query", "")}])
        return {"response": response, "status": "completed"}
