"""Knowledge Base API endpoints for RAG document management."""
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timezone
import logging

from ..api.deps import get_current_user
from ..services.rag_knowledge_base import get_rag_knowledge_base
from ..core.mongodb import MongoD

router = APIRouter(prefix="/api/knowledge-base", tags=["Knowledge Base RAG"])
logger = logging.getLogger(__name__)


# ============= REQUEST/RESPONSE MODELS =============

class DocumentUploadResponse(BaseModel):
    doc_id: str
    filename: str
    chunks_created: int
    doc_type: str
    products: str
    version: str
    status: str


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=1000)
    top_k: int = Field(default=5, ge=1, le=20)
    filter_by_product: Optional[str] = Field(default=None, pattern="^(all|urgaa|gstsaas|ignition|arjun)$")
    filter_by_type: Optional[str] = Field(default=None, pattern="^(foundation|product|operations|technical|training)$")
    min_score: float = Field(default=0.7, ge=0.0, le=1.0)


class QuerySource(BaseModel):
    source_filename: str
    chunk_text: str
    relevance_score: float
    doc_type: str
    products: str
    version: str
    chunk_index: int
    doc_id: str


class QueryResponse(BaseModel):
    query: str
    sources: List[QuerySource]
    context: str
    total_results: int
    filters_applied: dict


class DocumentInfo(BaseModel):
    doc_id: str
    filename: str
    doc_type: str
    products: str
    version: str
    total_chunks: int
    uploaded_at: str
    uploaded_by: str


class StatsResponse(BaseModel):
    total_vectors: int
    total_documents: int
    index_name: str
    dimension: int
    by_doc_type: dict
    by_product: dict
    documents: List[DocumentInfo]


# ============= ENDPOINTS =============

