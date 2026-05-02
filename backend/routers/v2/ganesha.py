"""GANESHA v2.0 Backend Router - Analytics & Agent Management"""
from fastapi import APIRouter, HTTPException
from typing import Optional

router = APIRouter(prefix="/ganesha", tags=["GANESHA v2.0"])

# 36-Agent Registry
AGENTS = [
    # URGAA (8 agents)
    {"agent_id": "U-AI-01", "name": "SURYA", "product": "URGAA", "specialty": "Revenue Insight", "model": "claude-3-5-sonnet-20241022", "tier": "tier_1"},
    {"agent_id": "U-AI-02", "name": "VARUNA", "product": "URGAA", "specialty": "Demand Prediction", "model": "claude-3-5-haiku-20241022", "tier": "tier_2"},
    {"agent_id": "U-AI-03", "name": "KUBER", "product": "URGAA", "specialty": "Dynamic Pricing", "model": "claude-3-5-haiku-20241022", "tier": "tier_2"},
    {"agent_id": "U-AI-04", "name": "BHUMI", "product": "URGAA", "specialty": "Site Scoring", "model": "gemini-2.0-flash-exp", "tier": "tier_3"},
    {"agent_id": "U-AI-05", "name": "VAYU", "product": "URGAA", "specialty": "Task Prioritization", "model": "gemini-2.0-flash-exp", "tier": "tier_3"},
    {"agent_id": "U-AI-06", "name": "AGNI", "product": "URGAA", "specialty": "Health Monitoring", "model": "claude-3-5-sonnet-20241022", "tier": "tier_1"},
    {"agent_id": "U-AI-07", "name": "SHIV", "product": "URGAA", "specialty": "Auto-Rectification", "model": "claude-3-5-haiku-20241022", "tier": "tier_2"},
    {"agent_id": "U-AI-08", "name": "VISHWAKARMA", "product": "URGAA", "specialty": "Troubleshooting", "model": "claude-3-5-haiku-20241022", "tier": "tier_2"},
    # GSTSAAS (10 agents)
    {"agent_id": "G-AI-01", "name": "LAKSHMI", "product": "GSTSAAS", "specialty": "Profit Target", "model": "claude-3-5-sonnet-20241022", "tier": "tier_1"},
    {"agent_id": "G-AI-02", "name": "DHANVANTARI", "product": "GSTSAAS", "specialty": "Cash Flow", "model": "claude-3-5-haiku-20241022", "tier": "tier_2"},
    {"agent_id": "G-AI-03", "name": "NARADA", "product": "GSTSAAS", "specialty": "Churn Alert", "model": "gemini-2.0-flash-exp", "tier": "tier_3"},
    {"agent_id": "G-AI-04", "name": "CHANAKYA", "product": "GSTSAAS", "specialty": "Opportunity Detection", "model": "claude-3-5-haiku-20241022", "tier": "tier_2"},
    {"agent_id": "G-AI-05", "name": "BRIHASPATI", "product": "GSTSAAS", "specialty": "Quote Generation", "model": "gemini-2.0-flash-exp", "tier": "tier_3"},
    {"agent_id": "G-AI-06", "name": "VYASA", "product": "GSTSAAS", "specialty": "Follow-up", "model": "gemini-2.0-flash-exp", "tier": "tier_3"},
    {"agent_id": "G-AI-07", "name": "KUBERA", "product": "GSTSAAS", "specialty": "Inventory Reorder", "model": "claude-3-5-haiku-20241022", "tier": "tier_2"},
    {"agent_id": "G-AI-08", "name": "VAISRAVANA", "product": "GSTSAAS", "specialty": "Vendor Comparison", "model": "gemini-2.0-flash-exp", "tier": "tier_3"},
    {"agent_id": "G-AI-09", "name": "ASHWINI", "product": "GSTSAAS", "specialty": "Repair Guide", "model": "claude-3-5-haiku-20241022", "tier": "tier_2"},
    {"agent_id": "G-AI-10", "name": "GURU", "product": "GSTSAAS", "specialty": "Skill Gap", "model": "claude-3-5-sonnet-20241022", "tier": "tier_1"},
    # IGNITION (9 agents)
    {"agent_id": "I-AI-01", "name": "SARASWATI", "product": "IGNITION", "specialty": "Charger Recommendation", "model": "gemini-2.0-flash-exp", "tier": "tier_3"},
    {"agent_id": "I-AI-02", "name": "HANUMAN", "product": "IGNITION", "specialty": "Route Planning", "model": "claude-3-5-sonnet-20241022", "tier": "tier_1"},
    {"agent_id": "I-AI-03", "name": "ARTHA", "product": "IGNITION", "specialty": "Expense Tracking", "model": "gemini-2.0-flash-exp", "tier": "tier_3"},
    {"agent_id": "I-AI-04", "name": "PARVATI", "product": "IGNITION", "specialty": "Workshop Finder", "model": "gemini-2.0-flash-exp", "tier": "tier_3"},
    {"agent_id": "I-AI-05", "name": "GANESHA-C", "product": "IGNITION", "specialty": "Consumer Chat", "model": "claude-3-5-haiku-20241022", "tier": "tier_2"},
    {"agent_id": "I-AI-06", "name": "KARNA", "product": "IGNITION", "specialty": "Shift Planning", "model": "claude-3-5-haiku-20241022", "tier": "tier_2"},
    {"agent_id": "I-AI-07", "name": "INDRA", "product": "IGNITION", "specialty": "Fleet Reporting", "model": "claude-3-5-sonnet-20241022", "tier": "tier_1"},
    {"agent_id": "I-AI-08", "name": "YAMA", "product": "IGNITION", "specialty": "Fleet Health", "model": "claude-3-5-haiku-20241022", "tier": "tier_2"},
    {"agent_id": "I-AI-09", "name": "DHANA", "product": "IGNITION", "specialty": "Fleet Cost", "model": "claude-3-5-sonnet-20241022", "tier": "tier_1"},
    # ARJUN (8 agents)
    {"agent_id": "A-AI-01", "name": "VIDYA", "product": "ARJUN", "specialty": "Course Recommendation", "model": "gemini-2.0-flash-exp", "tier": "tier_3"},
    {"agent_id": "A-AI-02", "name": "DRONA", "product": "ARJUN", "specialty": "Adaptive Learning", "model": "claude-3-5-sonnet-20241022", "tier": "tier_1"},
    {"agent_id": "A-AI-03", "name": "ARJUNA", "product": "ARJUN", "specialty": "Practice Coach", "model": "claude-3-5-haiku-20241022", "tier": "tier_2"},
    {"agent_id": "A-AI-04", "name": "CHITRAGUPTA", "product": "ARJUN", "specialty": "Certification", "model": "gemini-2.0-flash-exp", "tier": "tier_3"},
    {"agent_id": "A-AI-05", "name": "PARASHURAMA", "product": "ARJUN", "specialty": "Skill Gap", "model": "claude-3-5-sonnet-20241022", "tier": "tier_1"},
    {"agent_id": "A-AI-06", "name": "NAKULA", "product": "ARJUN", "specialty": "Career Matching", "model": "claude-3-5-haiku-20241022", "tier": "tier_2"},
    {"agent_id": "A-AI-07", "name": "SAHADEVA", "product": "ARJUN", "specialty": "Batch Insights", "model": "claude-3-5-haiku-20241022", "tier": "tier_2"},
    {"agent_id": "A-AI-08", "name": "BHISHMA", "product": "ARJUN", "specialty": "Employer Matching", "model": "claude-3-5-haiku-20241022", "tier": "tier_2"},
    # Master Orchestrator
    {"agent_id": "GANESHA", "name": "GANESHA", "product": "ALL", "specialty": "Master Orchestrator", "model": "claude-3-5-sonnet-20241022", "tier": "tier_1"}
]

