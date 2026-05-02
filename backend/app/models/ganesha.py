from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid

class GaneshaCommand(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    command: str
    priority: str = "medium"  # low, medium, high, urgent
    deadline: Optional[datetime] = None
    processing_status: str = "pending"  # pending, parsing, routing, completed, failed
    assigned_department: Optional[str] = None
    task_ids: List[str] = []  # Created tasks
    ai_response: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "command": "Analyze energy consumption trends for last quarter",
                "priority": "high",
                "processing_status": "completed",
                "assigned_department": "surya"
            }
        }
