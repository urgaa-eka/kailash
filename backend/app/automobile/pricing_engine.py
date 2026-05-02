"""Pricing Engine - Market + GST Software Data Fusion"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from ..core.mongodb import get_db
import statistics
import logging

logger = logging.getLogger("kailash.automobile")

class PricingEngine:
    """Uniform Pricing Calculator - Market + GST Software Data Fusion"""
    
    def __init__(self):
        self.cache: Dict[str, Any] = {}

    async def calculate_uniform_price(
        self,
        service_type: str,
        vehicle_type: str,
        region: Optional[str] = None
    ) -> Dict[str, Any]:
        """Calculate uniform price from market + internal data"""
        
        try:
            # Get market prices
            market_prices = await self._get_market_prices(service_type, vehicle_type, region)
            
            # Get GST software prices (job cards)
            gst_prices = await self._get_gst_prices(service_type, vehicle_type)
            
            all_prices = market_prices + gst_prices
            
            if not all_prices:
                return {
                    "error": "No pricing data available",
                    "service_type": service_type,
                    "vehicle_type": vehicle_type
                }
            
            result = {
                "service_type": service_type,
                "vehicle_type": vehicle_type,
                "region": region or "all",
                "uniform_price": round(statistics.median(all_prices), 2),
                "min_price": round(min(all_prices), 2),
                "max_price": round(max(all_prices), 2),
                "avg_price": round(statistics.mean(all_prices), 2),
                "sample_size": len(all_prices),
                "sources": {
                    "market_data": len(market_prices),
                    "gst_software": len(gst_prices)
                },
                "calculated_at": datetime.utcnow().isoformat()
            }
            
            # Store for history
            db = get_db()
            await db.pricing_history.insert_one(result.copy())
            
            logger.info(f"Calculated uniform price for {service_type}/{vehicle_type}: ₹{result['uniform_price']}")
            return result
            
        except Exception as e:
            logger.error(f"Error calculating uniform price: {str(e)}")
            return {
                "error": str(e),
                "service_type": service_type,
                "vehicle_type": vehicle_type
            }

    async def _get_market_prices(self, service_type: str, vehicle_type: str, region: Optional[str]) -> List[float]:
        """Get prices from market data"""
        db = get_db()
        query = {"service_type": service_type, "vehicle_type": vehicle_type}
        if region:
            query["region"] = region
        
        try:
            records = await db.market_prices.find(query).to_list(500)
            prices = [float(r["price"]) for r in records if "price" in r and r["price"] > 0]
            logger.debug(f"Found {len(prices)} market prices for {service_type}/{vehicle_type}")
            return prices
        except Exception as e:
            logger.error(f"Error fetching market prices: {str(e)}")
            return []

    async def _get_gst_prices(self, service_type: str, vehicle_type: str) -> List[float]:
        """Get prices from GST software job cards (last 90 days)"""
        db = get_db()
        cutoff = datetime.utcnow() - timedelta(days=90)
        query = {
            "service_type": service_type,
            "vehicle_type": vehicle_type,
            "created_at": {"$gte": cutoff}
        }
        
        try:
            records = await db.job_cards.find(query).to_list(1000)
            prices = [float(r["total_amount"]) for r in records if "total_amount" in r and r["total_amount"] > 0]
            logger.debug(f"Found {len(prices)} GST prices for {service_type}/{vehicle_type}")
            return prices
        except Exception as e:
            logger.error(f"Error fetching GST prices: {str(e)}")
            return []

    async def get_service_pricing_table(self, vehicle_type: str) -> List[Dict[str, Any]]:
        """Complete pricing table for vehicle type"""
        services = [
            "oil_change", "brake_service", "tire_rotation", "wheel_alignment",
            "ac_service", "battery_replacement", "engine_tune", "transmission_service",
            "suspension_repair", "electrical_repair", "body_work", "painting",
            "full_service", "periodic_maintenance", "clutch_repair", "gear_repair"
        ]
        
        table = []
        for service in services:
            price = await self.calculate_uniform_price(service, vehicle_type)
            if "error" not in price:
                table.append(price)
        
        logger.info(f"Generated pricing table for {vehicle_type}: {len(table)} services")
        return table

    async def analyze_pricing_trends(self, service_type: str, days: int = 30) -> Dict[str, Any]:
        """Analyze pricing trends over time"""
        db = get_db()
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        try:
            prices = await db.pricing_history.find({
                "service_type": service_type,
                "calculated_at": {"$gte": cutoff.isoformat()}
            }).sort("calculated_at", 1).to_list(1000)
            
            if len(prices) < 2:
                return {
                    "error": "Insufficient data",
                    "service_type": service_type,
                    "message": "Need at least 2 data points"
                }
            
            values = [p["uniform_price"] for p in prices]
            first_price = values[0]
            last_price = values[-1]
            
            return {
                "service_type": service_type,
                "period_days": days,
                "trend": "increasing" if last_price > first_price else "decreasing" if last_price < first_price else "stable",
                "change_percent": round((last_price - first_price) / first_price * 100, 2) if first_price > 0 else 0,
                "current_price": last_price,
                "period_avg": round(statistics.mean(values), 2),
                "data_points": len(values),
                "generated_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error analyzing pricing trends: {str(e)}")
            return {"error": str(e), "service_type": service_type}

pricing_engine = PricingEngine()
