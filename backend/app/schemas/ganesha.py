from datetime import datetime

from pydantic import BaseModel


class GaneshaCommandRequest(BaseModel):
    command: str
    priority: str = "medium"
    deadline: datetime | None = None

    class Config:
        json_schema_extra = {
            "example": {
                "command": "Analyze energy consumption trends for the last quarter and provide recommendations",
                "priority": "high",
                "deadline": "--T::Z"
            }
        }

class GaneshaCommandResponse(BaseModel):
    id: str
    command: str
    priority: str
    processing_status: str
    assigned_department: str | None
    ai_response: str | None
    task_ids: list = []
    created_at: datetime

    class Config:
        from_attributes = True
