from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: str = "medium"
    assigned_department: Optional[str] = None
    deadline: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Review energy analytics",
                "description": "Analyze Q energy consumption",
                "priority": "high",
                "assigned_department": "surya"
            }
        }

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    assigned_department: Optional[str] = None
    assigned_sub_agent: Optional[str] = None
    deadline: Optional[datetime] = None

class TaskResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    priority: str
    status: str
    assigned_department: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True
