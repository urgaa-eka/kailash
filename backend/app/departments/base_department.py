from abc import ABC, abstractmethod
from typing import Dict, Any, List
from datetime import datetime
import os
try:
    from emergentintegrations import LLM
except ImportError:
    LLM = None

class BaseDepartment(ABC):
    """ase class for all KAILASH departments"""
    
    def __init__(self, name: str, deity: str, domain: str, description: str):
        self.name = name
        self.deity = deity
        self.domain = domain
        self.description = description
        self.sub_agents = []
        self.is_active = True
        if LLM:
            self.llm_client = LLM(api_key=os.getenv('EMERGENT_LLM_KEY', 'sk-emergent-b9EeA3Ea33e'))
        else:
            self.llm_client = None
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Return department system prompt"""
        pass
    
    @abstractmethod
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a task"""
        pass
    
    def register_sub_agent(self, name: str, role: str, capabilities: List[str]):
        """Register a sub-agent"""
        self.sub_agents.append({
            "name": name,
            "role": role,
            "capabilities": capabilities
        })
    
    async def invoke_ai(self, messages: List[Dict], max_tokens: int = 48) -> str:
        """Invoke AI for department tasks"""
        if not self.llm_client:
            return "AI service not available"
        
        try:
            system_prompt = self.get_system_prompt()
            full_messages = messages
            
            response = self.llm_client.generate(
                model="gpt-4o",
                messages=full_messages,
                system_prompt=system_prompt,
                max_tokens=max_tokens
            )
            
            if isinstance(response, dict):
                return response.get('content', response.get('text', str(response)))
            return str(response)
        except Exception as e:
            return f"AI processing error: {str(e)}"
    
    async def log_activity(self, activity_type: str, details: Dict[str, Any]):
        """Log department activity"""
        from ..core.database import get_mongo_db
        db = await get_mongo_db()
        if db:
            await db.department_logs.insert_one({
                "department": self.name,
                "activity_type": activity_type,
                "details": details,
                "timestamp": datetime.utcnow()
            })
    
    def get_status(self) -> Dict[str, Any]:
        """Get department status"""
        return {
            "name": self.name,
            "deity": self.deity,
            "domain": self.domain,
            "is_active": self.is_active,
            "sub_agents_count": len(self.sub_agents)
        }
