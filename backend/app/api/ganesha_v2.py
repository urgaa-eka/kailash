"""
GANESHA Orchestrator API v2.0
Enhanced with RAG and C4 Agent Prompts
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime
from bson import ObjectId
import json
import asyncio
import logging

from app.api.deps import get_current_active_user
from app.core.mongodb import get_db
from app.services.ganesha_orchestrator_v2 import get_orchestrator_v2
from app.core.config import get_settings
from app.models.user import User
from app.agents.prompts import list_all_agents, get_agent_prompt, route_to_agent

router = APIRouter(prefix="/v2", tags=["GANESHA v2.0"])
logger = logging.getLogger("kailash.ganesha.api.v2")
settings = get_settings()


# =============================================================================
# REQUEST/RESPONSE MODELS
# =============================================================================
class OrchestrateRequest(BaseModel):
    user_message: str
    conversation_history: Optional[List[Dict]] = []
    product_context: Optional[str] = None  # URGAA, GSTSAAS, IGNITION, ARJUN


class DirectAgentRequest(BaseModel):
    agent_id: str
    query: str
    context: Optional[Dict] = {}


class QuickActionRequest(BaseModel):
    action: str  # 'status', 'review', 'next_steps', 'agents'


# =============================================================================
# MAIN ORCHESTRATION ENDPOINT
# =============================================================================
@router.post("/ganesha/orchestrate")
async def orchestrate_request_v2(
    request: OrchestrateRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Main orchestration endpoint v2.0
    
    Features:
    - RAG knowledge retrieval from Pinecone
    - Intelligent routing to 35+ specialist agents
    - C4 system prompts for contextual responses
    - Real-time streaming response
    """
    
    db = get_db()
    
    # Get orchestrator with RAG
    orchestrator = get_orchestrator_v2(
        anthropic_key=settings.anthropic_api_key,
        pinecone_key=settings.PINECONE_API_KEY,
        pinecone_index=settings.PINECONE_INDEX,
        emergent_url=getattr(settings, 'emergent_api_url', None),
        emergent_key=getattr(settings, 'emergent_api_key', None)
    )
    
    # Build user context
    user_context = {
        'user_name': getattr(current_user, 'full_name', current_user.kailash_code),
        'kailash_code': current_user.kailash_code,
        'role': 'Admin' if current_user.is_admin else 'User',
        'organization': getattr(current_user, 'organization', 'Go4Garage'),
        'product': request.product_context or 'URGAA'
    }
    
    # Store command in database
    command_doc = {
        'user_id': current_user.kailash_code,
        'message': request.user_message,
        'product_context': request.product_context,
        'created_at': datetime.now(),
        'status': 'processing',
        'version': '2.0'
    }
    
    result = await db.ganesha_commands.insert_one(command_doc)
    command_id = str(result.inserted_id)
    
    async def generate_stream():
        """Generate SSE stream with RAG-enhanced responses"""
        
        agent_id = None
        rag_used = False
        
        try:
            async for event in orchestrator.process_request(
                user_message=request.user_message,
                conversation_history=request.conversation_history,
                user_context=user_context
            ):
                # Track metadata
                if event.get('type') == 'routing':
                    agent_id = event.get('agent_id')
                if event.get('type') == 'rag_complete':
                    rag_used = True
                
                # Send event to client
                yield f"data: {json.dumps(event)}\n\n"
                await asyncio.sleep(0.02)
            
            # Update command status
            await db.ganesha_commands.update_one(
                {'_id': ObjectId(command_id)},
                {
                    '$set': {
                        'status': 'completed',
                        'completed_at': datetime.now(),
                        'agent_id': agent_id,
                        'rag_used': rag_used
                    }
                }
            )
            
        except Exception as e:
            logger.error(f"Stream error: {str(e)}")
            
            error_event = {
                'type': 'error',
                'message': str(e),
                'timestamp': datetime.now().isoformat()
            }
            yield f"data: {json.dumps(error_event)}\n\n"
            
            await db.ganesha_commands.update_one(
                {'_id': ObjectId(command_id)},
                {
                    '$set': {
                        'status': 'error',
                        'error': str(e),
                        'completed_at': datetime.now()
                    }
                }
            )
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'X-Accel-Buffering': 'no'
        }
    )


