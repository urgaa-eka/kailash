from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class GaneshaCommandRequest(BaseModel):
    command: str
    priority: str = "medium"
    deadline: Optional[datetime] = None
    
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
    assigned_department: Optional[str]
    ai_response: Optional[str]
    task_ids: list = []
    created_at: datetime
    
    class Config:
        from_attributes = True
