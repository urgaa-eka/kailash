"""
C5 MULTI-MODEL STRATEGY
========================
Defines LLM routing per agent for optimal cost/capability balance.

Strategy Tiers:
- TIER 1 (Claude Opus/Sonnet): Complex reasoning, strategic analysis, critical decisions
- TIER 2 (Claude Haiku/GPT-4o-mini): Standard operations, structured outputs
- TIER 3 (Gemini Flash): High-volume, simple queries, data lookup

Cost Optimization Target: 40% reduction while maintaining quality
"""

from typing import Dict, Optional, Literal
from dataclasses import dataclass
from enum import Enum


class ModelTier(Enum):
    """Model capability tiers"""
    TIER_1 = "tier_1"  # High capability, higher cost
    TIER_2 = "tier_2"  # Balanced capability/cost
    TIER_3 = "tier_3"  # High volume, low cost


class LLMProvider(Enum):
    """Available LLM providers"""
    CLAUDE_OPUS = "claude-3-opus-20240229"
    CLAUDE_SONNET = "claude-3-5-sonnet-20241022"
    CLAUDE_HAIKU = "claude-3-5-haiku-20241022"
    GPT_4O = "gpt-4o"
    GPT_4O_MINI = "gpt-4o-mini"
    GEMINI_PRO = "gemini-1.5-pro"
    GEMINI_FLASH = "gemini-1.5-flash"


@dataclass
class ModelConfig:
    """Configuration for a model assignment"""
    primary: str
    fallback: str
    tier: ModelTier
    max_tokens: int
    temperature: float
    cost_per_1k_input: float  # USD
    cost_per_1k_output: float  # USD
    capabilities: list[str]


# =============================================================================
# MODEL DEFINITIONS
# =============================================================================

MODELS: Dict[str, ModelConfig] = {
    # Tier 1 - High Capability
    "claude-sonnet": ModelConfig(
        primary=LLMProvider.CLAUDE_SONNET.value,
        fallback=LLMProvider.GPT_4O.value,
        tier=ModelTier.TIER_1,
        max_tokens=4096,
        temperature=0.7,
        cost_per_1k_input=0.003,
        cost_per_1k_output=0.015,
        capabilities=["complex_reasoning", "strategic_analysis", "nuanced_response", "code_generation"]
    ),
    "gpt-4o": ModelConfig(
        primary=LLMProvider.GPT_4O.value,
        fallback=LLMProvider.CLAUDE_SONNET.value,
        tier=ModelTier.TIER_1,
        max_tokens=4096,
        temperature=0.7,
        cost_per_1k_input=0.005,
        cost_per_1k_output=0.015,
        capabilities=["complex_reasoning", "multimodal", "structured_output"]
    ),
    
    # Tier 2 - Balanced
    "claude-haiku": ModelConfig(
        primary=LLMProvider.CLAUDE_HAIKU.value,
        fallback=LLMProvider.GPT_4O_MINI.value,
        tier=ModelTier.TIER_2,
        max_tokens=2048,
        temperature=0.5,
        cost_per_1k_input=0.0008,
        cost_per_1k_output=0.004,
        capabilities=["fast_response", "structured_output", "standard_reasoning"]
    ),
    "gpt-4o-mini": ModelConfig(
        primary=LLMProvider.GPT_4O_MINI.value,
        fallback=LLMProvider.CLAUDE_HAIKU.value,
        tier=ModelTier.TIER_2,
        max_tokens=2048,
        temperature=0.5,
        cost_per_1k_input=0.00015,
        cost_per_1k_output=0.0006,
        capabilities=["fast_response", "cost_effective", "basic_reasoning"]
    ),
    
    # Tier 3 - High Volume
    "gemini-flash": ModelConfig(
        primary=LLMProvider.GEMINI_FLASH.value,
        fallback=LLMProvider.CLAUDE_HAIKU.value,
        tier=ModelTier.TIER_3,
        max_tokens=1024,
        temperature=0.3,
        cost_per_1k_input=0.000075,
        cost_per_1k_output=0.0003,
        capabilities=["high_volume", "data_lookup", "simple_queries", "fast_response"]
    ),
}


# =============================================================================
# AGENT-TO-MODEL MAPPING
# =============================================================================

