import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class GaneshaCommand(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    command: str
    priority: str = "medium"  # low, medium, high, urgent
    deadline: datetime | None = None
    processing_status: str = "pending"  # pending, parsing, routing, completed, failed
    assigned_department: str | None = None
    task_ids: list[str] = []  # Created tasks
    ai_response: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    processed_at: datetime | None = None

    class Config:
        json_schema_extra = {
            "example": {
                "command": "Analyze energy consumption trends for last quarter",
                "priority": "high",
                "processing_status": "completed",
                "assigned_department": "surya"
            }
        }
