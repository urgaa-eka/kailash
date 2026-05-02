from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid

class Activity(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: str  # task_assigned, task_completed, security_scan, rebalance, etc.
    message: str
    department: Optional[str] = None
    user_id: Optional[str] = None
    metadata: dict = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "type": "task_assigned",
                "message": "Task assigned to KAMADEVA",
                "department": "kamadeva"
            }
        }
