from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

class SubAgent(BaseModel):
    name: str
    role: str
    function: Optional[str] = None
    status: str = "active"
    workload: int = 0  # 0-100
    tasks: int = 0
    current_task: Optional[str] = None
    latest_output: Optional[Any] = None

class DataSource(BaseModel):
    source_name: str
    source_type: str  # "product" | "external_api" | "manual"
    data_fields: List[str] = []
    fetch_frequency: str = "daily"  # "real-time" | "hourly" | "daily"
    last_synced: Optional[datetime] = None

class ProblemSolved(BaseModel):
    problem_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    problem_description: str
    solution_approach: str
    automation_percentage: int = 0  # 0-100
    source_product: Optional[str] = None

class PreData(BaseModel):
    thresholds: Dict[str, Any] = {}
    policies: Dict[str, Any] = {}
    sops: List[Dict[str, Any]] = []
    domain_knowledge: Optional[str] = None  # Markdown content

class PostData(BaseModel):
    current_metrics: Dict[str, Any] = {}
    last_fetched: Optional[datetime] = None
    market_intelligence: Dict[str, Any] = {}

class KPI(BaseModel):
    name: str
    value: Any
    trend: Optional[str] = None
    status: str = "normal"

class Department(BaseModel):
    id: str  # Using department id from frontend (e.g., 'ganesha', 'vishwakarma')
    name: str
    chief: Optional[str] = None
    role: Optional[str] = None
    tier: Optional[str] = None  # Executive, Product, etc.
    color: str = "#0A3D62"  # Hex color
    status: str = "active"
    workload: int = 0  # 0-100
    active_tasks: int = 0
    completed_today: int = 0
    description: Optional[str] = None
    responsibilities: List[str] = []
    ai_tools: List[str] = []
    k_location: Optional[str] = None
    sub_agents: List[SubAgent] = []
    
    # NEW FIELDS for GANESHA routing
    scope: Optional[str] = None  # "internal" | "external" | "guardian"
    display_name: Optional[str] = None
    source_product: Optional[str] = None  # For external departments
    
    # Data intelligence fields
    data_sources: List[DataSource] = []
    problems_solved: List[ProblemSolved] = []
    automation_percentage: Optional[int] = None
    
    # Pre and Post data
    pre_data: Optional[PreData] = None
    post_data: Optional[PostData] = None
    
    # KPIs
    kpis: List[KPI] = []
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_activity: Optional[datetime] = None
    
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
