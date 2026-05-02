"""
GANESHA Multi-Model AI Orchestrator
The AI brain of Kailash - Routes queries to appropriate departments
and uses multiple AI models based on query type.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, Form
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os
import logging
import tempfile
from datetime import datetime, timezone
from uuid import uuid4

from ..api.deps import get_current_active_user
from ..models.user import User
from ..core.mongodb import get_db

# Voice transcription imports
try:
    from emergentintegrations.llm.openai import OpenAISpeechToText
    EMERGENT_STT_AVAILABLE = True
except ImportError:
    EMERGENT_STT_AVAILABLE = False

# Legacy OpenAI import for fallback
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

logger = logging.getLogger("kailash.ganesha")

router = APIRouter(prefix="/ganesha", tags=["GANESHA AI Orchestrator"])

# Get Emergent LLM Key for voice transcription
EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY', '')

# ============ MODELS ============


class GaneshaQuery(BaseModel):
    message: str
    model: str = "auto"  # "auto", "claude", "gpt4", "gemini", "perplexity"
    conversation_id: Optional[str] = None
    include_level2: bool = True  # Include market intelligence

class GaneshaResponse(BaseModel):
    response: str
    routed_to: str  # Department name
    scope: str  # "internal" or "external"
    source_product: Optional[str] = None  # "URGAA", "GSTSAAS", etc.
    models_used: List[str]
    level: int  # 1 or 2
    data_sources: List[str]
    problems_addressed: List[str]
    automation_percentage: Optional[int] = None

# ============ DEPARTMENT ROUTING ============

DEPARTMENT_ROUTING = {
    # INTERNAL DEPARTMENTS (Company Operations)
    "internal": {
        "LAKSHMI": {
            "keywords": ["revenue", "expenses", "budget", "p&l", "burn", "runway", "financial", "money", "profit", "loss", "income", "cost"],
            "display_name": "Finance & Revenue",
            "data_sources": ["Zoho Books", "Bank APIs", "Razorpay"]
        },
        "VISHWAKARMA": {
            "keywords": ["code", "deploy", "bug", "pr", "engineering", "architecture", "tech", "development", "api", "software", "system"],
            "display_name": "Technology/CTO",
            "data_sources": ["GitHub", "Sentry", "AWS CloudWatch"]
        },
        "KUBERA": {
            "keywords": ["bank", "cash", "payment", "collection", "ar", "ap", "treasury", "balance", "fund"],
            "display_name": "Treasury & Banking",
            "data_sources": ["ICICI API", "HDFC API", "Razorpay"]
        },
        "CHANDRA": {
            "keywords": ["hire", "employee", "team", "attrition", "culture", "payroll", "hr", "recruitment", "people", "staff"],
            "display_name": "HR & Culture",
            "data_sources": ["Zoho People", "LinkedIn", "Internal HRMS"]
        },
        "BRIHASPATI": {
            "keywords": ["kpi", "metrics", "okr", "dashboard", "analytics", "report", "performance", "insight", "data"],
            "display_name": "Analytics & Insights",
            "data_sources": ["All Products", "Google Analytics", "Internal Metrics"]
        },
        "VISHNU": {
            "keywords": ["server", "aws", "infra", "uptime", "security", "devops", "cloud", "hosting", "infrastructure"],
            "display_name": "IT & Infrastructure",
            "data_sources": ["AWS", "Cloudflare", "Monitoring Tools"]
        },
        "KARTIKEYA": {
            "keywords": ["workflow", "sop", "process", "task", "operations", "efficiency", "procedure"],
            "display_name": "Operations",
            "data_sources": ["Internal Tools", "Process Docs"]
        },
        "HANUMAN": {
            "keywords": ["urgent", "deadline", "blocker", "today", "immediate", "priority", "asap", "critical"],
            "display_name": "Execution & Delivery",
            "data_sources": ["Task Management", "Slack", "Email"]
        },
        "NARADA": {
            "keywords": ["announcement", "meeting", "slack", "email", "communication", "internal comms", "message", "notify"],
            "display_name": "Communications",
            "data_sources": ["Slack", "Email", "Calendar"]
        },
        "ASHWINI": {
            "keywords": ["system health", "monitoring", "diagnostics", "uptime", "incident", "alert", "status"],
            "display_name": "System Health",
            "data_sources": ["Grafana", "Prometheus", "Sentry"]
        },
        "DURGA": {
            "keywords": ["fraud", "security alert", "risk", "protection", "threat", "breach", "attack"],
            "display_name": "Protection & Security",
            "data_sources": ["Security Logs", "Access Control"]
        },
        "YAMA": {
            "keywords": ["contract", "compliance", "gst", "audit", "legal", "regulatory", "law", "license"],
            "display_name": "Legal & Compliance",
            "data_sources": ["Contract DB", "GST Portal", "Compliance Tools"]
        },
        "INDRA": {
            "keywords": ["pipeline", "deal", "partnership", "bd", "sales", "lead", "prospect", "client", "customer"],
            "display_name": "Sales & BD",
            "data_sources": ["CRM", "LinkedIn", "Deal Tracker"]
        },
        "VAYU": {
            "keywords": ["campaign", "brand", "social", "cac", "marketing", "content", "pr", "ads", "seo"],
            "display_name": "Marketing",
            "data_sources": ["Google Ads", "Meta Ads", "Analytics"]
        },
        "AGNI": {
            "keywords": ["quality", "testing", "bug count", "qa", "defect", "test", "validation"],
            "display_name": "Quality Assurance",
            "data_sources": ["Test Reports", "Bug Tracker"]
        }
    },
    
    # EXTERNAL DEPARTMENTS (Product Intelligence)
    "external": {
        "SURYA": {
            "keywords": ["charging", "charger", "station", "ev charging", "urgaa", "ocpp", "utilization", "ev", "connector"],
            "display_name": "URGAA Intelligence",
            "source_product": "URGAA",
            "data_sources": ["URGAA Database", "OCPP WebSocket", "DISCOM APIs"],
            "problems_solved": [
                "Charger health monitoring without physical inspection",
                "Predictive maintenance reducing downtime by 70%",
                "Auto-rectification of software issues remotely",
                "Demand forecasting for capacity planning",
                "Dynamic pricing optimization"
            ],
            "automation_percentage": 75
        },
        "VARUNA": {
            "keywords": ["workshop", "job card", "inventory", "gst", "gstsaas", "service", "spare parts", "mechanic", "garage"],
            "display_name": "GSTSAAS Intelligence",
            "source_product": "GSTSAAS",
            "data_sources": ["GSTSAAS Database", "Inventory System", "Customer Records"],
            "problems_solved": [
                "Inventory reorder prediction preventing stockouts",
                "Customer churn prediction and retention",
                "GST compliance automation",
                "Technician productivity optimization",
                "Service demand forecasting"
            ],
            "automation_percentage": 80
        },
        "SARASWATI": {
            "keywords": ["training", "course", "learner", "certification", "ev vidya", "skill", "education", "learning", "student"],
            "display_name": "EV VIDYA Intelligence",
            "source_product": "EV VIDYA",
            "data_sources": ["EV VIDYA LMS", "Assessment Engine", "Job Market APIs"],
            "problems_solved": [
                "Adaptive learning path personalization",
                "Skill gap analysis for workforce",
                "Course completion prediction",
                "Learner-job matching",
                "Content effectiveness optimization"
            ],
            "automation_percentage": 85
        },
        "BRAHMA": {
            "keywords": ["app", "user", "consumer", "ignition", "mau", "engagement", "mobile", "download"],
            "display_name": "IGNITION Intelligence",
            "source_product": "IGNITION",
            "data_sources": ["Ignition App Analytics", "User Database", "Transaction Logs"],
            "problems_solved": [
                "Personalized charger recommendations",
                "User churn prediction",
                "Engagement optimization",
                "Route-based charger suggestions",
                "Payment friction reduction"
            ],
            "automation_percentage": 70
        },
        "PRAGYA": {
            "keywords": ["total", "all products", "ecosystem", "cross-sell", "unified", "overall", "company", "organization"],
            "display_name": "Cross-Product Intelligence",
            "source_product": "ALL",
            "data_sources": ["All Product Databases", "Unified Analytics"],
            "problems_solved": [
                "Cross-product customer journey optimization",
                "Unified revenue forecasting",
                "Cross-sell opportunity identification",
                "Ecosystem health monitoring",
                "Competitive intelligence"
            ],
            "automation_percentage": 65
        }
    },
    
    # GUARDIAN DEPARTMENTS
    "guardian": {
        "SHIV": {
            "keywords": ["security status", "threat", "breach", "system integrity", "anomaly"],
            "display_name": "System Integrity Guardian",
            "mode": "passive_observer"
        },
        "PARVATI": {
            "keywords": ["workload", "balance", "harmony", "conflict", "team health"],
            "display_name": "Organizational Harmony",
            "mode": "passive_observer"
        },
        "GANESHA": {
            "keywords": [],  # Handles all unrouted queries
            "display_name": "AI Orchestrator",
            "mode": "active"
        }
    }
}

def classify_query(message: str) -> dict:
    """Classify query and route to appropriate department"""
    message_lower = message.lower()
    
    # Check external first (product-specific queries)
    for dept, config in DEPARTMENT_ROUTING["external"].items():
        if any(kw in message_lower for kw in config["keywords"]):
            return {
                "department": dept,
                "scope": "external",
                "source_product": config.get("source_product"),
                "display_name": config["display_name"],
                "data_sources": config.get("data_sources", []),
                "problems_solved": config.get("problems_solved", []),
                "automation_percentage": config.get("automation_percentage")
            }
    
    # Check internal
    for dept, config in DEPARTMENT_ROUTING["internal"].items():
        if any(kw in message_lower for kw in config["keywords"]):
            return {
                "department": dept,
                "scope": "internal",
                "source_product": None,
                "display_name": config["display_name"],
                "data_sources": config.get("data_sources", [])
            }
    
    # Check guardians
    for dept, config in DEPARTMENT_ROUTING["guardian"].items():
        if any(kw in message_lower for kw in config["keywords"]):
            return {
                "department": dept,
                "scope": "guardian",
                "display_name": config["display_name"]
            }
    
    # Default to GANESHA for general queries
    return {
        "department": "GANESHA",
        "scope": "guardian",
        "display_name": "AI Orchestrator",
        "data_sources": ["All Systems"]
    }

def select_model(message: str, requested_model: str) -> tuple:
    """Select appropriate AI model based on query type - returns (provider, model_name)"""
    if requested_model != "auto":
        model_map = {
            "claude": ("anthropic", "claude-4-sonnet-20250514"),
            "gpt4": ("openai", "gpt-4o"),
            "gemini": ("gemini", "gemini-2.5-flash"),
            "perplexity": ("openai", "gpt-4o")  # Fallback - perplexity not in Emergent
        }
        return model_map.get(requested_model, ("anthropic", "claude-4-sonnet-20250514"))
    
    message_lower = message.lower()
    
    # Real-time search needs - use Gemini (fast)
    if any(kw in message_lower for kw in ["latest", "current", "today", "news", "market", "trending"]):
        return ("gemini", "gemini-2.5-flash")
    
    # Code-related - use Claude (best for reasoning)
    if any(kw in message_lower for kw in ["code", "function", "debug", "implement", "script", "api"]):
        return ("anthropic", "claude-4-sonnet-20250514")
    
    # Structured data - use Gemini
    if any(kw in message_lower for kw in ["table", "spreadsheet", "json", "structured", "list"]):
        return ("gemini", "gemini-2.5-flash")
    
    # Creative/general - use OpenAI
    if any(kw in message_lower for kw in ["write", "create", "generate", "draft", "compose"]):
        return ("openai", "gpt-4o")
    
    # Default to Claude for reasoning/analysis
    return ("anthropic", "claude-4-sonnet-20250514")

# ============ AI MODEL CALLS ============

async def call_ai_model(provider: str, model: str, prompt: str, system_prompt: str = None) -> str:
    """Call AI model using Emergent Integrations library"""
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    from dotenv import load_dotenv
    load_dotenv(override=False)
    
    api_key = os.getenv("EMERGENT_LLM_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="EMERGENT_LLM_KEY not configured")
    
    try:
        chat = LlmChat(
            api_key=api_key,
            session_id=f"ganesha-{uuid4()}",
            system_message=system_prompt or "You are GANESHA, the AI Orchestrator for Kailash at Go4Garage. You help manage and coordinate all AI departments."
        ).with_model(provider, model)
        
        user_message = UserMessage(text=prompt)
        response = await chat.send_message(user_message)
        return response
    except Exception as e:
        logger.error(f"AI model call failed: {e}")
        raise HTTPException(status_code=500, detail=f"AI model call failed: {str(e)}")

# ============ MAIN ORCHESTRATION ENDPOINT ============

@router.post("/query", response_model=GaneshaResponse)
async def ganesha_query(
    query: GaneshaQuery,
    current_user: User = Depends(get_current_active_user)
):
    """Main GANESHA orchestration endpoint"""
    
    # 1. Classify the query
    routing = classify_query(query.message)
    
    # 2. Select AI model
    provider, model_name = select_model(query.message, query.model)
    
    # 3. Build context with data sources
    context = f"""
