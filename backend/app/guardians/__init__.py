from abc import ABC, abstractmethod
from typing import Dict, Any
from datetime import datetime
import logging

class BaseGuardian(ABC):
    """Base class for all KAILASH guardians"""
    
    def __init__(self, name: str, domain: str):
        self.name = name
        self.domain = domain
        self.status = "active"
        self.last_check = None
        self.logger = logging.getLogger(f"guardian.{name.lower()}")
    
    @abstractmethod
    async def monitor(self) -> Dict[str, Any]:
        """Monitor guardian's domain"""
        pass
    
    @abstractmethod
    async def intervene(self, issue: Dict[str, Any]) -> Dict[str, Any]:
        """Take action on detected issues"""
        pass
    
    @abstractmethod
    async def report(self) -> Dict[str, Any]:
        """Generate status report"""
        pass
    
    async def heartbeat(self) -> Dict[str, Any]:
        """Health check"""
        self.last_check = datetime.utcnow()
        return {
            "guardian": self.name,
            "status": self.status,
            "timestamp": self.last_check.isoformat()
        }

from .shiv import ShivGuardian
from .parvati import ParvatiGuardian
from .ganesha import GaneshaGuardian

__all__ = [
    "BaseGuardian",
    "ShivGuardian",
    "ParvatiGuardian",
    "GaneshaGuardian"
]
