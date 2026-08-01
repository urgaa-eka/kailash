import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class SubAgent(BaseModel):
    name: str
    role: str
    function: str | None = None
    status: str = "active"
    workload: int = 0  # 0-100
    tasks: int = 0
    current_task: str | None = None
    latest_output: Any | None = None

class DataSource(BaseModel):
    source_name: str
    source_type: str  # "product" | "external_api" | "manual"
    data_fields: list[str] = []
    fetch_frequency: str = "daily"  # "real-time" | "hourly" | "daily"
    last_synced: datetime | None = None

class ProblemSolved(BaseModel):
    problem_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    problem_description: str
    solution_approach: str
    automation_percentage: int = 0  # 0-100
    source_product: str | None = None

class PreData(BaseModel):
    thresholds: dict[str, Any] = {}
    policies: dict[str, Any] = {}
    sops: list[dict[str, Any]] = []
    domain_knowledge: str | None = None  # Markdown content

class PostData(BaseModel):
    current_metrics: dict[str, Any] = {}
    last_fetched: datetime | None = None
    market_intelligence: dict[str, Any] = {}

class KPI(BaseModel):
    name: str
    value: Any
    trend: str | None = None
    status: str = "normal"

class Department(BaseModel):
    id: str  # Using department id from frontend (e.g., 'ganesha', 'vishwakarma')
    name: str
    chief: str | None = None
    role: str | None = None
    tier: str | None = None  # Executive, Product, etc.
    color: str = "#0A3D62"  # Hex color
    status: str = "active"
    workload: int = 0  # 0-100
    active_tasks: int = 0
    completed_today: int = 0
    description: str | None = None
    responsibilities: list[str] = []
    ai_tools: list[str] = []
    k_location: str | None = None
    sub_agents: list[SubAgent] = []

    # NEW FIELDS for GANESHA routing
    scope: str | None = None  # "internal" | "external" | "guardian"
    display_name: str | None = None
    source_product: str | None = None  # For external departments

    # Data intelligence fields
    data_sources: list[DataSource] = []
    problems_solved: list[ProblemSolved] = []
    automation_percentage: int | None = None

    # Pre and Post data
    pre_data: PreData | None = None
    post_data: PostData | None = None

    # KPIs
    kpis: list[KPI] = []

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_activity: datetime | None = None

    class Config:
        json_schema_extra = {
            "example": {
                "id": "surya",
                "name": "SURYA",
                "chief": "Lord Surya",
                "role": "URGAA Intelligence",
                "tier": "Product",
                "color": "#FFE66D",
                "status": "active",
                "workload": 65,
                "scope": "external",
                "source_product": "URGAA",
                "automation_percentage": 75
            }
        }
