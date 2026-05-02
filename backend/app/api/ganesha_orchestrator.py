"""
GANESHA Orchestrator API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
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
from app.services.ganesha_orchestrator_service import get_orchestrator
from app.core.config import get_settings
from app.models.user import User

router = APIRouter()
logger = logging.getLogger("kailash.ganesha.api")
settings = get_settings()


class OrchestrateRequest(BaseModel):
    user_message: str
    conversation_history: Optional[List[Dict]] = []


class QuickActionRequest(BaseModel):
    action: str  # 'status', 'review', 'next_steps'


@router.post("/ganesha/orchestrate")
async def orchestrate_request(
    request: OrchestrateRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Main orchestration endpoint
    Streams GANESHA's workflow in real-time
    """
    
    # Get database connection
    db = get_db()
    
    # Get orchestrator instance
    orchestrator = get_orchestrator(
        anthropic_key=settings.anthropic_api_key,
        emergent_url=getattr(settings, 'emergent_api_url', None),
        emergent_key=getattr(settings, 'emergent_api_key', None)
    )
    
    # Prepare user context
    user_context = {
        'kailash_code': current_user.kailash_code,
        'role': 'Admin' if current_user.is_admin else 'User',
        'current_phase': 'Phase 3: Production Hardening'  # Get from D
    }
    
    # Store command in database
    command_doc = {
        'user_id': current_user.kailash_code,
        'message': request.user_message,
        'created_at': datetime.now(),
        'status': 'processing'
    }
    
    result = await db.ganesha_commands.insert_one(command_doc)
    command_id = str(result.inserted_id)
    
    async def generate_stream():
        """Generate SSE stream"""
        
        try:
            async for event in orchestrator.process_request(
                user_message=request.user_message,
                conversation_history=request.conversation_history,
                user_context=user_context
            ):
                # Send event to client
                yield f"data: {json.dumps(event)}\n\n"
                
                # Small delay to prevent overwhelming
                await asyncio.sleep(0.05)
            
            # Update command status in database
            await db.ganesha_commands.update_one(
                {'_id': ObjectId(command_id)},
                {
                    '$set': {
                        'status': 'completed',
                        'completed_at': datetime.now()
                    }
                }
            )
            
        except Exception as e:
            logger.error(f"Stream error: {str(e)}")
            
            error_event = {
                'type': 'error',
                'message': f"Stream error: {str(e)}",
                'timestamp': datetime.now().isoformat()
            }
            
            yield f"data: {json.dumps(error_event)}\n\n"
            
            # Update command status
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
            'X-Accel-uffering': 'no'  # Disable nginx buffering
        }
    )


@router.post("/ganesha/quick-action")
async def quick_action(
    request: QuickActionRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Handle quick action buttons
    """
    
    action_messages = {
        'status': 'Show me the current project status and progress on all phases',
        'review': 'Review the code quality of our current implementation',
        'next_steps': 'What should I work on next? Prioritize by impact and effort.',
        'help': 'Show me what commands and features are available'
    }
    
    message = action_messages.get(request.action)
    
    if not message:
        raise HTTPException(status_code=400, detail="Invalid action")
    
    # Return message for frontend to process
    return {
        'action': request.action,
        'message': message
    }


@router.get("/ganesha/history")
async def get_conversation_history(
    limit: int = 10,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get user's conversation history with GANESHA
    """
    
    db = get_db()
    commands = await db.ganesha_commands.find(
        {'user_id': current_user.kailash_code},
        sort=[('created_at', -1)],
        limit=limit
    ).to_list(limit)
    
    for cmd in commands:
        cmd['_id'] = str(cmd['_id'])
    
    return {
        'commands': commands,
        'total': len(commands)
    }


@router.get("/ganesha/stats")
async def get_orchestrator_stats(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get usage statistics
    """
    
    db = get_db()
    total_commands = await db.ganesha_commands.count_documents({
        'user_id': current_user.kailash_code
    })
    
    completed_commands = await db.ganesha_commands.count_documents({
        'user_id': current_user.kailash_code,
        'status': 'completed'
    })
    
    # Estimated credit savings (assuming 8% efficiency)
    traditional_credits = total_commands * 10   # Average without GANESHA
    with_ganesha_credits = total_commands * 10   # Average with GANESHA
    credits_saved = traditional_credits - with_ganesha_credits
    
    return {
        'total_commands': total_commands,
        'completed_commands': completed_commands,
        'success_rate': (completed_commands / total_commands * 100) if total_commands > 0 else 0,
        'estimated_credits_saved': credits_saved,
        'efficiency_percentage': 8
    }