@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    doc_type: str = Form(..., pattern="^(foundation|product|operations|technical|training)$"),
    products: str = Form(..., pattern="^(all|urgaa|gstsaas|ignition|arjun)$"),
    version: str = Form(default="1.0"),
    current_user: dict = Depends(get_current_user)
):
    """Upload a single markdown document to the knowledge base.
    
    - **file**: Markdown file (.md)
    - **doc_type**: foundation / product / operations / technical / training
    - **products**: all / urgaa / gstsaas / ignition / arjun
    - **version**: Document version (e.g., 1.0, 1.1)
    """
    # Validate file type
    if not file.filename.endswith('.md'):
        raise HTTPException(status_code=400, detail="Only markdown (.md) files are supported")
    
    # Check file size (max 10MB)
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size exceeds 10MB limit")
    
    try:
        content_str = content.decode('utf-8')
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File must be UTF-8 encoded")
    
    # Upload to RAG knowledge base
    rag_kb = get_rag_knowledge_base()
    
    # Handle both dict and User model
    user_email = current_user.email if hasattr(current_user, 'email') else current_user.get("email", "unknown")
    
    try:
        result = await rag_kb.upload_document(
            filename=file.filename,
            content=content_str,
            doc_type=doc_type,
            products=products,
            version=version,
            uploaded_by=user_email
        )
        
        # Store metadata in MongoDB for tracking
        db = MongoD.get_database()
        await db.knowledge_base_docs.update_one(
            {"doc_id": result["doc_id"]},
            {
                "$set": {
                    "doc_id": result["doc_id"],
                    "filename": file.filename,
                    "doc_type": doc_type,
                    "products": products,
                    "version": version,
                    "chunks_created": result["chunks_created"],
                    "uploaded_at": datetime.now(timezone.utc).isoformat(),
                    "uploaded_by": user_email,
                    "file_size_bytes": len(content)
                }
            },
            upsert=True
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.post("/upload-bulk")
async def upload_bulk_documents(
    files: List[UploadFile] = File(...),
    doc_type: str = Form(..., pattern="^(foundation|product|operations|technical|training)$"),
    products: str = Form(..., pattern="^(all|urgaa|gstsaas|ignition|arjun)$"),
    version: str = Form(default="1.0"),
    background_tasks: BackgroundTasks = None,
    current_user: dict = Depends(get_current_user)
):
    """Upload multiple markdown documents at once.
    
    - **files**: Multiple markdown files (.md)
    - **doc_type**: foundation / product / operations / technical / training
    - **products**: all / urgaa / gstsaas / ignition / arjun
    - **version**: Document version
    """
    results = []
    errors = []
    
    rag_kb = get_rag_knowledge_base()
    db = MongoD.get_database()
    
    for file in files:
        # Validate file type
        if not file.filename.endswith('.md'):
            errors.append({"filename": file.filename, "error": "Not a markdown file"})
            continue
        
        try:
            content = await file.read()
            content_str = content.decode('utf-8')
            
            # Handle both dict and User model
            user_email = current_user.email if hasattr(current_user, 'email') else current_user.get("email", "unknown")
            
            result = await rag_kb.upload_document(
                filename=file.filename,
                content=content_str,
                doc_type=doc_type,
                products=products,
                version=version,
                uploaded_by=user_email
            )
            
            # Store in MongoDB
            await db.knowledge_base_docs.update_one(
                {"doc_id": result["doc_id"]},
                {
                    "$set": {
                        "doc_id": result["doc_id"],
                        "filename": file.filename,
                        "doc_type": doc_type,
                        "products": products,
                        "version": version,
                        "chunks_created": result["chunks_created"],
                        "uploaded_at": datetime.now(timezone.utc).isoformat(),
                        "uploaded_by": user_email,
                        "file_size_bytes": len(content)
                    }
                },
                upsert=True
            )
            
            results.append(result)
            
        except Exception as e:
            errors.append({"filename": file.filename, "error": str(e)})
    
    return {
        "uploaded": len(results),
        "failed": len(errors),
        "results": results,
        "errors": errors
    }


@router.post("/query", response_model=QueryResponse)
async def query_knowledge_base(
    request: QueryRequest,
    current_user: dict = Depends(get_current_user)
):
    """Query the knowledge base with semantic search.
    
    Returns relevant document chunks with source attribution.
    
    - **query**: Your question or search query
    - **top_k**: Number of results (1-20)
    - **filter_by_product**: Filter by product (urgaa, gstsaas, ignition, arjun, all)
    - **filter_by_type**: Filter by doc type (foundation, product, operations, technical, training)
    - **min_score**: Minimum relevance score (0.0-1.0)
    """
    rag_kb = get_rag_knowledge_base()
    
    try:
        result = await rag_kb.query(
            query_text=request.query,
            top_k=request.top_k,
            filter_by_product=request.filter_by_product,
            filter_by_type=request.filter_by_type,
            min_score=request.min_score
        )
        
        # Log query for analytics
        db = MongoD.get_database()
        # Handle both dict and User model
        user_email = current_user.email if hasattr(current_user, 'email') else current_user.get("email", "unknown")
        
        await db.knowledge_base_queries.insert_one({
            "query": request.query,
            "user": user_email,
            "filters": {
                "product": request.filter_by_product,
                "type": request.filter_by_type
            },
            "results_count": result["total_results"],
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        return result
        
    except Exception as e:
        logger.error(f"Query error: {e}")
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")


@router.get("/documents", response_model=List[DocumentInfo])
async def list_documents(
    current_user: dict = Depends(get_current_user)
):
    """List all documents in the knowledge base."""
    rag_kb = get_rag_knowledge_base()
    
    try:
        documents = await rag_kb.list_documents()
        return documents
    except Exception as e:
        logger.error(f"List documents error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list documents: {str(e)}")


@router.delete("/documents/{doc_id}")
async def delete_document(
    doc_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a document from the knowledge base."""
    rag_kb = get_rag_knowledge_base()
    
    try:
        result = await rag_kb.delete_document(doc_id)
        
        # Remove from MongoDB
        db = MongoD.get_database()
        await db.knowledge_base_docs.delete_one({"doc_id": doc_id})
        
        return result
    except Exception as e:
        logger.error(f"Delete error: {e}")
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")


@router.get("/stats", response_model=StatsResponse)
async def get_stats(
    current_user: dict = Depends(get_current_user)
):
    """Get knowledge base statistics."""
    rag_kb = get_rag_knowledge_base()
    
    try:
        stats = await rag_kb.get_stats()
        return stats
    except Exception as e:
        logger.error(f"Stats error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")


# ============= AGENT INTEGRATION ENDPOINT =============

@router.post("/agent-query")
async def agent_query(
    query: str,
    agent_name: str = "GANESHA",
    product_context: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Simplified query endpoint for AI agents.
    
    Used by all 35 KAILASH-AI agents to retrieve relevant knowledge.
    
    - **query**: The agent's question
    - **agent_name**: Name of the requesting agent
    - **product_context**: Optional product context for filtering
    """
    rag_kb = get_rag_knowledge_base()
    
    try:
        result = await rag_kb.query(
            query_text=query,
            top_k=5,
            filter_by_product=product_context,
            min_score=0.65
        )
        
        # Format for agent consumption
        return {
            "agent": agent_name,
            "query": query,
            "knowledge_found": result["total_results"] > 0,
            "context": result["context"],
            "sources": [
                {
                    "file": s["source_filename"],
                    "relevance": s["relevance_score"],
                    "excerpt": s["chunk_text"][:300] + "..." if len(s["chunk_text"]) > 300 else s["chunk_text"]
                }
                for s in result["sources"]
            ]
        }
        
    except Exception as e:
        logger.error(f"Agent query error: {e}")
        return {
            "agent": agent_name,
            "query": query,
            "knowledge_found": False,
            "context": "",
            "sources": [],
            "error": str(e)
        }