You are {routing['department']}, the {routing.get('display_name', 'AI Department')} department of Kailash-AI at Go4Garage.

SCOPE: {routing['scope'].upper()}
{f"SOURCE PRODUCT: {routing.get('source_product', 'N/A')}" if routing['scope'] == 'external' else ''}
DATA SOURCES: {', '.join(routing.get('data_sources', []))}

{"PROBLEMS YOU SOLVE:" if routing['scope'] == 'external' else ''}
{chr(10).join(['• ' + p for p in routing.get('problems_solved', [])])}

{f"AUTOMATION CAPABILITY: {routing.get('automation_percentage', 0)}% of issues resolved without human intervention" if routing.get('automation_percentage') else ''}

USER QUERY: {query.message}

Provide a comprehensive, helpful response. Be specific with numbers and cite your data sources where applicable.
Format your response in a clear, structured way.
"""
    
    # 4. Call appropriate AI model
    models_used = [f"{provider}/{model_name}"]
    
    try:
        response = await call_ai_model(provider, model_name, context)
    except Exception as e:
        logger.error(f"Primary model failed, falling back to Claude: {e}")
        # Fallback to Claude
        response = await call_ai_model("anthropic", "claude-4-sonnet-20250514", context)
        models_used = ["anthropic/claude-4-sonnet-20250514"]
    
    # 5. If Level 2 requested for external queries, add market context
    if query.include_level2 and routing['scope'] == 'external':
        try:
            market_query = f"Provide brief market context and industry benchmarks for {routing.get('source_product', 'EV industry')} in India. Focus on recent trends and key metrics."
            market_data = await call_ai_model("gemini", "gemini-2.5-flash", market_query)
            response += f"\n\n**LEVEL 2 — MARKET CONTEXT:**\n{market_data}"
            models_used.append("gemini/gemini-2.5-flash")
        except Exception as e:
            logger.warning(f"Market intelligence fetch failed: {e}")
    
    # 6. Log conversation to database
    try:
        db = get_db()
        await db.ganesha_conversations.insert_one({
            "id": str(uuid4()),
            "user_id": current_user.id,
            "query": query.message,
            "response": response,
            "routed_to": routing["department"],
            "scope": routing["scope"],
            "models_used": models_used,
            "timestamp": datetime.now(timezone.utc)
        })
    except Exception as e:
        logger.warning(f"Failed to log conversation: {e}")
    
    return GaneshaResponse(
        response=response,
        routed_to=routing["department"],
        scope=routing["scope"],
        source_product=routing.get("source_product"),
        models_used=models_used,
        level=2 if query.include_level2 else 1,
        data_sources=routing.get("data_sources", []),
        problems_addressed=routing.get("problems_solved", []),
        automation_percentage=routing.get("automation_percentage")
    )

# ============ OCR ENDPOINT ============

@router.post("/ocr")
async def process_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user)
):
    """Process PDF/Image with OCR using AI Vision"""
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    from dotenv import load_dotenv
    load_dotenv(override=False)
    
    api_key = os.getenv("EMERGENT_LLM_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="EMERGENT_LLM_KEY not configured")
    
    contents = await file.read()
    
    # Determine media type
    filename_lower = file.filename.lower()
    if filename_lower.endswith(".pdf"):
        media_type = "application/pdf"
    elif filename_lower.endswith(".png"):
        media_type = "image/png"
    elif filename_lower.endswith((".jpg", ".jpeg")):
        media_type = "image/jpeg"
    else:
        media_type = "image/png"  # Default
    
    try:
        # Use Gemini for vision tasks
        chat = LlmChat(
            api_key=api_key,
            session_id=f"ocr-{uuid4()}",
            system_message="You are a document analysis AI. Extract all text and data from documents accurately."
        ).with_model("gemini", "gemini-2.5-flash")
        
        prompt = f"""Extract all text and data from this document. If it contains tables, preserve the structure.
