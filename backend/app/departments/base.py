from abc import ABC, abstractmethod
from typing import Dict, Any, List
from datetime import datetime

class BaseDepartment(ABC):
    """
    Abstract base class for all deity departments.
    All 20 departments must inherit from this class.
    """
    
    def __init__(self, name: str, domain: str, description: str):
        self.name = name
        self.domain = domain
        self.description = description
        self.sub_agents: List[str] = []
        self.system_prompt: str = ""
        self.status: str = "active"
        self.created_at = datetime.utcnow()

    @abstractmethod
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process an incoming task. Must be implemented by all departments.
        
        Args:
            task: Dictionary containing:
                - message: User's request
                - user_id: ID of requesting user
                - conversation_id: Current conversation
                - sub_task: Specific sub-task if identified
        
        Returns:
            Dictionary with:
                - content: Response text
                - department: Department name
                - metadata: Optional additional data
        """
        pass

    async def invoke_llm(self, prompt: str, task_type: str = "general") -> Dict[str, Any]:
        """Invoke LLM with department-specific context"""
        full_prompt = f"{self.system_prompt}\n\nTask: {prompt}"
        return {"content": f"Response from {self.name}"}

    async def log_activity(self, action: str, details: Dict[str, Any]):
        """Log department activity to MongoDB"""
        from app.core.mongodb import MongoD
        db = MongoD.get_database()
        
        await db.department_logs.insert_one({
            "department": self.name,
            "action": action,
            "details": details,
            "timestamp": datetime.utcnow()
        })

    def get_status(self) -> Dict[str, Any]:
        """Get department status"""
        return {
            "name": self.name,
            "domain": self.domain,
            "description": self.description,
            "status": self.status,
            "sub_agents": self.sub_agents
        }

    def register_sub_agent(self, agent_name: str):
        """Register a sub-agent for this department"""
        if agent_name not in self.sub_agents:
            self.sub_agents.append(agent_name)

    def __repr__(self):
        return f"<Department {self.name} ({self.domain})>"
