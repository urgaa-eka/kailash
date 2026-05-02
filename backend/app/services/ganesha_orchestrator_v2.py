"""
GANESHA AI Orchestration Service v2.0
Enhanced with RAG Integration, C4 Agent Prompts, and C5 Multi-Model Strategy
Coordinates User → RAG → Model Selection → Specialist Agent workflow
"""

import anthropic
import httpx
import json
import logging
import os
from typing import AsyncGenerator, Dict, List, Optional
from datetime import datetime

from app.services.rag_service import get_rag_service
from app.agents.prompts import (
    get_agent_prompt,
    route_to_agent,
    GANESHA_SYSTEM_PROMPT,
    AGENT_NAMES
)
from app.agents.c5_multimodel_strategy import (
    get_model_for_agent,
    get_model_name,
    get_fallback_model,
    estimate_cost,
    classify_query_complexity,
    MODELS,
    LLMProvider
)

logger = logging.getLogger("kailash.ganesha.v2")


class GaneshaOrchestratorV2:
    """
    Enhanced GANESHA Orchestration Service
    Now with RAG knowledge retrieval, C4 specialist agent prompts,
    and C5 multi-model cost optimization
    """
    
    def __init__(
        self,
        anthropic_api_key: str,
        pinecone_api_key: str = None,
        pinecone_index: str = "kailashai",
        emergent_api_url: str = None,
        emergent_api_key: str = None,
        openai_api_key: str = None,
        google_api_key: str = None
    ):
        # Initialize Claude client (primary)
        self.claude_client = anthropic.AsyncAnthropic(api_key=anthropic_api_key)
        self.anthropic_api_key = anthropic_api_key
        
        # Store additional API keys for multi-model
        self.openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        self.google_api_key = google_api_key or os.getenv('GOOGLE_API_KEY')
        
        # C5 Multi-Model: Track model usage for cost monitoring
        self.model_usage = {}
        
        # Initialize RAG service
        self.rag_service = get_rag_service(
            pinecone_api_key=pinecone_api_key,
            pinecone_index=pinecone_index,
            anthropic_api_key=anthropic_api_key
        )
        
        # Emergent integration (optional)
        self.emergent_api_url = emergent_api_url
        self.emergent_api_key = emergent_api_key
    
    async def process_request(
        self,
        user_message: str,
        conversation_history: List[Dict],
        user_context: Dict
    ) -> AsyncGenerator[Dict, None]:
        """
        Main orchestration method with RAG integration
        
        Flow:
        1. Query RAG for relevant knowledge
        2. Route to appropriate specialist agent
        3. Execute agent with enhanced context
        4. Stream response back to user
        """
        
        try:
            # Step 1: Query RAG for relevant context
            yield {
                'type': 'thinking',
                'content': '🔍 Searching knowledge base...',
                'timestamp': datetime.now().isoformat()
            }
            
            rag_context = await self._query_rag(user_message, user_context)
            
            if rag_context:
                yield {
                    'type': 'rag_complete',
                    'content': f'📚 Found {len(rag_context.get("matches", []))} relevant sources',
                    'sources': rag_context.get('sources', []),
                    'timestamp': datetime.now().isoformat()
                }
            
            # Step 2: Route to appropriate agent
            product_context = user_context.get('product', None)
            agent_id = route_to_agent(user_message, product_context)
            agent_config = get_agent_prompt(agent_id)
            
            if agent_config:
                agent_name = agent_config.get('name', 'GANESHA')
                yield {
                    'type': 'routing',
                    'agent_id': agent_id,
                    'agent_name': agent_name,
                    'specialty': agent_config.get('specialty', ''),
                    'content': f'🎯 Routing to {agent_name}...',
                    'timestamp': datetime.now().isoformat()
                }
            else:
                agent_id = "GANESHA"
                agent_name = "GANESHA"
            
            # Step 3: Execute agent with full context
            agent_response = ""
            async for chunk in self._execute_agent(
                agent_id=agent_id,
                user_message=user_message,
                conversation_history=conversation_history,
                user_context=user_context,
                rag_context=rag_context
            ):
                agent_response += chunk
                yield {
                    'type': 'agent_response',
                    'agent_id': agent_id,
                    'agent_name': agent_name,
                    'content': chunk,
                    'timestamp': datetime.now().isoformat()
                }
            
            # Step 4: Check if code generation needed
            needs_emergent = self._should_use_emergent(user_message)
            
            if needs_emergent and self.emergent_api_url:
                yield {
                    'type': 'code_generation',
                    'content': '⚙️ Generating code with Emergent...',
                    'timestamp': datetime.now().isoformat()
                }
                
                # Create optimized prompt for Emergent
                emergent_prompt = await self._create_emergent_prompt(
                    user_message, 
                    agent_response
                )
                
                try:
                    emergent_result = await self._call_emergent(emergent_prompt)
                    
                    yield {
                        'type': 'emergent_complete',
                        'summary': emergent_result.get('summary', 'Code generated'),
                        'files': emergent_result.get('files', []),
                        'timestamp': datetime.now().isoformat()
                    }
                except Exception as e:
                    logger.error(f"Emergent error: {e}")
                    yield {
                        'type': 'emergent_error',
                        'content': f'Code generation skipped: {str(e)}',
                        'timestamp': datetime.now().isoformat()
                    }
            
            # Step 5: Final summary
            yield {
                'type': 'complete',
                'agent_id': agent_id,
                'agent_name': agent_name,
                'rag_used': bool(rag_context and rag_context.get('context')),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Orchestration error: {e}")
            yield {
                'type': 'error',
                'content': f'Error: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }
    
    async def _query_rag(
        self,
        query: str,
        user_context: Dict
    ) -> Optional[Dict]:
        """Query RAG for relevant knowledge"""
        try:
            # Determine product filter from context
            product = user_context.get('product', None)
            
            # Query RAG
            result = await self.rag_service.query(
                query_text=query,
                product_filter=product,
                top_k=5,
                min_score=0.3
            )
            
            return result if result and result.get('context') else None
            
        except Exception as e:
            logger.warning(f"RAG query failed: {e}")
            return None
    
    async def _execute_agent(
        self,
        agent_id: str,
        user_message: str,
        conversation_history: List[Dict],
        user_context: Dict,
        rag_context: Optional[Dict]
    ) -> AsyncGenerator[str, None]:
        """Execute a specialist agent with C5 multi-model selection"""
        
        # Get agent prompt
        agent_config = get_agent_prompt(agent_id)
        
        if agent_config:
            system_prompt = agent_config.get('prompt', GANESHA_SYSTEM_PROMPT)
        else:
            system_prompt = GANESHA_SYSTEM_PROMPT
        
        # Build context-enhanced prompt
        enhanced_prompt = self._build_enhanced_prompt(
            base_prompt=system_prompt,
            user_context=user_context,
            rag_context=rag_context
        )
        
        # Build conversation messages
        messages = self._build_messages(
            conversation_history=conversation_history,
            user_message=user_message
        )
        
        # C5 Multi-Model Selection
        model_config = get_model_for_agent(agent_id, user_message)
        selected_model = model_config.primary
        complexity = classify_query_complexity(user_message)
        
        logger.info(f"C5 Model Selection: Agent={agent_id}, Model={selected_model}, Complexity={complexity}")
        
        # Track model usage
        if selected_model not in self.model_usage:
            self.model_usage[selected_model] = 0
        self.model_usage[selected_model] += 1
        
        # Stream response from selected model
        try:
            # Currently supporting Claude models primarily
            # GPT and Gemini integration can be added here
            if 'claude' in selected_model.lower():
                async with self.claude_client.messages.stream(
                    model=selected_model,
                    max_tokens=model_config.max_tokens,
                    system=enhanced_prompt,
                    messages=messages,
                    temperature=model_config.temperature
                ) as stream:
                    async for text in stream.text_stream:
                        yield text
            else:
                # Fallback to Claude for non-Claude models (for now)
                # TODO: Add OpenAI and Google API integrations
                fallback_model = get_fallback_model(agent_id)
                logger.info(f"Using fallback model: {fallback_model}")
                
                async with self.claude_client.messages.stream(
                    model=fallback_model if 'claude' in fallback_model else "claude-3-5-haiku-20241022",
                    max_tokens=model_config.max_tokens,
                    system=enhanced_prompt,
                    messages=messages,
                    temperature=model_config.temperature
                ) as stream:
                    async for text in stream.text_stream:
                        yield text
                    
        except Exception as e:
            logger.error(f"Model execution error ({selected_model}): {e}")
            # Try fallback
            try:
                fallback = model_config.fallback
                logger.info(f"Attempting fallback to: {fallback}")
                
                if 'claude' in fallback.lower():
                    async with self.claude_client.messages.stream(
                        model=fallback,
                        max_tokens=2048,
                        system=enhanced_prompt,
                        messages=messages,
                        temperature=0.7
                    ) as stream:
                        async for text in stream.text_stream:
                            yield text
                else:
                    yield f"I apologize, but I encountered an error. Please try again."
            except Exception as fallback_error:
                logger.error(f"Fallback also failed: {fallback_error}")
                yield f"I apologize, but I encountered an error processing your request. Please try again."
    
    def _build_enhanced_prompt(
        self,
        base_prompt: str,
        user_context: Dict,
        rag_context: Optional[Dict]
    ) -> str:
        """Build enhanced system prompt with RAG context"""
        
        enhanced = base_prompt
        
        # Add user context
        enhanced += f"""

---
## CURRENT SESSION CONTEXT

**User:** {user_context.get('user_name', 'User')}
**Role:** {user_context.get('role', 'User')}
**Organization:** {user_context.get('organization', 'Go4Garage')}
**Product:** {user_context.get('product', 'URGAA')}
**Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        # Add RAG context if available
        if rag_context and rag_context.get('context'):
            enhanced += f"""

---
## RELEVANT KNOWLEDGE FROM DATABASE

{rag_context['context']}

**Sources:** {', '.join(rag_context.get('sources', ['Internal KB']))}

---
Use this knowledge to provide accurate, contextual responses.
"""
        
        return enhanced
    
    def _build_messages(
        self,
        conversation_history: List[Dict],
        user_message: str
    ) -> List[Dict]:
        """Build message history for Claude"""
        
        messages = []
        
        # Add recent history (last 10 turns)
        for msg in conversation_history[-10:]:
            if msg.get('type') == 'user':
                messages.append({
                    'role': 'user',
                    'content': msg.get('content', '')
                })
            elif msg.get('type') in ['ganesha', 'assistant', 'agent']:
                messages.append({
                    'role': 'assistant',
                    'content': msg.get('content', '')
                })
        
        # Add current message
        messages.append({
            'role': 'user',
            'content': user_message
        })
        
        return messages
    
    def _should_use_emergent(self, user_message: str) -> bool:
        """Determine if Emergent code execution is needed"""
        
        code_keywords = [
            'build', 'create', 'implement', 'add feature',
            'develop', 'code', 'generate code', 'make',
            'setup', 'configure', 'deploy', 'install'
        ]
        
        info_keywords = [
            'what', 'how', 'why', 'explain', 'tell me',
            'show me', 'help', 'status', 'review',
            'should i', 'can you explain', 'describe'
        ]
        
        message_lower = user_message.lower()
        
        # If it's an info request, don't use Emergent
        if any(kw in message_lower for kw in info_keywords):
            if not any(kw in message_lower for kw in code_keywords):
                return False
        
        return any(kw in message_lower for kw in code_keywords)
    
    async def _create_emergent_prompt(
        self,
        user_message: str,
        agent_analysis: str
    ) -> str:
        """Create optimized prompt for Emergent"""
        
        response = await self.claude_client.messages.create(
            model=self.model,
            max_tokens=2000,
            messages=[{
                'role': 'user',
                'content': f"""Create a comprehensive code generation prompt:

**User Request:** {user_message}

**Analysis:** {agent_analysis}

**Requirements:**
1. Include exact file paths
2. Provide complete, working code
3. Include all imports
4. Add error handling
5. Follow Go4Garage brand guidelines
6. Include integration points

Create the prompt now."""
            }]
        )
        
        return response.content[0].text
    
    async def _call_emergent(self, prompt: str) -> Dict:
        """Call Emergent API"""
        
        if not self.emergent_api_url or not self.emergent_api_key:
            return {
                'summary': 'Code generation simulated (Emergent not configured)',
                'files': []
            }
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.emergent_api_url}/execute",
                    headers={
                        'Authorization': f'Bearer {self.emergent_api_key}',
                        'Content-Type': 'application/json'
                    },
                    json={
                        'prompt': prompt,
                        'project': 'KAILASH-hub'
                    }
                )
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            logger.error(f"Emergent API error: {e}")
            raise
    
    async def query_specialist(
        self,
        agent_id: str,
        query: str,
        user_context: Dict
    ) -> str:
        """Directly query a specialist agent"""
        
        # Get RAG context
        rag_context = await self._query_rag(query, user_context)
        
        # Execute agent
        response_parts = []
        async for chunk in self._execute_agent(
            agent_id=agent_id,
            user_message=query,
            conversation_history=[],
            user_context=user_context,
            rag_context=rag_context
        ):
            response_parts.append(chunk)
        
        return ''.join(response_parts)
    
    def get_available_agents(self) -> List[Dict]:
        """Get list of available agents"""
        from app.agents.prompts import list_all_agents
        return list_all_agents()
    
    def get_rag_stats(self) -> Dict:
        """Get RAG knowledge base statistics"""
        return self.rag_service.get_stats()
    
    def get_model_usage_stats(self) -> Dict:
        """Get C5 multi-model usage statistics"""
        from app.agents.c5_multimodel_strategy import (
            get_model_distribution,
            get_tier_distribution,
            estimate_monthly_cost
        )
        
        return {
            "session_usage": self.model_usage,
            "model_distribution": get_model_distribution(),
            "tier_distribution": get_tier_distribution(),
            "estimated_monthly_cost": estimate_monthly_cost()
        }


# =============================================================================
# SINGLETON INSTANCE
# =============================================================================
_orchestrator_v2_instance = None


def get_orchestrator_v2(
    anthropic_key: str,
    pinecone_key: str = None,
    pinecone_index: str = "kailashai",
    emergent_url: str = None,
    emergent_key: str = None
) -> GaneshaOrchestratorV2:
    """Get or create orchestrator v2 instance"""
    global _orchestrator_v2_instance
    
    if _orchestrator_v2_instance is None:
        _orchestrator_v2_instance = GaneshaOrchestratorV2(
            anthropic_api_key=anthropic_key,
            pinecone_api_key=pinecone_key,
            pinecone_index=pinecone_index,
            emergent_api_url=emergent_url,
            emergent_api_key=emergent_key
        )
    
    return _orchestrator_v2_instance
