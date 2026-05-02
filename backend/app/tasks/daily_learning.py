"""Daily learning pipeline for gathering and processing intelligence."""
import os
import httpx
import asyncio
from datetime import datetime, timezone
import json
from typing import Dict, List
from pathlib import Path
from celery import shared_task
import logging

logger = logging.getLogger(__name__)

# Department configuration
DEPARTMENTS = {
    "internal": [
        "lakshmi", "vishwakarma", "agni", "indra", "vayu", "yama", "kubera",
        "ashwini", "brihaspati", "chandra", "kartikeya", "marut", "narada",
        "rudra", "tvashta"
    ],
    "external": ["surya", "brahma", "saraswati", "varuna", "pragya"]
}

KNOWLEDGE_BASE_PATH = Path("/app/backend/knowledge")


async def query_perplexity(query: str, api_key: str) -> Dict:
    """Query Perplexity API for real-time intelligence."""
    url = "https://api.perplexity.ai/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "sonar",
        "messages": [
            {
                "role": "system",
                "content": "You are a market intelligence analyst. Provide concise, factual insights based on latest data."
            },
            {
                "role": "user",
                "content": query
            }
        ],
        "temperature": 0.2,
        "top_p": 0.9,
        "search_recency_filter": "day",
        "stream": False
    }
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            return {
                "content": data["choices"][0]["message"]["content"],
                "citations": data.get("citations", []),
                "model": data.get("model", "unknown")
            }
    except Exception as e:
        logger.error(f"Perplexity API error: {str(e)}")
        return {"content": f"Error fetching intelligence: {str(e)}", "citations": [], "model": "error"}


async def process_with_llm(intelligence: str, department: str) -> str:
    """Process raw intelligence with LLM to extract relevant insights for department."""
    # Using emergentintegrations for LLM processing
    try:
        from emergentintegrations.claude import ClaudeClient
        
        emergent_key = os.getenv("EMERGENT_LLM_KEY")
        if not emergent_key:
            return intelligence  # Return raw if no key available
        
        client = ClaudeClient(api_key=emergent_key)
        
        prompt = f"""Given the following market intelligence, extract and summarize only the insights 
relevant to the {department.upper()} department. Be concise and focus on actionable insights.

Intelligence:
{intelligence}

Provide a concise summary (max 300 words) of insights relevant to {department.upper()}."""
        
        response = await client.generate_async(messages=[{"role": "user", "content": prompt}], max_tokens=500)
        return response.get("content", intelligence)
    except Exception as e:
        logger.error(f"LLM processing error: {str(e)}")
        return intelligence  # Fallback to raw intelligence


async def gather_department_intelligence(department: str, scope: str, api_key: str) -> Dict:
    """Gather intelligence for a specific department."""
    # Define queries based on department
    queries = {
        "lakshmi": "Latest trends in fintech, payment processing, and financial analytics in the last 24 hours",
        "vishwakarma": "Latest developments in software engineering, AI/ML, and cloud infrastructure",
        "agni": "Latest in energy management, infrastructure monitoring, and system optimization",
        "indra": "Latest cybersecurity threats, vulnerabilities, and security best practices",
        "vayu": "Latest in web performance optimization, CDN technologies, and caching strategies",
        "yama": "Latest compliance updates, GDPR changes, and regulatory requirements",
        "kubera": "Latest in operations management, resource optimization, and procurement",
        "surya": "Latest in EV charging technology, energy management, and renewable energy",
        "brahma": "Latest product innovation trends, user experience, and product strategy",
        "saraswati": "Latest in educational technology, content delivery, and learning platforms",
        "varuna": "Latest in customer service, communication trends, and CRM technologies",
        "pragya": "Latest market research tools, competitive intelligence, and analytics trends"
    }
    
    query = queries.get(department, f"Latest developments relevant to {department} operations")
    
    logger.info(f"Gathering intelligence for {department}: {query}")
    raw_intelligence = await query_perplexity(query, api_key)
    
    # Process with LLM to extract relevant insights
    processed_intelligence = await process_with_llm(raw_intelligence["content"], department)
    
    return {
        "department": department,
        "scope": scope,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "query": query,
        "raw_intelligence": raw_intelligence["content"],
        "processed_intelligence": processed_intelligence,
        "citations": raw_intelligence.get("citations", []),
        "model_used": raw_intelligence.get("model", "unknown")
    }


async def save_intelligence(intelligence: Dict, department: str, scope: str):
    """Save intelligence to post-data directory."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    
    # Create department-specific directory
    dept_dir = KNOWLEDGE_BASE_PATH / "post-data" / "department-specific" / scope / department
    dept_dir.mkdir(parents=True, exist_ok=True)
    
    # Save to dated file
    file_path = dept_dir / f"{today}.json"
    
    with open(file_path, "w") as f:
        json.dump(intelligence, f, indent=2)
    
    logger.info(f"Saved intelligence for {department} to {file_path}")
    
    # Also save to daily digest
    digest_dir = KNOWLEDGE_BASE_PATH / "post-data" / "daily-digest" / today
    digest_dir.mkdir(parents=True, exist_ok=True)
    
    digest_file = digest_dir / f"{department}.json"
    with open(digest_file, "w") as f:
        json.dump(intelligence, f, indent=2)


async def async_daily_learning_pipeline():
    """Async implementation of daily learning pipeline."""
    logger.info("Starting daily learning pipeline...")
    
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        logger.error("PERPLEXITY_API_KEY not found in environment")
        return {"status": "error", "message": "Missing Perplexity API key"}
    
    results = []
    
    # Process internal departments
    for department in DEPARTMENTS["internal"]:
        try:
            intelligence = await gather_department_intelligence(department, "internal", api_key)
            await save_intelligence(intelligence, department, "internal")
            results.append({"department": department, "status": "success"})
            logger.info(f"Completed intelligence gathering for {department}")
            # Small delay to avoid rate limiting
            await asyncio.sleep(2)
        except Exception as e:
            logger.error(f"Error processing {department}: {str(e)}")
            results.append({"department": department, "status": "error", "error": str(e)})
    
    # Process external departments
    for department in DEPARTMENTS["external"]:
        try:
            intelligence = await gather_department_intelligence(department, "external", api_key)
            await save_intelligence(intelligence, department, "external")
            results.append({"department": department, "status": "success"})
            logger.info(f"Completed intelligence gathering for {department}")
            await asyncio.sleep(2)
        except Exception as e:
            logger.error(f"Error processing {department}: {str(e)}")
            results.append({"department": department, "status": "error", "error": str(e)})
    
    # Generate summary
    summary = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_departments": len(results),
        "successful": len([r for r in results if r["status"] == "success"]),
        "failed": len([r for r in results if r["status"] == "error"]),
        "results": results
    }
    
    # Save summary
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    summary_dir = KNOWLEDGE_BASE_PATH / "post-data" / "daily-digest" / today
    summary_dir.mkdir(parents=True, exist_ok=True)
    
    with open(summary_dir / "summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    logger.info(f"Daily learning pipeline completed. Success: {summary['successful']}/{summary['total_departments']}")
    return summary


@shared_task(name="app.tasks.daily_learning.daily_learning_pipeline", bind=True)
def daily_learning_pipeline(self):
    """Celery task wrapper for daily learning pipeline."""
    logger.info("Daily learning pipeline task started")
    
    # Run async function in sync context
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        result = loop.run_until_complete(async_daily_learning_pipeline())
        return result
    except Exception as e:
        logger.error(f"Daily learning pipeline failed: {str(e)}")
        return {"status": "error", "message": str(e)}
    finally:
        loop.close()
