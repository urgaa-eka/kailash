"""Market Data Collector for Automobile Pricing"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from ..core.mongodb import get_db
import logging

logger = logging.getLogger("kailash.automobile")

class MarketDataCollector:
    """Collect and manage market pricing data"""

    async def get_service_prices(
        self,
        service_type: str,
        vehicle_type: str,
        region: Optional[str] = None
    ) -> List[float]:
        """Get market prices for a service"""
        db = get_db()
        query = {"service_type": service_type, "vehicle_type": vehicle_type}
        if region:
            query["region"] = region
        
        try:
            records = await db.market_prices.find(query).to_list(500)
            prices = [float(r["price"]) for r in records if "price" in r]
            return prices
        except Exception as e:
            logger.error(f"Error fetching service prices: {str(e)}")
            return []

    async def update_market_data(self, data: List[Dict[str, Any]]) -> Dict[str, int]:
        """Bulk update market pricing data"""
        if not data:
            return {"inserted": 0, "message": "No data provided"}
        
        db = get_db()
        
        try:
            # Add timestamp to all records
            for item in data:
                item["updated_at"] = datetime.utcnow()
                if "created_at" not in item:
                    item["created_at"] = datetime.utcnow()
            
            result = await db.market_prices.insert_many(data)
            logger.info(f"Inserted {len(result.inserted_ids)} market price records")
            
            return {
                "inserted": len(result.inserted_ids),
                "message": f"Successfully inserted {len(result.inserted_ids)} records"
            }
        except Exception as e:
            logger.error(f"Error updating market data: {str(e)}")
            return {"inserted": 0, "error": str(e)}

    async def get_market_insights(self, vehicle_type: str) -> Dict[str, Any]:
        """Aggregated insights for vehicle type"""
        db = get_db()
        
        try:
            pipeline = [
                {"$match": {"vehicle_type": vehicle_type}},
                {"$group": {
                    "_id": "$service_type",
                    "avg_price": {"$avg": "$price"},
                    "min_price": {"$min": "$price"},
                    "max_price": {"$max": "$price"},
                    "count": {"$sum": 1}
                }},
                {"$sort": {"avg_price": -1}},
                {"$limit": 100}
            ]
            
            results = await db.market_prices.aggregate(pipeline).to_list(100)
            
            # Format results
            services = [
                {
                    "service_type": r["_id"],
                    "avg_price": round(r["avg_price"], 2),
                    "min_price": round(r["min_price"], 2),
                    "max_price": round(r["max_price"], 2),
                    "sample_size": r["count"]
                }
                for r in results
            ]
            
            return {
                "vehicle_type": vehicle_type,
                "services": services,
                "total_data_points": sum(s["sample_size"] for s in services),
                "generated_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error generating market insights: {str(e)}")
            return {
                "error": str(e),
                "vehicle_type": vehicle_type,
                "services": []
            }

    async def add_sample_data(self) -> Dict[str, int]:
        """Add sample market data for testing"""
        sample_data = [
            {"service_type": "oil_change", "vehicle_type": "sedan", "price": 2500, "region": "north"},
            {"service_type": "oil_change", "vehicle_type": "sedan", "price": 2800, "region": "south"},
            {"service_type": "oil_change", "vehicle_type": "suv", "price": 3500, "region": "north"},
            {"service_type": "brake_service", "vehicle_type": "sedan", "price": 4500, "region": "north"},
            {"service_type": "brake_service", "vehicle_type": "suv", "price": 6000, "region": "south"},
            {"service_type": "tire_rotation", "vehicle_type": "sedan", "price": 800, "region": "north"},
            {"service_type": "ac_service", "vehicle_type": "sedan", "price": 3500, "region": "south"},
            {"service_type": "battery_replacement", "vehicle_type": "sedan", "price": 5500, "region": "north"},
        ]
        
        return await self.update_market_data(sample_data)

market_data_collector = MarketDataCollector()