MODEL_PRICING = {
    "claude-3-5-sonnet-20241022": {"input": 3.0, "output": 15.0},
    "claude-3-5-haiku-20241022": {"input": 1.0, "output": 5.0},
    "gemini-2.0-flash-exp": {"input": 0.0, "output": 0.0}
}

@router.get("/models/stats")
async def get_model_stats():
    """Get model usage statistics and cost analysis"""
    tier_dist = {"tier_1": 0, "tier_2": 0, "tier_3": 0}
    model_dist = {}
    
    for agent in AGENTS:
        tier_dist[agent["tier"]] += 1
        model = agent["model"]
        model_dist[model] = model_dist.get(model, 0) + 1
    
    # Calculate costs (1000 queries/agent, 500 input + 1000 output tokens)
    tier_costs = {
        "tier_1": tier_dist["tier_1"] * 1000 * (500 * 3.0 + 1000 * 15.0) / 1_000_000,
        "tier_2": tier_dist["tier_2"] * 1000 * (500 * 1.0 + 1000 * 5.0) / 1_000_000,
        "tier_3": 0.0
    }
    
    return {
        "tier_distribution": tier_dist,
        "model_distribution": model_dist,
        "estimated_costs": {
            "total_monthly_cost_usd": sum(tier_costs.values()),
            "breakdown_by_tier": tier_costs
        },
        "pricing_per_model": MODEL_PRICING
    }