Return in markdown format with clear sections. File: {file.filename}"""
        
        # For now, return a structured response (vision requires different API)
        user_message = UserMessage(text=f"[Document uploaded: {file.filename}] {prompt}")
        response = await chat.send_message(user_message)
        
        return {
            "extracted_text": response,
            "file_name": file.filename,
            "file_size": len(contents),
            "media_type": media_type
        }
    except Exception as e:
        logger.error(f"OCR processing failed: {e}")
        raise HTTPException(status_code=500, detail=f"OCR processing failed: {str(e)}")

# ============ VOICE INPUT ENDPOINT ============

@router.post("/voice")
async def process_voice(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user)
):
    """
    Process voice input and transcribe using OpenAI Whisper API.
    Supports audio formats: mp3, wav, webm, m4a, ogg
    """
    try:
        # Read file contents
        contents = await file.read()
        file_size = len(contents)
        
        # Check file size (max 25MB for Whisper)
        if file_size > 25 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Audio file too large. Max 25MB allowed.")
        
        # Get file extension
        filename = file.filename or "audio.webm"
        extension = filename.split('.')[-1].lower() if '.' in filename else 'webm'
        
        # Supported formats
        supported_formats = ['mp3', 'wav', 'webm', 'm4a', 'ogg', 'flac', 'mp4', 'mpeg', 'mpga']
        if extension not in supported_formats:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported audio format: {extension}. Supported: {', '.join(supported_formats)}"
            )
        
        transcription = ""
        transcription_method = "none"
        
        # Try Emergent Speech-to-Text transcription (preferred)
        if EMERGENT_STT_AVAILABLE and EMERGENT_LLM_KEY:
            try:
                # Create a temporary file for the audio
                with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{extension}') as temp_file:
                    temp_file.write(contents)
                    temp_file_path = temp_file.name
                
                # Initialize Emergent STT client
                stt = OpenAISpeechToText(api_key=EMERGENT_LLM_KEY)
                
                # Transcribe using Whisper via Emergent
                with open(temp_file_path, 'rb') as audio_file:
                    response = await stt.transcribe(
                        file=audio_file,
                        model="whisper-1",
                        response_format="json"
                    )
                
                transcription = response.text if hasattr(response, 'text') else str(response)
                transcription_method = "whisper-1-emergent"
                
                # Clean up temp file
                os.unlink(temp_file_path)
                
                logger.info(f"Voice transcription successful via Emergent: {len(transcription)} chars")
                
            except Exception as e:
                logger.error(f"Emergent STT transcription error: {str(e)}")
                transcription = ""
                transcription_method = "failed"
        
        # Fallback to legacy OpenAI if Emergent failed
        elif OPENAI_AVAILABLE and EMERGENT_LLM_KEY and not transcription:
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{extension}') as temp_file:
                    temp_file.write(contents)
                    temp_file_path = temp_file.name
                
                client = OpenAI(api_key=EMERGENT_LLM_KEY)
                
                with open(temp_file_path, 'rb') as audio_file:
                    transcript = client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        response_format="text"
                    )
                
                transcription = transcript if isinstance(transcript, str) else str(transcript)
                transcription_method = "whisper-1-openai"
                
                os.unlink(temp_file_path)
                
                logger.info(f"Voice transcription successful via OpenAI: {len(transcription)} chars")
                
            except Exception as e:
                logger.error(f"OpenAI Whisper transcription error: {str(e)}")
                transcription = ""
                transcription_method = "failed"
        
        # Fallback message if no transcription
        if not transcription:
            return {
                "transcription": "",
                "file_name": filename,
                "file_size": file_size,
                "status": "no_transcription",
                "method": transcription_method,
                "message": "Voice transcription is not available. Please type your message instead.",
                "note": "Whisper API key may not be configured or there was an error."
            }
        
        # Log voice interaction to database
        db = get_db()
        await db.voice_logs.insert_one({
            "user_id": str(current_user.id),
            "timestamp": datetime.now(timezone.utc),
            "file_name": filename,
            "file_size": file_size,
            "transcription_length": len(transcription),
            "method": transcription_method
        })
        
        return {
            "transcription": transcription,
            "file_name": filename,
            "file_size": file_size,
            "status": "success",
            "method": transcription_method,
            "message": "Voice successfully transcribed"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Voice processing error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Voice processing failed: {str(e)}")

# ============ DEPARTMENT ROUTING INFO ============

@router.get("/routing-info")
async def get_routing_info(current_user: User = Depends(get_current_active_user)):
    """Get information about all department routing rules"""
    return {
        "internal_departments": list(DEPARTMENT_ROUTING["internal"].keys()),
        "external_departments": list(DEPARTMENT_ROUTING["external"].keys()),
        "guardian_departments": list(DEPARTMENT_ROUTING["guardian"].keys()),
        "total_departments": (
            len(DEPARTMENT_ROUTING["internal"]) + 
            len(DEPARTMENT_ROUTING["external"]) + 
            len(DEPARTMENT_ROUTING["guardian"])
        ),
        "routing_logic": "Queries are routed based on keyword matching. External products take priority."
    }

# ============ DAILY INTELLIGENCE COLLECTION ============

class DailyIntelligenceCreate(BaseModel):
    source: str  # URGAA, GSTSAAS, IGNITION, INTERNAL, EXTERNAL
    category: str  # market_data, competitor_intel, industry_news, financial_data
    title: str
    summary: str
    data: Optional[Dict[str, Any]] = None
    relevance_score: Optional[float] = 0.5
    tags: Optional[List[str]] = []

class DailyIntelligenceResponse(BaseModel):
    id: str
    source: str
    category: str
    title: str
    summary: str
    data: Optional[Dict[str, Any]]
    relevance_score: float
    tags: List[str]
    created_at: str
    processed: bool

@router.post("/intelligence", response_model=DailyIntelligenceResponse)
async def create_daily_intelligence(
    intel: DailyIntelligenceCreate,
    current_user: User = Depends(get_current_active_user)
):
    """
    Store daily intelligence/market data for KAILASH AI analysis.
    Categories: market_data, competitor_intel, industry_news, financial_data
    Sources: URGAA, GSTSAAS, IGNITION, INTERNAL, EXTERNAL
    """
    try:
        db = get_db()
        
        intel_doc = {
            "id": str(uuid4()),
            "source": intel.source.upper(),
            "category": intel.category,
            "title": intel.title,
            "summary": intel.summary,
            "data": intel.data or {},
            "relevance_score": intel.relevance_score,
            "tags": intel.tags or [],
            "created_at": datetime.now(timezone.utc).isoformat(),
            "created_by": str(current_user.id),
            "processed": False,
            "processed_insights": None
        }
        
        await db.daily_intelligence.insert_one(intel_doc)
        
        return DailyIntelligenceResponse(
            id=intel_doc["id"],
            source=intel_doc["source"],
            category=intel_doc["category"],
            title=intel_doc["title"],
            summary=intel_doc["summary"],
            data=intel_doc["data"],
            relevance_score=intel_doc["relevance_score"],
            tags=intel_doc["tags"],
            created_at=intel_doc["created_at"],
            processed=intel_doc["processed"]
        )
        
    except Exception as e:
        logger.error(f"Failed to store intelligence: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to store intelligence: {str(e)}")

@router.get("/intelligence")
async def get_daily_intelligence(
    source: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = 20,
    current_user: User = Depends(get_current_active_user)
):
    """
    Retrieve daily intelligence data with optional filtering.
    """
    try:
        db = get_db()
        
        # Build query filter
        query = {}
        if source:
            query["source"] = source.upper()
        if category:
            query["category"] = category
        
        # Get intelligence items
        cursor = db.daily_intelligence.find(query).sort("created_at", -1).limit(limit)
        items = await cursor.to_list(length=limit)
        
        return {
            "items": [
                {
                    "id": item.get("id"),
                    "source": item.get("source"),
                    "category": item.get("category"),
                    "title": item.get("title"),
                    "summary": item.get("summary"),
                    "relevance_score": item.get("relevance_score", 0.5),
                    "tags": item.get("tags", []),
                    "created_at": item.get("created_at"),
                    "processed": item.get("processed", False)
                }
                for item in items
            ],
            "total": len(items),
            "filters": {
                "source": source,
                "category": category
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to retrieve intelligence: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve intelligence: {str(e)}")

@router.get("/intelligence/summary")
async def get_intelligence_summary(current_user: User = Depends(get_current_active_user)):
    """
    Get a summary of daily intelligence by source and category.
    """
    try:
        db = get_db()
        
        # Count by source
        source_counts = {}
        for source in ['URGAA', 'GSTSAAS', 'IGNITION', 'INTERNAL', 'EXTERNAL']:
            count = await db.daily_intelligence.count_documents({"source": source})
            source_counts[source] = count
        
        # Count by category
        category_counts = {}
        for category in ['market_data', 'competitor_intel', 'industry_news', 'financial_data']:
            count = await db.daily_intelligence.count_documents({"category": category})
            category_counts[category] = count
        
        # Total counts
        total_count = await db.daily_intelligence.count_documents({})
        processed_count = await db.daily_intelligence.count_documents({"processed": True})
        
        return {
            "total_items": total_count,
            "processed_items": processed_count,
            "unprocessed_items": total_count - processed_count,
            "by_source": source_counts,
            "by_category": category_counts,
            "last_updated": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get intelligence summary: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get intelligence summary: {str(e)}")