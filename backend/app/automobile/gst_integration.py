"""GST Software Integration for Job Card Data"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from ..core.mongodb import get_db
from ..core.config import settings
import logging
import aiohttp

logger = logging.getLogger("kailash.automobile")

class GSTSoftwareClient:
    """Integration with Go4Garage GST Software for job card data"""
    
    def __init__(self):
        self.base_url = getattr(settings, 'GST_SOFTWARE_API_URL', '')
        self.api_key = getattr(settings, 'GST_SOFTWARE_API_KEY', '')

    async def get_job_card_prices(
        self,
        service_type: str,
        vehicle_type: str,
        days: int = 90
    ) -> List[float]:
        """Get prices from job cards"""
        
        # Try external API first if configured
        if self.base_url and self.api_key:
            try:
                async with aiohttp.ClientSession() as session:
                    headers = {"Authorization": f"Bearer {self.api_key}"}
                    params = {
                        "service_type": service_type,
                        "vehicle_type": vehicle_type,
                        "days": days
                    }
                    
                    async with session.get(
                        f"{self.base_url}/api/job-cards/prices",
                        headers=headers,
                        params=params,
                        timeout=aiohttp.ClientTimeout(total=10)
                    ) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            prices = [jc["total_amount"] for jc in data.get("job_cards", [])]
                            logger.info(f"Fetched {len(prices)} prices from external GST software")
                            return prices
            except Exception as e:
                logger.warning(f"External GST API error: {str(e)}. Falling back to local data.")
        
        # Fallback to local MongoDB data
        return await self._get_local_job_card_prices(service_type, vehicle_type, days)

    async def _get_local_job_card_prices(self, service_type: str, vehicle_type: str, days: int) -> List[float]:
        """Get job card prices from local MongoDB"""
        db = get_db()
        cutoff = datetime.utcnow() - timedelta(days=days)
        query = {
            "service_type": service_type,
            "vehicle_type": vehicle_type,
            "created_at": {"$gte": cutoff}
        }
        
        try:
            records = await db.job_cards.find(query).to_list(1000)
            prices = [float(r["total_amount"]) for r in records if "total_amount" in r]
            logger.debug(f"Found {len(prices)} local job card prices")
            return prices
        except Exception as e:
            logger.error(f"Error fetching local job card prices: {str(e)}")
            return []

    async def sync_job_cards(self, days: int = 30) -> Dict[str, Any]:
        """Sync job cards from external GST software"""
        if not self.base_url or not self.api_key:
            return {
                "status": "skipped",
                "reason": "GST software not configured",
                "message": "Set GST_SOFTWARE_API_URL and GST_SOFTWARE_API_KEY to enable sync"
            }
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"Authorization": f"Bearer {self.api_key}"}
                
                async with session.get(
                    f"{self.base_url}/api/job-cards/export?days={days}",
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        job_cards = data.get("job_cards", [])
                        
                        if job_cards:
                            db = get_db()
                            # Add sync timestamp
                            for jc in job_cards:
                                jc["synced_at"] = datetime.utcnow()
                            
                            await db.job_cards.insert_many(job_cards)
                            logger.info(f"Synced {len(job_cards)} job cards from GST software")
                        
                        return {
                            "status": "success",
                            "synced": len(job_cards),
                            "message": f"Successfully synced {len(job_cards)} job cards"
                        }
                    else:
                        return {
                            "status": "error",
                            "http_status": resp.status,
                            "message": "Failed to fetch job cards from GST software"
                        }
        except Exception as e:
            logger.error(f"Error syncing job cards: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "message": "Failed to connect to GST software"
            }

    async def analyze_job_cards(self, filters: Optional[Dict] = None) -> Dict[str, Any]:
        """Analyze job card data"""
        db = get_db()
        match_stage = filters or {}
        
        try:
            pipeline = [
                {"$match": match_stage},
                {"$group": {
                    "_id": {
                        "service_type": "$service_type",
                        "vehicle_type": "$vehicle_type"
                    },
                    "total_jobs": {"$sum": 1},
                    "total_revenue": {"$sum": "$total_amount"},
                    "avg_job_value": {"$avg": "$total_amount"}
                }},
                {"$sort": {"total_revenue": -1}},
                {"$limit": 100}
            ]
            
            results = await db.job_cards.aggregate(pipeline).to_list(100)
            
            # Format results
            analysis = [
                {
                    "service_type": r["_id"]["service_type"],
                    "vehicle_type": r["_id"]["vehicle_type"],
                    "total_jobs": r["total_jobs"],
                    "total_revenue": round(r["total_revenue"], 2),
                    "avg_job_value": round(r["avg_job_value"], 2)
                }
                for r in results
            ]
            
            return {
                "analysis": analysis,
                "total_categories": len(analysis),
                "generated_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error analyzing job cards: {str(e)}")
            return {"error": str(e), "analysis": []}

    async def add_sample_job_cards(self) -> Dict[str, int]:
        """Add sample job card data for testing"""
        db = get_db()
        
        sample_cards = [
            {"service_type": "oil_change", "vehicle_type": "sedan", "total_amount": 2600, "created_at": datetime.utcnow() - timedelta(days=5)},
            {"service_type": "oil_change", "vehicle_type": "sedan", "total_amount": 2750, "created_at": datetime.utcnow() - timedelta(days=10)},
            {"service_type": "brake_service", "vehicle_type": "sedan", "total_amount": 4800, "created_at": datetime.utcnow() - timedelta(days=15)},
            {"service_type": "brake_service", "vehicle_type": "suv", "total_amount": 6200, "created_at": datetime.utcnow() - timedelta(days=20)},
            {"service_type": "ac_service", "vehicle_type": "sedan", "total_amount": 3800, "created_at": datetime.utcnow() - timedelta(days=7)},
        ]
        
        try:
            result = await db.job_cards.insert_many(sample_cards)
            logger.info(f"Added {len(result.inserted_ids)} sample job cards")
            return {"inserted": len(result.inserted_ids)}
        except Exception as e:
            logger.error(f"Error adding sample job cards: {str(e)}")
            return {"inserted": 0, "error": str(e)}

gst_software_client = GSTSoftwareClient()
