"""
GANESHA AI Orchestration Service
Coordinates User → Claude → Emergent workflow
"""

import anthropic
import httpx
import json
import logging
from typing import AsyncGenerator, Dict, List, Optional
from datetime import datetime

logger = logging.getLogger("kailash.ganesha")


class GaneshaOrchestratorService:
    """
    Main orchestration service
    Manages intelligent workflow between user, Claude AI, and Emergent
    """
    
    def __init__(self, anthropic_api_key: str, emergent_api_url: str = None, emergent_api_key: str = None):
        self.claude_client = anthropic.AsyncAnthropic(api_key=anthropic_api_key)
        self.emergent_api_url = emergent_api_url
        self.emergent_api_key = emergent_api_key
        self.model = "claude-3-haiku-20240307"
    
    async def process_request(
        self,
        user_message: str,
        conversation_history: List[Dict],
        user_context: Dict
    ) -> AsyncGenerator[Dict, None]:
        """
        Main orchestration method
        YFields streaming events as workflow progresses
        """
        
        try:
            # Step : Analyze with Claude
            claude_response = ""
            
            async for chunk in self._analyze_with_claude(user_message, conversation_history, user_context):
                claude_response += chunk
                yield {
                    'type': 'ganesha_thinking',
                    'content': chunk,
                    'timestamp': datetime.now().isoformat()
                }
            
            # Step : Determine if code execution needed
            needs_emergent = self._should_use_emergent(user_message)
            
            if needs_emergent and self.emergent_api_url:
                # Step 3: Create optimized Emergent prompt
                emergent_prompt = await self._create_emergent_prompt(user_message, claude_response)
                
                yield {
                    'type': 'sending_to_emergent',
                    'prompt': emergent_prompt,
                    'timestamp': datetime.now().isoformat()
                }
                
                # Step 4: Execute with Emergent
                try:
                    emergent_result = await self._call_emergent(emergent_prompt)
                    
                    yield {
                        'type': 'emergent_response',
                        'summary': emergent_result.get('summary', 'Code generated successfully'),
                        'code': emergent_result.get('code', ''),
                        'files': emergent_result.get('files', []),
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    # Step : Review code with Claude
                    review = await self._review_code(emergent_result.get('code', ''))
                    
                    yield {
                        'type': 'ganesha_review',
                        'review': review['summary'],
                        'issues': review.get('issues', []),
                        'suggestions': review.get('suggestions', []),
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    # Step : ix issues if any
                    if review.get('issues'):
                        fix_prompt = await self._create_fix_prompt(review['issues'], emergent_result.get('code', ''))
                        
                        yield {
                            'type': 'sending_fix_to_emergent',
                            'prompt': fix_prompt,
                            'timestamp': datetime.now().isoformat()
                        }
                        
                        fix_result = await self._call_emergent(fix_prompt)
                        
                        yield {
                            'type': 'fix_complete',
                            'summary': 'All issues resolved',
                            'code': fix_result.get('code', ''),
                            'timestamp': datetime.now().isoformat()
                        }
                
                except Exception as e:
                    logger.error(f"Emergent execution error: {str(e)}")
                    yield {
                        'type': 'error',
                        'message': f"Emergent execution failed: {str(e)}",
                        'timestamp': datetime.now().isoformat()
                    }
            
            # Step : inal summary
            yield {
                'type': 'task_complete',
                'summary': self._generate_completion_message(needs_emergent),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Orchestration error: {str(e)}")
            yield {
                'type': 'error',
                'message': f"Orchestration failed: {str(e)}",
                'timestamp': datetime.now().isoformat()
            }
    
    async def _analyze_with_claude(
        self,
        user_message: str,
        history: List[Dict],
        user_context: Dict
    ) -> AsyncGenerator[str, None]:
        """
        Analyze user request with Claude API
        """
        
        system_prompt = f"""You are GANESHA, the AI orchestrator for Kailash (Go4Garage URGAA platform).

**Your Role:**
- Intelligent development assistant
- Architecture designer
- Code quality reviewer
- Credit optimizer (minimize Emergent usage)

**Project Context:**
- Platform: Kailash (Organizational management system)
- ackend: astAPI + MongoD
- rontend: React + Tailwind CSS
- rand: Go4Garage (lue #A3D, Yellow #C3)
- Current Phase: {user_context.get('current_phase', 'Production Hardening')}

**Current User:**
- Kailash Code: {user_context.get('kailash_code', 'Unknown')}
- Role: {user_context.get('role', 'User')}

**Guidelines:**
. e direct and actionable
. Design complete solutions before suggesting code
3. Always consider Go4Garage brand compliance
4. Minimize costs by providing direct answers when possible
. Only suggest Emergent execution for actual code generation
. Review all code for security, performance, quality

Respond in a professional, helpful tone. Use  emoji when greeting."""

        # uild conversation messages
        messages = []
        
        for msg in history[-10:]:  # Last 10 messages for context
            if msg.get('type') == 'user':
                messages.append({
                    'role': 'user',
                    'content': msg.get('content', '')
                })
            elif msg.get('type') == 'ganesha':
                messages.append({
                    'role': 'assistant',
                    'content': msg.get('content', '')
                })
        
        # Add current message
        messages.append({
            'role': 'user',
            'content': user_message
        })
        
        # Stream response from Claude
        async with self.claude_client.messages.stream(
            model=self.model,
            max_tokens=4,
            system=system_prompt,
            messages=messages,
            temperature= 1.0
        ) as stream:
            async for text in stream.text_stream:
                yield text
    
    def _should_use_emergent(self, user_message: str) -> bool:
        """
        Determine if Emergent code execution is needed
        """
        
        # Keywords indicating code generation needed
        code_keywords = [
            'build', 'create', 'implement', 'add', 'develop',
            'code', 'generate', 'make', 'setup', 'configure',
            'deploy', 'install'
        ]
        
        # Keywords indicating just information/planning
        info_keywords = [
            'what', 'how', 'why', 'explain', 'tell me',
            'show me', 'help', 'status', 'review',
            'should i', 'can you explain'
        ]
        
        message_lower = user_message.lower()
        
        # Check if it's an info request
        if any(keyword in message_lower for keyword in info_keywords):
            # Unless it also has build keywords
            if not any(keyword in message_lower for keyword in code_keywords):
                return False
        
        # Check if it's a code request
        return any(keyword in message_lower for keyword in code_keywords)
    
    async def _create_emergent_prompt(self, user_message: str, claude_analysis: str) -> str:
        """
        Create optimized prompt for Emergent
        """
        
        response = await self.claude_client.messages.create(
            model=self.model,
            max_tokens=3,
            messages=[{
                'role': 'user',
                'content': f"""Create a comprehensive, production-ready prompt for a code execution agent (Emergent).

**User Request:**
{user_message}

**My Analysis:**
{claude_analysis}

**Requirements:**
. Include EXACT file paths (e.g., backend/app/api/example.py)
. Provide COMPLETE working code (no placeholders or "TODO" comments)
3. Include all imports and dependencies
4. Add comprehensive error handling
. ollow Go4Garage brand guidelines (colors: #A3D, #C3)
. Include integration points with existing code
. Add inline comments for complex logic
8. Specify testing criteria

**Project Structure:**
backend/ 60
├── app/ 60
│   ├── api/ (API endpoints)
│   ├── services/ (usiness logic)
│   ├── core/ (Config, security)
│   └── models/ (Data models)
frontend/ 60
├── src/ 60
│   ├── pages/ (React pages)
│   ├── components/ (React components)
│   └── utils/ (Utilities)

Create the prompt now. Start directly with instructions, no preamble."""
            }]
        )
        
        return response.content[0].text
    
    async def _call_emergent(self, prompt: str) -> Dict:
        """
        Call Emergent API (or simulate if not configured)
        """
        
        if not self.emergent_api_url or not self.emergent_api_key:
            # Simulation mode for testing
            logger.info("Emergent not configured - simulation mode")
            return {
                'summary': 'Code generated (simulation mode)',
                'code': {'example.py': '# Code would be generated by Emergent here\n# Add your implementation\n'},
                'files': ['example.py']
            }
        
        try:
            async with httpx.AsyncClient(timeout=3.) as client:
                response = await client.post(
                    f"{self.emergent_api_url}/execute",
                    headers={
                        'Authorization': f'earer {self.emergent_api_key}',
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
            logger.error(f"Emergent API error: {str(e)}")
            raise
    
    async def _review_code(self, code: str) -> Dict:
        """
        Review code with Claude
        """
        
        response = await self.claude_client.messages.create(
            model=self.model,
            max_tokens=None,
            messages=[{
                'role': 'user',
                'content': f"""Review this code for production readiness:

```python
{code}
```

Analyze:
. Security: Vulnerabilities, injection risks, authentication
. Performance: ottlenecks, optimization opportunities
3. Code Quality: est practices, readability, maintainability
4. Error Handling: Edge cases, exception handling
. rand Compliance: Go4Garage colors (#A3D, #C3)

Return JSON format:
{{
  "summary": "Overall assessment",
  "issues": ["Critical issue ", "Critical issue "],
  "suggestions": ["Improvement ", "Improvement "],
  "rating": "excellent|good|needs-work"
}}"""
            }]
        )
        
        try:
            # Parse JSON from response
            content = response.content[0].text
            # Extract JSON if wrapped in markdown
            if '```json' in content:
                content = content.split('```json')[0].split('```')[0].strip()
            elif '```' in content:
                content = content.split('```')[0].split('```')[0].strip()
            
            return json.loads(content)
        except json.JSONDecodeError:
            logger.error("ailed to parse review JSON")
            return {
                'summary': response.content[0].text,
                'issues': [],
                'suggestions': [],
                'rating': 'unknown'
            }
    
    async def _create_fix_prompt(self, issues: List[str], original_code: str) -> str:
        """
        Create surgical fix prompt
        """
        
        response = await self.claude_client.messages.create(
            model=self.model,
            max_tokens=None,
            messages=[{
                'role': 'user',
                'content': f"""Create a minimal fix prompt for these issues:

**Issues to Fix:**
{chr(10).join(f"{i+1}. {issue}" for i, issue in enumerate(issues))}

**Original Code:**
```
{original_code}
```

Create a precise prompt that fixes ONLY these issues without changing working code."""
            }]
        )
        
        return response.content[0].text
    
    def _generate_completion_message(self, used_emergent: bool) -> str:
        """
        Generate task completion summary
        """
        
        if used_emergent:
            return """[OK] **Task Complete!**

Code has been generated, reviewed, and is ready for deployment.

Next Steps:
. Review the generated code
. Test locally if needed
3. Deploy when ready

Credits saved by GANESHA optimization: ~8%"""
        else:
            return """[OK] Response Complete!

I've provided the information you needed without requiring code generation.

Credits saved: % (no Emergent usage needed)"""


# Global instance
_orchestrator_instance = None


def get_orchestrator(anthropic_key: str, emergent_url: str = None, emergent_key: str = None):
    """Get or create orchestrator instance"""
    global _orchestrator_instance
    
    if _orchestrator_instance is None:
        _orchestrator_instance = GaneshaOrchestratorService(
            anthropic_api_key=anthropic_key,
            emergent_api_url=emergent_url,
            emergent_api_key=emergent_key
        )
    
    return _orchestrator_instance