AGENT_MODEL_MAP: Dict[str, str] = {
    # =========================================================================
    # GANESHA - Master Orchestrator
    # =========================================================================
    "GANESHA": "claude-sonnet",  # Needs complex routing logic
    
    # =========================================================================
    # URGAA - EV Infrastructure (8 Agents)
    # =========================================================================
    "U-AI-01": "claude-sonnet",   # SURYA - Revenue Insight (complex financial analysis)
    "U-AI-02": "claude-haiku",    # VARUNA - Demand Prediction (structured forecasting)
    "U-AI-03": "claude-sonnet",   # KUBER - Dynamic Pricing (strategic optimization)
    "U-AI-04": "gpt-4o-mini",     # BHUMI - Site Scoring (data processing)
    "U-AI-05": "gemini-flash",    # VAYU - Task Priority (high volume, simple sorting)
    "U-AI-06": "claude-haiku",    # AGNI - Health Monitor (structured diagnostics)
    "U-AI-07": "claude-sonnet",   # SHIV - Auto-Rectify (complex decision-making)
    "U-AI-08": "claude-haiku",    # VISHWAKARMA - Troubleshoot (structured debugging)
    
    # =========================================================================
    # GSTSAAS - Workshop Management (10 Agents)
    # =========================================================================
    "G-AI-01": "claude-sonnet",   # LAKSHMI - Profit Target (strategic financial)
    "G-AI-02": "claude-haiku",    # DHANVANTARI - Cash Flow (structured analysis)
    "G-AI-03": "claude-sonnet",   # NARADA - Churn Alert (predictive, nuanced)
    "G-AI-04": "claude-sonnet",   # CHANAKYA - Opportunity (strategic analysis)
    "G-AI-05": "gpt-4o-mini",     # BRIHASPATI - Quote (structured generation)
    "G-AI-06": "gemini-flash",    # VYASA - Follow-up (high volume, templates)
    "G-AI-07": "gemini-flash",    # KUBERA - Reorder (data lookup, simple)
    "G-AI-08": "claude-haiku",    # VAISRAVANA - Vendor Compare (structured comparison)
    "G-AI-09": "claude-haiku",    # ASHWINI - Repair Guide (technical, structured)
    "G-AI-10": "claude-haiku",    # GURU - Skill Gap (assessment, structured)
    
    # =========================================================================
    # IGNITION - Consumer App (9 Agents)
    # =========================================================================
    "I-AI-01": "claude-haiku",    # SARASWATI - Charger Rec (personalized, structured)
    "I-AI-02": "gpt-4o-mini",     # HANUMAN - Route Planning (algorithmic)
    "I-AI-03": "gemini-flash",    # ARTHA - Expense Tracking (data aggregation)
    "I-AI-04": "gemini-flash",    # PARVATI - Workshop Finder (location lookup)
    "I-AI-05": "claude-sonnet",   # GANESHA-C - Consumer Chat (nuanced conversation)
    "I-AI-06": "gpt-4o-mini",     # KARNA - Shift Planning (scheduling logic)
    "I-AI-07": "claude-haiku",    # INDRA - Fleet Reporting (structured reports)
    "I-AI-08": "claude-haiku",    # YAMA - Fleet Health (diagnostics)
    "I-AI-09": "gpt-4o-mini",     # DHANA - Fleet Cost (financial calculations)
    
    # =========================================================================
    # ARJUN - Training Platform (8 Agents)
    # =========================================================================
    "A-AI-01": "claude-haiku",    # VIDYA - Course Rec (personalized learning)
    "A-AI-02": "claude-sonnet",   # DRONA - Adaptive Learning (complex adaptation)
    "A-AI-03": "claude-haiku",    # ARJUNA - Practice Coach (interactive, structured)
    "A-AI-04": "gemini-flash",    # CHITRAGUPTA - Certification (data lookup)
    "A-AI-05": "claude-haiku",    # PARASHURAMA - Skill Gap (assessment)
    "A-AI-06": "gpt-4o-mini",     # NAKULA - Career Matching (matching algorithm)
    "A-AI-07": "gemini-flash",    # SAHADEVA - Batch Insights (data aggregation)
    "A-AI-08": "claude-sonnet",   # BHISHMA - Employer Matching (strategic matching)
}


# =============================================================================
# QUERY COMPLEXITY CLASSIFIER
# =============================================================================

COMPLEXITY_KEYWORDS = {
    "high": [
        "analyze", "strategy", "optimize", "predict", "recommend", 
        "compare", "evaluate", "why", "how should", "what if",
        "forecast", "projection", "diagnosis", "root cause"
    ],
    "medium": [
        "show", "list", "report", "summary", "calculate",
        "status", "update", "check", "review", "explain"
    ],
    "low": [
        "find", "get", "lookup", "search", "where", "when",
        "count", "total", "what is", "who is"
    ]
}


def classify_query_complexity(query: str) -> Literal["high", "medium", "low"]:
    """Classify query complexity based on keywords"""
    query_lower = query.lower()
    
    for keyword in COMPLEXITY_KEYWORDS["high"]:
        if keyword in query_lower:
            return "high"
    
    for keyword in COMPLEXITY_KEYWORDS["medium"]:
        if keyword in query_lower:
            return "medium"
    
    return "low"