# =============================================================================
# DIRECT AGENT QUERY
# =============================================================================
@router.post("/ganesha/agent/query")
async def query_agent_directly(
    request: DirectAgentRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Query a specific agent directly
    Bypasses GANESHA routing for targeted queries
    """
    
    # Verify agent exists
    agent_config = get_agent_prompt(request.agent_id)
    if not agent_config:
        raise HTTPException(
            status_code=404,
            detail=f"Agent {request.agent_id} not found"
        )
    
    orchestrator = get_orchestrator_v2(
        anthropic_key=settings.anthropic_api_key,
        pinecone_key=settings.PINECONE_API_KEY,
        pinecone_index=settings.PINECONE_INDEX
    )
    
    user_context = {
        'user_name': getattr(current_user, 'full_name', current_user.kailash_code),
        'kailash_code': current_user.kailash_code,
        'role': 'Admin' if current_user.is_admin else 'User',
        'organization': 'Go4Garage',
        'product': agent_config.get('product', 'URGAA'),
        **request.context
    }
    
    response = await orchestrator.query_specialist(
        agent_id=request.agent_id,
        query=request.query,
        user_context=user_context
    )
    
    return {
        'agent_id': request.agent_id,
        'agent_name': agent_config.get('name'),
        'specialty': agent_config.get('specialty'),
        'response': response,
        'timestamp': datetime.now().isoformat()
    }


# =============================================================================
# AGENT DISCOVERY
# =============================================================================
@router.get("/ganesha/agents")
async def list_available_agents(
    product: Optional[str] = Query(None, description="Filter by product"),
    current_user: User = Depends(get_current_active_user)
):
    """
    List all available AI agents
    
    Products: URGAA, GSTSAAS, IGNITION, ARJUN
    """
    
    agents = list_all_agents()
    
    if product:
        agents = [a for a in agents if a.get('product') == product or a.get('product') == 'ALL']
    
    # Group by product
    grouped = {}
    for agent in agents:
        prod = agent.get('product', 'OTHER')
        if prod not in grouped:
            grouped[prod] = []
        grouped[prod].append(agent)
    
    return {
        'total_agents': len(agents),
        'agents': agents,
        'by_product': grouped
    }


@router.get("/ganesha/agents/{agent_id}")
async def get_agent_details(
    agent_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get detailed information about a specific agent"""
    
    agent_config = get_agent_prompt(agent_id)
    
    if not agent_config:
        raise HTTPException(
            status_code=404,
            detail=f"Agent {agent_id} not found"
        )
    
    return {
        'agent_id': agent_id,
        'name': agent_config.get('name'),
        'specialty': agent_config.get('specialty'),
        'product': agent_config.get('product'),
        'prompt_preview': agent_config.get('prompt', '')[:500] + '...'
    }


# =============================================================================
# ROUTING PREVIEW
# =============================================================================
@router.post("/ganesha/route/preview")
async def preview_routing(
    query: str = Query(..., description="Query to route"),
    product: Optional[str] = Query(None, description="Product context"),
    current_user: User = Depends(get_current_active_user)
):
    """
    Preview which agent would handle a query
    Useful for debugging and understanding routing
    """
    
    agent_id = route_to_agent(query, product)
    agent_config = get_agent_prompt(agent_id)
    
    return {
        'query': query,
        'product_context': product,
        'routed_to': {
            'agent_id': agent_id,
            'name': agent_config.get('name') if agent_config else 'GANESHA',
            'specialty': agent_config.get('specialty') if agent_config else 'Master Orchestrator',
            'product': agent_config.get('product') if agent_config else 'ALL'
        }
    }


# =============================================================================
# RAG STATISTICS
# =============================================================================
@router.get("/ganesha/rag/stats")
async def get_rag_statistics(
    current_user: User = Depends(get_current_active_user)
):
    """Get RAG knowledge base statistics"""
    
    orchestrator = get_orchestrator_v2(
        anthropic_key=settings.anthropic_api_key,
        pinecone_key=settings.PINECONE_API_KEY,
        pinecone_index=settings.PINECONE_INDEX
    )
    
    stats = orchestrator.get_rag_stats()
    
    return {
        'index': settings.PINECONE_INDEX,
        'stats': stats,
        'status': 'connected' if not stats.get('error') else 'error'
    }


# =============================================================================
# C5 MODEL STATISTICS
# =============================================================================
@router.get("/ganesha/models/stats")
async def get_model_statistics(
    current_user: User = Depends(get_current_active_user)
):
    """Get C5 multi-model usage statistics"""
    
    orchestrator = get_orchestrator_v2(
        anthropic_key=settings.anthropic_api_key,
        pinecone_key=settings.PINECONE_API_KEY,
        pinecone_index=settings.PINECONE_INDEX
    )
    
    stats = orchestrator.get_model_usage_stats()
    
    return {
        'session_usage': stats.get('session_usage', {}),
        'model_distribution': stats.get('model_distribution', {}),
        'tier_distribution': stats.get('tier_distribution', {}),
        'estimated_costs': stats.get('estimated_monthly_cost', {}),
        'version': 'C5'
    }


@router.get("/ganesha/models/config")
async def get_model_configuration(
    current_user: User = Depends(get_current_active_user)
):
    """Get C5 model configuration for all agents"""
    
    from app.agents.c5_multimodel_strategy import AGENT_MODEL_MAP, MODELS
    
    config = []
    for agent_id, model_key in AGENT_MODEL_MAP.items():
        model_config = MODELS.get(model_key, {})
        config.append({
            'agent_id': agent_id,
            'model': model_key,
            'tier': model_config.tier.value if hasattr(model_config, 'tier') else 'unknown',
            'primary_model': model_config.primary if hasattr(model_config, 'primary') else model_key,
            'fallback': model_config.fallback if hasattr(model_config, 'fallback') else None
        })
    
    return {
        'agent_count': len(config),
        'configuration': config
    }


# =============================================================================
# QUICK ACTIONS
# =============================================================================
@router.post("/ganesha/quick-action")
async def quick_action_v2(
    request: QuickActionRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Handle quick action buttons"""
    
    action_messages = {
        'status': 'Show me the current system status and key metrics',
        'review': 'Review recent activities and highlight any issues',
        'next_steps': 'What should I focus on next? Prioritize by impact.',
        'agents': 'List all available AI agents and their specialties',
        'help': 'Show me available commands and features',
        'revenue': 'Give me a revenue summary for this month',
        'alerts': 'Show me active alerts that need attention'
    }
    
    message = action_messages.get(request.action)
    
    if not message:
        raise HTTPException(status_code=400, detail="Invalid action")
    
    return {
        'action': request.action,
        'message': message,
        'suggested_agent': route_to_agent(message, None)
    }


# =============================================================================
# CONVERSATION HISTORY
# =============================================================================
@router.get("/ganesha/history")
async def get_conversation_history_v2(
    limit: int = Query(20, le=100),
    product: Optional[str] = None,
    current_user: User = Depends(get_current_active_user)
):
    """Get user's conversation history with enhanced metadata"""
    
    db = get_db()
    
    query_filter = {'user_id': current_user.kailash_code}
    if product:
        query_filter['product_context'] = product
    
    commands = await db.ganesha_commands.find(
        query_filter,
        sort=[('created_at', -1)],
        limit=limit
    ).to_list(limit)
    
    for cmd in commands:
        cmd['_id'] = str(cmd['_id'])
    
    # Calculate stats
    total = len(commands)
    rag_used_count = sum(1 for c in commands if c.get('rag_used'))
    
    return {
        'commands': commands,
        'total': total,
        'rag_usage_rate': (rag_used_count / total * 100) if total > 0 else 0
    }


# =============================================================================
# USAGE STATISTICS
# =============================================================================
@router.get("/ganesha/stats")
async def get_orchestrator_stats_v2(
    current_user: User = Depends(get_current_active_user)
):
    """Get comprehensive usage statistics"""
    
    db = get_db()
    
    # Basic counts
    total_commands = await db.ganesha_commands.count_documents({
        'user_id': current_user.kailash_code
    })
    
    completed_commands = await db.ganesha_commands.count_documents({
        'user_id': current_user.kailash_code,
        'status': 'completed'
    })
    
    rag_used = await db.ganesha_commands.count_documents({
        'user_id': current_user.kailash_code,
        'rag_used': True
    })
    
    # Agent usage breakdown
    pipeline = [
        {'$match': {'user_id': current_user.kailash_code, 'agent_id': {'$exists': True}}},
        {'$group': {'_id': '$agent_id', 'count': {'$sum': 1}}},
        {'$sort': {'count': -1}},
        {'$limit': 10}
    ]
    
    agent_usage = await db.ganesha_commands.aggregate(pipeline).to_list(10)
    
    return {
        'total_commands': total_commands,
        'completed_commands': completed_commands,
        'success_rate': (completed_commands / total_commands * 100) if total_commands > 0 else 0,
        'rag_usage_rate': (rag_used / total_commands * 100) if total_commands > 0 else 0,
        'top_agents': agent_usage,
        'version': '2.0'
    }
