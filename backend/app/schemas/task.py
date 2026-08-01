from datetime import datetime

from pydantic import BaseModel


class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    priority: str = "medium"
    assigned_department: str | None = None
    deadline: datetime | None = None

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
    title: str | None = None
    description: str | None = None
    priority: str | None = None
    status: str | None = None
    assigned_department: str | None = None
    assigned_sub_agent: str | None = None
    deadline: datetime | None = None

class TaskResponse(BaseModel):
    id: str
    title: str
    description: str | None
    priority: str
    status: str
    assigned_department: str | None
    created_at: datetime

    class Config:
        from_attributes = True
