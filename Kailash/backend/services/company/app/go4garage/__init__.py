"""Go4Garage financial-controller model, logic, and FY dashboard.

Structure and confirmed logic live here; financial values are supplied by a data
provider after deployment (see provider.py). Grounded on the Go4Garage Agent
Knowledge Pack.
"""
from . import api, dashboard, defects, kp_data, logic, model, provider, store
from .dashboard import render_fy, render_static
from .provider import (
    DbProvider,
    FinancialDataProvider,
    FYFinancials,
    KnowledgePackProvider,
    NullProvider,
)

__all__ = [
    "api", "defects", "dashboard", "kp_data", "logic", "model", "provider", "store",
    "render_fy", "render_static", "FinancialDataProvider", "FYFinancials",
    "DbProvider", "KnowledgePackProvider", "NullProvider",
]
