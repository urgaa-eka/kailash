from typing import Dict, Any
from .base_department import BaseDepartment

class BrahmaDepartment(BaseDepartment):
    """BRAHMA - Product Innovation Department"""
    
    def __init__(self):
        super().__init__(
            "BRAHMA", 
            "Brahma", 
            "product_innovation", 
            "R&D, new products, feature ideation"
        )
        self.register_sub_agent("ProductVisionary", "Product Vision", ["product", "vision", "roadmap"])
        self.register_sub_agent("InnovationResearcher", "R&D", ["research", "innovation", "trends"])
        self.register_sub_agent("FeatureDesigner", "Feature Design", ["features", "design", "ux"])
    
    def get_system_prompt(self) -> str:
        return """You are BRAHMA, the Product Innovation Department of KAILASH.
You are the Creator, responsible for bringing new ideas to life.

Domain: Product innovation, R&D, feature ideation, market research
Responsibilities:
- New product conceptualization
- Feature ideation and design
- Market research and trend analysis
- Innovation roadmap planning
- Prototype development guidance

For Go4Garage/Kailash: Innovate on EV charging solutions, design new features 
for the platform, research emerging technologies in the EV space."""
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        response = await self.invoke_ai([{"role": "user", "content": task.get("query", "")}])
        return {"response": response, "status": "completed"}
    
    def get_system_prompt(self) -> str:
        return "You are RAHMA, the Architecture Department. System design, planning, technical blueprints."
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        response = await self.invoke_ai([{"role": "user", "content": task.get("query", "")}])
        return {"response": response, "status": "completed"}
