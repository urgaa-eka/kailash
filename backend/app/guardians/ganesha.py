from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from app.guardians import BaseGuardian
from app.core.mongodb import MongoD
import json
import os
from dotenv import load_dotenv
from emergentintegrations.llm.chat import LlmChat, UserMessage

# Load environment variables - DO NOT override Kubernetes-injected env vars
load_dotenv(override=False)

class GaneshaGuardian(BaseGuardian):
    """
    GANESHA - The AI Orchestrator & Command Center
    
    Responsibilities:
    - Natural language command processing
    - Intent classification
    - Department routing
    - Conversation management
    - Central AI coordination
    """
    
    def __init__(self):
        super().__init__(
            name="GANESHA",
            domain="orchestration"
        )
        self.active_conversations: Dict[str, Any] = {}
        self.request_count = 0
        self.department_routes: Dict[str, int] = {}
        
        # Initialize Emergent LLM for intent classification
        self.llm_api_key = os.getenv("EMERGENT_LLM_KEY", "")
        self.intent_classifier = None
        if self.llm_api_key:
            self.intent_classifier = LlmChat(
                api_key=self.llm_api_key,
                session_id="ganesha-intent-classifier",
                system_message="""You are an intent classifier for Kailash's department routing system.
                
Analyze user messages and determine which department should handle them. Respond ONLY with valid JSON.

Available departments:
- VISHWAKARMA: Technology, development, infrastructure, coding
- LAKSHMI: Finance, accounting, budgets, payments, invoices
- SURYA: Energy management, URJAA EV charging, solar, sustainability
- SARASWATI: Knowledge management, documentation, training, research
- VAYU: Communications, messaging, notifications, broadcasts
- KUBERA: Treasury, investments, financial planning, assets
- INDRA: Leadership, executive decisions, strategic planning
- YAMA: Compliance, regulations, policies, audits, legal
- VARUNA: Data management, analytics, databases, data science
- AGNI: Crisis management, incidents, emergency response
- CHANDRA: Customer service, support, user experience
- BRIHASPATI: Advisory, consulting, recommendations
- VISHNU: Quality assurance, testing, standards, monitoring
- BRAHMA: Architecture, system design, planning
- KARTIKEYA: Operations, workflows, processes, execution
- DURGA: Security, protection, access control, threats
- HANUMAN: Execution, task management, implementation
- NARADA: Internal communications, collaboration, team updates
- ASHWINI: Health monitoring, diagnostics, system health
- DHARMA: Governance, ethics, principles, guidelines

Response format (JSON only):
{"department": "DEPARTMENT_NAME", "sub_task": "specific task", "confidence": 0.95}"""
            ).with_model("openai", "gpt-4o-mini")

    async def monitor(self) -> Dict[str, Any]:
        """Monitor AI operations and conversation health"""
        db = MongoD.get_database()
        
        # Get active conversation count
        active_count = await db.conversations.count_documents({
            "updated_at": {"$gte": datetime.utcnow() - timedelta(hours=1)}
        })
        
        # Get department routing stats
        routing_stats = await self._get_routing_stats()
        
        self.metrics = {
            "active_conversations": active_count,
            "total_requests": self.request_count,
            "routing_stats": routing_stats,
            "status": "operational"
        }
        
        return self.metrics

    async def _get_routing_stats(self) -> Dict[str, int]:
        """Get department routing statistics"""
        db = MongoD.get_database()
        pipeline = [
            {"$group": {"_id": "$department", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        results = await db.ganesha_commands.aggregate(pipeline).to_list(10)
        return {r["_id"]: r["count"] for r in results if r["_id"]}

    async def classify_intent(self, message: str) -> Dict[str, Any]:
        """Classify user intent using Emergent LLM to route to correct department"""
        if not self.intent_classifier:
            # Fallback to simple keyword matching if LLM not available
            return await self._fallback_classification(message)
        
        try:
            # Use Emergent LLM for classification
            user_message = UserMessage(text=f"Classify this user message: {message}")
            response = await self.intent_classifier.send_message(user_message)
            
            # Parse JSON response
            try:
                result = json.loads(response)
                if "department" in result:
                    # Track routing stats
                    dept = result["department"]
                    self.department_routes[dept] = self.department_routes.get(dept, 0) + 1
                    return result
            except json.JSONDecodeError:
                # If response is not valid JSON, try to extract department from text
                response_lower = response.lower()
                for dept in ["vishwakarma", "lakshmi", "surya", "saraswati", "vayu", 
                           "kubera", "indra", "yama", "varuna", "agni", "chandra",
                           "brihaspati", "vishnu", "brahma", "kartikeya", "durga",
                           "hanuman", "narada", "ashwini", "dharma"]:
                    if dept in response_lower:
                        return {
                            "department": dept.upper(),
                            "sub_task": "process request",
                            "confidence": 0.7
                        }
            
            # If no department found, use fallback
            return await self._fallback_classification(message)
            
        except Exception as e:
            print(f"LLM classification error: {str(e)}")
            return await self._fallback_classification(message)
    
    async def _fallback_classification(self, message: str) -> Dict[str, Any]:
        """Fallback keyword-based classification when LLM is unavailable"""
        message_lower = message.lower()
        
        # Simple keyword matching
        keywords = {
            "VISHWAKARMA": ["code", "develop", "tech", "software", "api", "infrastructure"],
            "LAKSHMI": ["finance", "money", "budget", "payment", "invoice", "cost"],
            "SURYA": ["energy", "charging", "ev", "solar", "urjaa", "power"],
            "SARASWATI": ["learn", "knowledge", "document", "train", "research"],
            "VAYU": ["message", "communicate", "notify", "broadcast", "send"],
            "KUBERA": ["investment", "treasury", "asset", "fund", "capital"],
            "INDRA": ["leader", "executive", "strategy", "decision", "plan"],
            "YAMA": ["compliance", "policy", "regulation", "legal", "audit"],
            "VARUNA": ["data", "analytics", "database", "report", "insight"],
            "AGNI": ["crisis", "emergency", "incident", "urgent", "critical"],
            "CHANDRA": ["customer", "support", "user", "help", "service"],
            "BRIHASPATI": ["advise", "consult", "recommend", "suggest"],
            "VISHNU": ["quality", "test", "standard", "monitor", "check"],
            "BRAHMA": ["architect", "design", "structure", "blueprint"],
            "KARTIKEYA": ["operation", "execute", "workflow", "process"],
            "DURGA": ["security", "protect", "access", "threat", "safe"],
            "HANUMAN": ["task", "implement", "execute", "deliver", "complete"],
            "NARADA": ["team", "collaborate", "internal", "colleague"],
            "ASHWINI": ["health", "monitor", "diagnostic", "system"],
            "DHARMA": ["govern", "ethics", "principle", "guideline", "rule"]
        }
        
        for dept, words in keywords.items():
            if any(word in message_lower for word in words):
                return {
                    "department": dept,
                    "sub_task": "process request",
                    "confidence": 0.6
                }
        
        # Default to GANESHA handling if no match
        return {
            "department": "GANESHA",
            "sub_task": "general inquiry",
            "confidence": 0.5
        }

    async def process_command(
        self,
        user_id: str,
        message: str,
        conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Main command processing pipeline"""
        self.request_count += 1
        
        # Create or get conversation
        if not conversation_id:
            conversation_id = await self._create_conversation(user_id)
        
        # Store user message
        await self._store_message(conversation_id, "user", message)
        
        # Classify intent and determine department
        classification = await self.classify_intent(message)
        department_name = classification.get("department")
        confidence = classification.get("confidence", 0)
        
        # Generate response
        response = await self._general_response(message, conversation_id)
        
        # Store assistant message
        content = response.get("content", "")
        await self._store_message(conversation_id, "assistant", content)
        
        # Log command
        await self._log_command(user_id, message, department_name, classification)
        
        return {
            "conversation_id": conversation_id,
            "department": department_name,
            "confidence": confidence,
            "response": response,
            "timestamp": datetime.utcnow().isoformat()
        }

    async def _create_conversation(self, user_id: str) -> str:
        """Create new conversation"""
        db = MongoD.get_database()
        result = await db.conversations.insert_one({
            "user_id": user_id,
            "messages": [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        })
        return str(result.inserted_id)

    async def _store_message(self, conversation_id: str, role: str, content: str):
        """Store message in conversation"""
        from bson import ObjectId
        db = MongoD.get_database()
        await db.conversations.update_one(
            {"_id": ObjectId(conversation_id)},
            {
                "$push": {
                    "messages": {
                        "role": role,
                        "content": content,
                        "timestamp": datetime.utcnow()
                    }
                },
                "$set": {"updated_at": datetime.utcnow()}
            }
        )

    async def _general_response(self, message: str, conversation_id: str) -> Dict[str, Any]:
        """Generate general response"""
        return {"content": f"Received: {message[:50]}...", "department": "GANESHA"}

    async def _log_command(self, user_id: str, message: str, department: Optional[str], classification: Dict):
        """Log command for analytics"""
        db = MongoD.get_database()
        await db.ganesha_commands.insert_one({
            "user_id": user_id,
            "message": message[:500],
            "department": department,
            "classification": classification,
            "timestamp": datetime.utcnow()
        })

    async def intervene(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle intervention requests"""
        event_type = event.get("type")
        
        if event_type == "reroute":
            return {"action": "rerouted", "details": event}
        elif event_type == "priority":
            return {"action": "prioritized", "details": event}
        
        return {"action": "acknowledged", "event": event}

    async def report(self) -> Dict[str, Any]:
        """Generate GANESHA status report"""
        await self.monitor()
        
        return {
            "guardian": "GANESHA",
            "description": "AI Orchestrator",
            "status": self.status,
            "metrics": self.metrics,
            "last_heartbeat": self.last_heartbeat.isoformat()
        }

# Singleton instance
ganesha = GaneshaGuardian()
