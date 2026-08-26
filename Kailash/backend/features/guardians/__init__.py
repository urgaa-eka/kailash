import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any


class BaseGuardian(ABC):
    """Base class for all KAILASH guardians"""

    def __init__(self, name: str, domain: str):
        self.name = name
        self.domain = domain
        self.status = "active"
        self.last_check = None
        self.logger = logging.getLogger(f"guardian.{name.lower()}")

    @abstractmethod
    async def monitor(self) -> dict[str, Any]:
        """Monitor guardian's domain"""
        pass

    @abstractmethod
    async def intervene(self, issue: dict[str, Any]) -> dict[str, Any]:
        """Take action on detected issues"""
        pass

    @abstractmethod
    async def report(self) -> dict[str, Any]:
        """Generate status report"""
        pass

    async def heartbeat(self) -> dict[str, Any]:
        """Health check"""
        self.last_check = datetime.utcnow()
        return {
            "guardian": self.name,
            "status": self.status,
            "timestamp": self.last_check.isoformat()
        }

# Imported after BaseGuardian is defined, not at the top: each of these modules
# does `from backend.features.guardians import BaseGuardian`, so hoisting them would be a circular import.
from backend.features.guardians.ganesha import GaneshaGuardian  # noqa: E402
from backend.features.guardians.parvati import ParvatiGuardian  # noqa: E402
from backend.features.guardians.shiv import ShivGuardian  # noqa: E402

__all__ = [
    "BaseGuardian",
    "ShivGuardian",
    "ParvatiGuardian",
    "GaneshaGuardian"
]