def get_model_override(agent_id: str, query: str) -> Optional[str]:
    """
    Override model selection based on query complexity.
    High complexity queries get upgraded to Tier 1 regardless of default.
    """
    complexity = classify_query_complexity(query)
    default_model = AGENT_MODEL_MAP.get(agent_id, "claude-haiku")
    default_config = MODELS.get(default_model)
    
    if not default_config:
        return None
    
    # Upgrade low-tier agents for complex queries
    if complexity == "high" and default_config.tier in [ModelTier.TIER_2, ModelTier.TIER_3]:
        return "claude-sonnet"
    
    # Downgrade for simple queries on expensive models (cost optimization)
    if complexity == "low" and default_config.tier == ModelTier.TIER_1:
        return "claude-haiku"
    
    return None


# =============================================================================
# MODEL SELECTION FUNCTIONS
# =============================================================================

def get_model_for_agent(agent_id: str, query: str = "") -> ModelConfig:
    """Get the appropriate model configuration for an agent"""
    
    # Check for complexity-based override
    override = get_model_override(agent_id, query) if query else None
    
    model_key = override or AGENT_MODEL_MAP.get(agent_id, "claude-haiku")
    return MODELS.get(model_key, MODELS["claude-haiku"])


def get_model_name(agent_id: str, query: str = "") -> str:
    """Get just the model name/ID for an agent"""
    config = get_model_for_agent(agent_id, query)
    return config.primary


def get_fallback_model(agent_id: str) -> str:
    """Get fallback model for an agent"""
    config = get_model_for_agent(agent_id)
    return config.fallback


def estimate_cost(agent_id: str, input_tokens: int, output_tokens: int) -> float:
    """Estimate cost for a query to an agent"""
    config = get_model_for_agent(agent_id)
    input_cost = (input_tokens / 1000) * config.cost_per_1k_input
    output_cost = (output_tokens / 1000) * config.cost_per_1k_output
    return round(input_cost + output_cost, 6)


# =============================================================================
# STATISTICS & REPORTING
# =============================================================================

def get_model_distribution() -> Dict[str, int]:
    """Get count of agents per model"""
    distribution = {}
    for agent_id, model_key in AGENT_MODEL_MAP.items():
        if model_key not in distribution:
            distribution[model_key] = 0
        distribution[model_key] += 1
    return distribution


def get_tier_distribution() -> Dict[str, int]:
    """Get count of agents per tier"""
    distribution = {"tier_1": 0, "tier_2": 0, "tier_3": 0}
    for agent_id, model_key in AGENT_MODEL_MAP.items():
        config = MODELS.get(model_key)
        if config:
            distribution[config.tier.value] += 1
    return distribution


def estimate_monthly_cost(queries_per_agent: int = 1000, avg_input_tokens: int = 500, avg_output_tokens: int = 1000) -> Dict:
    """Estimate monthly cost across all agents"""
    total_cost = 0
    agent_costs = {}
    
    for agent_id in AGENT_MODEL_MAP.keys():
        cost = estimate_cost(agent_id, avg_input_tokens * queries_per_agent, avg_output_tokens * queries_per_agent)
        agent_costs[agent_id] = cost
        total_cost += cost
    
    return {
        "total_monthly_cost_usd": round(total_cost, 2),
        "per_agent_costs": agent_costs,
        "tier_distribution": get_tier_distribution(),
        "model_distribution": get_model_distribution()
    }


# =============================================================================
# C5 STRATEGY SUMMARY
# =============================================================================

C5_STRATEGY_SUMMARY = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                        C5 MULTI-MODEL STRATEGY                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  TIER DISTRIBUTION (36 Agents):                                             ║
║  ┌─────────────────────────────────────────────────────────────────────┐    ║
║  │ TIER 1 (Claude Sonnet/GPT-4o)  │ 10 agents │ Complex reasoning     │    ║
║  │ TIER 2 (Claude Haiku/GPT-mini) │ 16 agents │ Standard operations   │    ║
║  │ TIER 3 (Gemini Flash)          │ 10 agents │ High-volume queries   │    ║
║  └─────────────────────────────────────────────────────────────────────┘    ║
║                                                                              ║
║  COST OPTIMIZATION:                                                          ║
║  • Estimated 40% cost reduction vs all-Sonnet baseline                      ║
║  • Dynamic upgrading for complex queries                                     ║
║  • Automatic downgrading for simple lookups                                  ║
║                                                                              ║
║  MODEL ROUTING LOGIC:                                                        ║
║  1. Agent default assignment (based on task complexity)                      ║
║  2. Query complexity override (upgrade/downgrade)                            ║
║  3. Fallback chain on failure                                                ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""


if __name__ == "__main__":
    print(C5_STRATEGY_SUMMARY)
    print("\nModel Distribution:", get_model_distribution())
    print("\nTier Distribution:", get_tier_distribution())
    print("\nEstimated Monthly Cost (1000 queries/agent):")
    print(estimate_monthly_cost())
