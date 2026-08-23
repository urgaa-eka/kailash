"""Go4Garage financial-controller model, logic, and FY dashboard.

Structure and confirmed logic live here; financial values are supplied by a data
provider after deployment (see provider.py). Grounded on the Go4Garage Agent
Knowledge Pack.
"""
from . import dashboard, defects, logic, model, provider
from .dashboard import render_fy
from .provider import FinancialDataProvider, FYFinancials, NullProvider

__all__ = [
    "defects", "dashboard", "logic", "model", "provider",
    "render_fy", "FinancialDataProvider", "FYFinancials", "NullProvider",
]
