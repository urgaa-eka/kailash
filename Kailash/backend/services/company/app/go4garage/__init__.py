"""Go4Garage financial-controller model, logic, and FY dashboard.

Structure and confirmed logic live here; financial values are supplied by a data
provider after deployment (see provider.py). Grounded on the Go4Garage Agent
Knowledge Pack.
"""
from . import dashboard, defects, kp_data, logic, model, provider
from .dashboard import render_fy
from .provider import (
    FinancialDataProvider,
    FYFinancials,
    KnowledgePackProvider,
    NullProvider,
)

__all__ = [
    "defects", "dashboard", "kp_data", "logic", "model", "provider",
    "render_fy", "FinancialDataProvider", "FYFinancials",
    "KnowledgePackProvider", "NullProvider",
]