@router.get("/rag/stats")
async def get_rag_stats():
    """Get RAG knowledge base statistics"""
    return {
        "status": "connected",
        "index": "kailashai",
        "stats": {
            "total_vectors": 851,
            "dimension": 384,
            "index_fullness": 0.0
        },
        "embedding_model": "all-MiniLM-L6-v2"
    }

@router.get("/agents")
async def get_agents(product: Optional[str] = None, tier: Optional[str] = None):
    """List all agents with optional filtering"""
    filtered = AGENTS
    
    if product:
        filtered = [a for a in filtered if a["product"] == product or a["product"] == "ALL"]
    if tier:
        filtered = [a for a in filtered if a["tier"] == tier]
    
    summary = {
        "by_product": {},
        "by_tier": {"tier_1": 0, "tier_2": 0, "tier_3": 0},
        "by_model": {}
    }
    
    for agent in AGENTS:
        prod = agent["product"]
        summary["by_product"][prod] = summary["by_product"].get(prod, 0) + 1
        summary["by_tier"][agent["tier"]] += 1
        model = agent["model"]
        summary["by_model"][model] = summary["by_model"].get(model, 0) + 1
    
    return {
        "agents": filtered,
        "total_count": len(filtered),
        "summary": summary
    }

@router.get("/agents/{agent_id}")
async def get_agent(agent_id: str):
    """Get detailed information about specific agent"""
    agent = next((a for a in AGENTS if a["agent_id"] == agent_id), None)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    return {
        **agent,
        "pricing": MODEL_PRICING.get(agent["model"], {}),
        "tier_description": {
            "tier_1": "Complex Reasoning - High accuracy, deep analysis",
            "tier_2": "Standard Operations - Balanced performance",
            "tier_3": "Volume Operations - High throughput, cost-effective"
        }.get(agent["tier"])
    }

@router.get("/stats")
async def get_platform_stats():
    """Get general GANESHA platform statistics"""
    products = list(set(a["product"] for a in AGENTS if a["product"] != "ALL"))
    
    return {
        "platform": "GANESHA v2.0",
        "version": "2.0.0",
        "status": "operational",
        "deployment": "URGAA Platform (Go4Garage)",
        "statistics": {
            "total_agents": len(AGENTS),
            "products": len(products),
            "product_names": products
        },
        "capabilities": {
            "multi_model": True,
            "cost_optimization": True,
            "rag_enabled": True
        },
        "models": list(MODEL_PRICING.keys())
    }

@router.get("/route/preview")
async def preview_routing(query: str):
    """Preview agent routing for a query"""
    # Simple keyword-based routing
    query_lower = query.lower()
    
    if "revenue" in query_lower or "profit" in query_lower:
        agent = next(a for a in AGENTS if a["agent_id"] == "U-AI-01")
    elif "price" in query_lower or "pricing" in query_lower:
        agent = next(a for a in AGENTS if a["agent_id"] == "U-AI-03")
    elif "health" in query_lower or "monitor" in query_lower:
        agent = next(a for a in AGENTS if a["agent_id"] == "U-AI-06")
    else:
        agent = next(a for a in AGENTS if a["agent_id"] == "GANESHA")
    
    return {
        "query": query,
        "routed_to": {
            "agent_id": agent["agent_id"],
            "name": agent["name"],
            "specialty": agent["specialty"]
        },
        "confidence": 0.85
    }
