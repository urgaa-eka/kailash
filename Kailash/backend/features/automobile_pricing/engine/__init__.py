"""Automobile Industry Module for KAILASH V2

Uniform Pricing Engine with Market Data + GST Software Fusion
"""

from backend.features.automobile_pricing.engine.gst_integration import gst_software_client
from backend.features.automobile_pricing.engine.market_data import market_data_collector
from backend.features.automobile_pricing.engine.pricing_engine import pricing_engine
from backend.features.automobile_pricing.engine.router import router

__all__ = [
    'pricing_engine',
    'market_data_collector',
    'gst_software_client',
    'router'
]
