from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid

class Task(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: Optional[str] = None
    command: Optional[str] = None  # Original GANESHA command
    priority: str = "medium"  # low, medium, high, urgent
    status: str = "pending"  # pending, in_progress, completed, failed
    assigned_department: Optional[str] = None  # Department ID
    assigned_sub_agent: Optional[str] = None  # Sub-agent name
    created_by: str  # User ID
    deadline: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    
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
