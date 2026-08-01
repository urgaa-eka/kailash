import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class Task(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str | None = None
    command: str | None = None  # Original GANESHA command
    priority: str = "medium"  # low, medium, high, urgent
    status: str = "pending"  # pending, in_progress, completed, failed
    assigned_department: str | None = None  # Department ID
    assigned_sub_agent: str | None = None  # Sub-agent name
    created_by: str  # User ID
    deadline: datetime | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Analyze energy consumption",
                "description": "Review last month's data",
                "priority": "high",
                "status": "pending",
                "assigned_department": "surya"
            }
        }
