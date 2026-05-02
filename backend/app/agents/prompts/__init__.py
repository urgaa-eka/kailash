"""
Agent Prompts Registry
Central hub for all C4 system prompts across Go4Garage products
"""

from .ganesha_prompt import GANESHA_SYSTEM_PROMPT, AGENT_ROUTING_CONFIG, get_ganesha_prompt, get_routing_config
from .urgaa_prompts import URGAA_PROMPTS, get_urgaa_prompt, get_all_urgaa_prompts
from .gstsaas_prompts import GSTSAAS_PROMPTS, get_gstsaas_prompt, get_all_gstsaas_prompts
from .ignition_prompts import IGNITION_PROMPTS, get_ignition_prompt, get_all_ignition_prompts
from .arjun_prompts import ARJUN_PROMPTS, get_arjun_prompt, get_all_arjun_prompts


# =============================================================================
# UNIFIED AGENT REGISTRY
# =============================================================================
ALL_AGENTS = {
    "GANESHA": {
        "name": "GANESHA",
        "prompt": GANESHA_SYSTEM_PROMPT,
        "specialty": "Master Orchestrator",
        "product": "ALL"
    },
    **{k: {**v, "product": "URGAA"} for k, v in URGAA_PROMPTS.items()},
    **{k: {**v, "product": "GSTSAAS"} for k, v in GSTSAAS_PROMPTS.items()},
    **{k: {**v, "product": "IGNITION"} for k, v in IGNITION_PROMPTS.items()},
    **{k: {**v, "product": "ARJUN"} for k, v in ARJUN_PROMPTS.items()},
}


# Agent ID to Name mapping
AGENT_NAMES = {
    "GANESHA": "GANESHA",
    # URGAA
    "U-AI-01": "SURYA",
    "U-AI-02": "VARUNA",
    "U-AI-03": "KUBER",
    "U-AI-04": "BHUMI",
    "U-AI-05": "VAYU",
    "U-AI-06": "AGNI",
    "U-AI-07": "SHIV",
    "U-AI-08": "VISHWAKARMA",
    # GSTSAAS
    "G-AI-01": "LAKSHMI",
    "G-AI-02": "DHANVANTARI",
    "G-AI-03": "NARADA",
    "G-AI-04": "CHANAKYA",
    "G-AI-05": "BRIHASPATI",
    "G-AI-06": "VYASA",
    "G-AI-07": "KUBERA",
    "G-AI-08": "VAISRAVANA",
    "G-AI-09": "ASHWINI",
    "G-AI-10": "GURU",
    # IGNITION
    "I-AI-01": "SARASWATI",
    "I-AI-02": "HANUMAN",
    "I-AI-03": "ARTHA",
    "I-AI-04": "PARVATI",
    "I-AI-05": "GANESHA-C",
    "I-AI-06": "KARNA",
    "I-AI-07": "INDRA",
    "I-AI-08": "YAMA",
    "I-AI-09": "DHANA",
    # ARJUN
    "A-AI-01": "VIDYA",
    "A-AI-02": "DRONA",
    "A-AI-03": "ARJUNA",
    "A-AI-04": "CHITRAGUPTA",
    "A-AI-05": "PARASHURAMA",
    "A-AI-06": "NAKULA",
    "A-AI-07": "SAHADEVA",
    "A-AI-08": "BHISHMA",
}


def get_agent_prompt(agent_id: str) -> dict:
    """
    Get agent configuration by ID
    
    Args:
        agent_id: Agent identifier (e.g., "U-AI-01", "GANESHA")
        
    Returns:
        Dict with name, prompt, specialty, product
    """
    return ALL_AGENTS.get(agent_id, None)


def get_agent_by_name(name: str) -> dict:
    """
    Get agent configuration by name
    
    Args:
        name: Agent name (e.g., "SURYA", "LAKSHMI")
        
    Returns:
        Dict with name, prompt, specialty, product
    """
    for agent_id, config in ALL_AGENTS.items():
        if config.get("name") == name:
            return {"agent_id": agent_id, **config}
    return None


def get_agents_by_product(product: str) -> dict:
    """
    Get all agents for a specific product
    
    Args:
        product: Product name (URGAA, GSTSAAS, IGNITION, ARJUN)
        
    Returns:
        Dict of agents for that product
    """
    return {
        k: v for k, v in ALL_AGENTS.items()
        if v.get("product") == product or v.get("product") == "ALL"
    }


def list_all_agents() -> list:
    """
    List all available agents
    
    Returns:
        List of agent summaries
    """
    return [
        {
            "agent_id": agent_id,
            "name": config.get("name"),
            "specialty": config.get("specialty"),
            "product": config.get("product")
        }
        for agent_id, config in ALL_AGENTS.items()
    ]


def get_agent_count() -> dict:
    """Get count of agents by product"""
    counts = {"URGAA": 0, "GSTSAAS": 0, "IGNITION": 0, "ARJUN": 0, "ALL": 0}
    for config in ALL_AGENTS.values():
        product = config.get("product", "ALL")
        if product in counts:
            counts[product] += 1
    return counts


# =============================================================================
# INTENT ROUTING HELPERS
# =============================================================================
def route_to_agent(query: str, product_context: str = None) -> str:
    """
    Route a user query to the appropriate agent
    
    Args:
        query: User's query text
        product_context: Current product context (if known)
        
    Returns:
        Agent ID to handle the query
    """
    query_lower = query.lower()
    routing_config = get_routing_config()
    
    # If product context is known, search within that product first
    if product_context and product_context in routing_config:
        product_agents = routing_config[product_context]["agents"]
        for keyword, agent_id in product_agents.items():
            if keyword in query_lower:
                return agent_id
    
    # Search across all products
    for product, config in routing_config.items():
        # Check if query matches product keywords
        if any(kw in query_lower for kw in config.get("keywords", [])):
            # Find specific agent within product
            for keyword, agent_id in config.get("agents", {}).items():
                if keyword in query_lower:
                    return agent_id
    
    # Default to GANESHA orchestrator
    return "GANESHA"


# =============================================================================
# EXPORTS
# =============================================================================
__all__ = [
    # Main prompt retrieval
    "get_agent_prompt",
    "get_agent_by_name",
    "get_agents_by_product",
    "list_all_agents",
    "get_agent_count",
    
    # Routing
    "route_to_agent",
    "AGENT_ROUTING_CONFIG",
    
    # Direct access
    "ALL_AGENTS",
    "AGENT_NAMES",
    "GANESHA_SYSTEM_PROMPT",
    "URGAA_PROMPTS",
    "GSTSAAS_PROMPTS",
    "IGNITION_PROMPTS",
    "ARJUN_PROMPTS",
    
    # Individual getters
    "get_ganesha_prompt",
    "get_urgaa_prompt",
    "get_gstsaas_prompt",
    "get_ignition_prompt",
    "get_arjun_prompt",
]
