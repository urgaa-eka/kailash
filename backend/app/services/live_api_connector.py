"""Live API Connector Service for real-time data from external sources."""
import os
import httpx
import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional
import logging
import json

logger = logging.getLogger(__name__)


class LiveAPIConnector:
    """Service to connect to and fetch data from live external APIs."""
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        
    async def close(self):
        await self.client.aclose()
    
    # ============= RBI API =============
    async def fetch_rbi_policy_data(self) -> Dict:
        """Fetch RBI monetary policy and financial regulations data."""
        try:
            # RBI doesn't have a public API, so we use a proxy/scraper approach
            # For production, you'd want to use official RBI data feeds
            # Note: RBI RSS/feeds would be parsed here in production
            
            # Simulated response based on typical RBI data structure
            # In production, this would parse actual RBI feeds/RSS
            return {
                "source": "RBI",
                "fetched_at": datetime.now(timezone.utc).isoformat(),
                "data": {
                    "repo_rate": 6.50,
                    "reverse_repo_rate": 3.35,
                    "crr": 4.50,
                    "slr": 18.00,
                    "bank_rate": 6.75,
                    "last_policy_date": "2024-12-06",
                    "policy_stance": "withdrawal of accommodation",
                    "inflation_target": "4% with +/- 2%",
                    "key_updates": [
                        "Repo rate unchanged at 6.50%",
                        "Focus on inflation management",
                        "GDP growth projection: 7.0%"
                    ]
                },
                "status": "success"
            }
        except Exception as e:
            logger.error(f"RBI API error: {e}")
            return {"source": "RBI", "status": "error", "error": str(e)}
    
    # ============= GST API =============
    async def fetch_gst_updates(self, gstin: Optional[str] = None) -> Dict:
        """Fetch GST compliance updates and rates."""
        try:
            # GST portal doesn't have public API, would need official registration
            # Simulated response for demo
            return {
                "source": "GST Portal",
                "fetched_at": datetime.now(timezone.utc).isoformat(),
                "data": {
                    "current_rates": {
                        "standard": [0, 5, 12, 18, 28],
                        "cess_applicable": ["luxury_cars", "tobacco", "aerated_drinks"]
                    },
                    "upcoming_deadlines": [
                        {"form": "GSTR-1", "due_date": "2025-01-11", "period": "December 2024"},
                        {"form": "GSTR-3B", "due_date": "2025-01-20", "period": "December 2024"},
                        {"form": "GSTR-9", "due_date": "2025-12-31", "period": "FY 2024-25"}
                    ],
                    "recent_circulars": [
                        {"number": "237/2024", "subject": "Clarification on ITC reversal"},
                        {"number": "236/2024", "subject": "E-invoicing threshold update"}
                    ],
                    "compliance_score": 98
                },
                "status": "success"
            }
        except Exception as e:
            logger.error(f"GST API error: {e}")
            return {"source": "GST Portal", "status": "error", "error": str(e)}
    
    # ============= STRIPE API =============
    async def fetch_stripe_data(self) -> Dict:
        """Fetch Stripe payment analytics and transaction data."""
        try:
            stripe_key = os.getenv("STRIPE_SECRET_KEY")
            
            if not stripe_key:
                # Return mock data if no key
                return {
                    "source": "Stripe",
                    "fetched_at": datetime.now(timezone.utc).isoformat(),
                    "data": {
                        "balance": {"available": 125000, "pending": 15000, "currency": "INR"},
                        "transactions_today": 47,
                        "revenue_today": 89500,
                        "successful_payments": 45,
                        "failed_payments": 2,
                        "refunds_today": 0,
                        "disputes": 0,
                        "avg_transaction_value": 1989
                    },
                    "status": "success",
                    "mode": "mock"
                }
            
            # Real Stripe API call
            headers = {"Authorization": f"Bearer {stripe_key}"}
            
            # Fetch balance
            balance_resp = await self.client.get(
                "https://api.stripe.com/v1/balance",
                headers=headers
            )
            balance_data = balance_resp.json() if balance_resp.status_code == 200 else {}
            
            return {
                "source": "Stripe",
                "fetched_at": datetime.now(timezone.utc).isoformat(),
                "data": {
                    "balance": balance_data.get("available", [{}])[0] if balance_data else {},
                    "pending": balance_data.get("pending", [{}])[0] if balance_data else {},
                },
                "status": "success",
                "mode": "live"
            }
        except Exception as e:
            logger.error(f"Stripe API error: {e}")
            return {"source": "Stripe", "status": "error", "error": str(e)}
    
    # ============= WEATHER API (for SURYA/Energy forecasting) =============
    async def fetch_weather_data(self, city: str = "Mumbai") -> Dict:
        """Fetch weather data for energy demand forecasting."""
        try:
            api_key = os.getenv("OPENWEATHER_API_KEY")
            
            if not api_key:
                # Return mock weather data
                return {
                    "source": "OpenWeatherMap",
                    "fetched_at": datetime.now(timezone.utc).isoformat(),
                    "city": city,
                    "data": {
                        "temperature": 28,
                        "feels_like": 32,
                        "humidity": 75,
                        "weather": "Partly cloudy",
                        "wind_speed": 12,
                        "uv_index": 7,
                        "sunrise": "06:45",
                        "sunset": "18:15",
                        "forecast_summary": "High solar generation expected"
                    },
                    "status": "success",
                    "mode": "mock"
                }
            
            url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
            response = await self.client.get(url)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "source": "OpenWeatherMap",
                    "fetched_at": datetime.now(timezone.utc).isoformat(),
                    "city": city,
                    "data": {
                        "temperature": data["main"]["temp"],
                        "feels_like": data["main"]["feels_like"],
                        "humidity": data["main"]["humidity"],
                        "weather": data["weather"][0]["description"],
                        "wind_speed": data["wind"]["speed"],
                    },
                    "status": "success",
                    "mode": "live"
                }
            else:
                return {"source": "OpenWeatherMap", "status": "error", "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            logger.error(f"Weather API error: {e}")
            return {"source": "OpenWeatherMap", "status": "error", "error": str(e)}
    
    # ============= CVE/Security API (for INDRA) =============
    async def fetch_security_vulnerabilities(self) -> Dict:
        """Fetch latest CVE vulnerabilities for security monitoring."""
        try:
            # CIRCL CVE API - free and public
            url = "https://cve.circl.lu/api/last/10"
            response = await self.client.get(url)
            
            if response.status_code == 200:
                cves = response.json()
                return {
                    "source": "CIRCL CVE Database",
                    "fetched_at": datetime.now(timezone.utc).isoformat(),
                    "data": {
                        "latest_cves": [
                            {
                                "id": cve.get("id", ""),
                                "summary": cve.get("summary", "")[:200] + "..." if cve.get("summary") else "",
                                "published": cve.get("Published", ""),
                                "cvss": cve.get("cvss", "N/A")
                            }
                            for cve in cves[:5]
                        ],
                        "total_fetched": len(cves),
                        "critical_count": len([c for c in cves if c.get("cvss", 0) and float(c.get("cvss", 0)) >= 9.0])
                    },
                    "status": "success",
                    "mode": "live"
                }
            else:
                return {"source": "CIRCL CVE", "status": "error", "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            logger.error(f"CVE API error: {e}")
            return {"source": "CIRCL CVE", "status": "error", "error": str(e)}
    
    # ============= GitHub API (for VISHWAKARMA) =============
    async def fetch_github_trends(self) -> Dict:
        """Fetch GitHub trending repos and tech trends."""
        try:
            # GitHub Search API for trending
            url = "https://api.github.com/search/repositories?q=stars:>10000&sort=stars&order=desc&per_page=5"
            headers = {"Accept": "application/vnd.github.v3+json"}
            
            github_token = os.getenv("GITHUB_TOKEN")
            if github_token:
                headers["Authorization"] = f"token {github_token}"
            
            response = await self.client.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "source": "GitHub",
                    "fetched_at": datetime.now(timezone.utc).isoformat(),
                    "data": {
                        "trending_repos": [
                            {
                                "name": repo["full_name"],
                                "stars": repo["stargazers_count"],
                                "language": repo["language"],
                                "description": repo["description"][:100] if repo["description"] else ""
                            }
                            for repo in data.get("items", [])[:5]
                        ]
                    },
                    "status": "success",
                    "mode": "live"
                }
            else:
                return {"source": "GitHub", "status": "error", "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            logger.error(f"GitHub API error: {e}")
            return {"source": "GitHub", "status": "error", "error": str(e)}
    
    # ============= World Bank API (for financial data) =============
    async def fetch_economic_indicators(self, country: str = "IN") -> Dict:
        """Fetch economic indicators from World Bank."""
        try:
            # World Bank API - free and public
            indicators = {
                "NY.GDP.MKTP.KD.ZG": "GDP Growth",
                "FP.CPI.TOTL.ZG": "Inflation Rate",
                "SL.UEM.TOTL.ZS": "Unemployment Rate"
            }
            
            results = {}
            for code, name in indicators.items():
                url = f"https://api.worldbank.org/v2/country/{country}/indicator/{code}?format=json&per_page=1"
                response = await self.client.get(url)
                
                if response.status_code == 200:
                    data = response.json()
                    if len(data) > 1 and data[1]:
                        results[name] = {
                            "value": data[1][0].get("value"),
                            "year": data[1][0].get("date")
                        }
            
            return {
                "source": "World Bank",
                "fetched_at": datetime.now(timezone.utc).isoformat(),
                "country": country,
                "data": results,
                "status": "success",
                "mode": "live"
            }
        except Exception as e:
            logger.error(f"World Bank API error: {e}")
            return {"source": "World Bank", "status": "error", "error": str(e)}
    
    # ============= Aggregate fetch for department =============
    async def fetch_department_live_data(self, department: str) -> Dict:
        """Fetch all relevant live data for a department."""
        department = department.lower()
        
        data = {
            "department": department,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "sources": []
        }
        
        if department == "lakshmi":
            data["sources"] = await asyncio.gather(
                self.fetch_rbi_policy_data(),
                self.fetch_gst_updates(),
                self.fetch_stripe_data(),
                self.fetch_economic_indicators()
            )
        elif department == "vishwakarma":
            data["sources"] = await asyncio.gather(
                self.fetch_github_trends(),
                self.fetch_security_vulnerabilities()
            )
        elif department == "indra":
            data["sources"] = [await self.fetch_security_vulnerabilities()]
        elif department == "surya":
            data["sources"] = [await self.fetch_weather_data()]
        elif department in ["agni", "tvashta", "kartikeya"]:
            data["sources"] = await asyncio.gather(
                self.fetch_github_trends(),
                self.fetch_security_vulnerabilities()
            )
        else:
            # Default sources
            data["sources"] = [await self.fetch_economic_indicators()]
        
        return data


# Singleton instance
_connector: Optional[LiveAPIConnector] = None

def get_connector() -> LiveAPIConnector:
    global _connector
    if _connector is None:
        _connector = LiveAPIConnector()
    return _connector
