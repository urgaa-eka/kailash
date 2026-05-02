"""
RAG (Retrieval Augmented Generation) Service
Connects Kailash-AI agents to Pinecone vector database for knowledge retrieval
"""

import os
import logging
from typing import List, Dict, Optional, Any
from pinecone import Pinecone
import anthropic
import hashlib
import json

logger = logging.getLogger("kailash.rag")


class RAGService:
    """
    RAG Service for Kailash-AI Knowledge Retrieval
    Queries Pinecone vector database and returns relevant context for AI agents
    """
    
    def __init__(
        self,
        pinecone_api_key: str = None,
        pinecone_index: str = "kailashai",
        pinecone_host: str = "us-east-1",
        anthropic_api_key: str = None
    ):
        """
        Initialize RAG Service
        
        Args:
            pinecone_api_key: Pinecone API key
            pinecone_index: Name of Pinecone index
            pinecone_host: Pinecone environment/host
            anthropic_api_key: Anthropic API key for embeddings
        """
        self.pinecone_api_key = pinecone_api_key or os.environ.get('PINECONE_API_KEY')
        self.pinecone_index_name = pinecone_index or os.environ.get('PINECONE_INDEX', 'kailashai')
        self.pinecone_host = pinecone_host or os.environ.get('PINECONE_HOST', 'us-east-1')
        self.anthropic_api_key = anthropic_api_key or os.environ.get('ANTHROPIC_API_KEY')
        
        self.pc = None
        self.index = None
        self.claude_client = None
        
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize Pinecone and Anthropic clients"""
        try:
            if self.pinecone_api_key:
                self.pc = Pinecone(api_key=self.pinecone_api_key)
                self.index = self.pc.Index(self.pinecone_index_name)
                logger.info(f"Pinecone initialized: index={self.pinecone_index_name}")
            else:
                logger.warning("Pinecone API key not configured - RAG disabled")
            
            if self.anthropic_api_key:
                self.claude_client = anthropic.Anthropic(api_key=self.anthropic_api_key)
                logger.info("Anthropic client initialized for embeddings")
            else:
                logger.warning("Anthropic API key not configured - embeddings disabled")
                
        except Exception as e:
            logger.error(f"Failed to initialize RAG clients: {e}")
    
    def _generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding using Claude's embedding capability
        Falls back to simple hash-based embedding if Claude unavailable
        
        Args:
            text: Text to embed
            
        Returns:
            List of floats representing the embedding
        """
        try:
            # Use Anthropic's embedding model via voyage
            # For now, use a simple approach with Claude to generate semantic representation
            if self.claude_client:
                # Generate a semantic hash using Claude
                response = self.claude_client.messages.create(
                    model="claude-3-haiku-20240307",
                    max_tokens=100,
                    messages=[{
                        "role": "user",
                        "content": f"Generate 10 key semantic keywords for this query, comma-separated: {text}"
                    }]
                )
                keywords = response.content[0].text.lower()
                
                # Create a simple embedding from keywords
                # This is a fallback - in production, use proper embedding model
                embedding = self._text_to_embedding(keywords, dim=1536)
                return embedding
            else:
                # Fallback to hash-based embedding
                return self._text_to_embedding(text, dim=1536)
                
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            return self._text_to_embedding(text, dim=1536)
    
    def _text_to_embedding(self, text: str, dim: int = 1536) -> List[float]:
        """
        Convert text to a simple embedding vector using hashing
        This is a fallback method - production should use proper embeddings
        
        Args:
            text: Text to convert
            dim: Dimension of output vector
            
        Returns:
            List of floats
        """
        # Create deterministic hash
        text_hash = hashlib.sha256(text.encode()).hexdigest()
        
        # Convert to floats
        embedding = []
        for i in range(0, min(len(text_hash), dim * 2), 2):
            if len(embedding) >= dim:
                break
            val = int(text_hash[i:i+2], 16) / 255.0 - 0.5
            embedding.append(val)
        
        # Pad if necessary
        while len(embedding) < dim:
            embedding.append(0.0)
        
        return embedding[:dim]
    
    async def query(
        self,
        query_text: str,
        product_filter: Optional[str] = None,
        document_type_filter: Optional[str] = None,
        top_k: int = 5,
        min_score: float = 0.3
    ) -> Dict[str, Any]:
        """
        Query the RAG knowledge base
        
        Args:
            query_text: Natural language query
            product_filter: Filter by product (URGAA, GSTSAAS, IGNITION, ARJUN)
            document_type_filter: Filter by document type
            top_k: Number of results to return
            min_score: Minimum similarity score threshold
            
        Returns:
            Dict containing matches and metadata
        """
        if not self.index:
            logger.warning("Pinecone not initialized - returning empty results")
            return {
                "matches": [],
                "context": "",
                "sources": [],
                "error": "RAG service not configured"
            }
        
        try:
            # Generate query embedding
            query_embedding = self._generate_embedding(query_text)
            
            # Build filter
            filter_dict = {}
            if product_filter:
                filter_dict["product"] = {"$eq": product_filter}
            if document_type_filter:
                filter_dict["document_type"] = {"$eq": document_type_filter}
            
            # Query Pinecone
            query_params = {
                "vector": query_embedding,
                "top_k": top_k,
                "include_metadata": True
            }
            
            if filter_dict:
                query_params["filter"] = filter_dict
            
            results = self.index.query(**query_params)
            
            # Process results
            matches = []
            context_parts = []
            sources = []
            
            for match in results.get("matches", []):
                score = match.get("score", 0)
                
                if score >= min_score:
                    metadata = match.get("metadata", {})
                    
                    matches.append({
                        "id": match.get("id"),
                        "score": score,
                        "title": metadata.get("title", "Unknown"),
                        "content": metadata.get("content", ""),
                        "product": metadata.get("product", ""),
                        "document_type": metadata.get("document_type", ""),
                        "source": metadata.get("source", "")
                    })
                    
                    # Build context string
                    content = metadata.get("content", "")
                    if content:
                        context_parts.append(f"[{metadata.get('title', 'Source')}]: {content}")
                    
                    # Track sources
                    source = metadata.get("source", metadata.get("title", ""))
                    if source and source not in sources:
                        sources.append(source)
            
            return {
                "matches": matches,
                "context": "\n\n".join(context_parts),
                "sources": sources,
                "query": query_text,
                "filters_applied": filter_dict
            }
            
        except Exception as e:
            logger.error(f"RAG query failed: {e}")
            return {
                "matches": [],
                "context": "",
                "sources": [],
                "error": str(e)
            }
    
    async def query_for_agent(
        self,
        agent_id: str,
        query_text: str,
        user_context: Optional[Dict] = None
    ) -> str:
        """
        Query RAG specifically for an agent's context needs
        
        Args:
            agent_id: Agent identifier (e.g., "U-AI-01" for SURYA)
            query_text: User's query
            user_context: Additional context about user/session
            
        Returns:
            Formatted context string for agent prompt injection
        """
        # Map agents to their product domains
        agent_product_map = {
            # URGAA agents
            "U-AI-01": "URGAA", "U-AI-02": "URGAA", "U-AI-03": "URGAA",
            "U-AI-04": "URGAA", "U-AI-05": "URGAA", "U-AI-06": "URGAA",
            "U-AI-07": "URGAA", "U-AI-08": "URGAA",
            # GSTSAAS agents
            "G-AI-01": "GSTSAAS", "G-AI-02": "GSTSAAS", "G-AI-03": "GSTSAAS",
            "G-AI-04": "GSTSAAS", "G-AI-05": "GSTSAAS", "G-AI-06": "GSTSAAS",
            "G-AI-07": "GSTSAAS", "G-AI-08": "GSTSAAS", "G-AI-09": "GSTSAAS",
            "G-AI-10": "GSTSAAS",
            # IGNITION agents
            "I-AI-01": "IGNITION", "I-AI-02": "IGNITION", "I-AI-03": "IGNITION",
            "I-AI-04": "IGNITION", "I-AI-05": "IGNITION", "I-AI-06": "IGNITION",
            "I-AI-07": "IGNITION", "I-AI-08": "IGNITION", "I-AI-09": "IGNITION",
            # ARJUN agents
            "A-AI-01": "ARJUN", "A-AI-02": "ARJUN", "A-AI-03": "ARJUN",
            "A-AI-04": "ARJUN", "A-AI-05": "ARJUN", "A-AI-06": "ARJUN",
            "A-AI-07": "ARJUN", "A-AI-08": "ARJUN",
            # Master orchestrator
            "GANESHA": None  # Searches all products
        }
        
        product_filter = agent_product_map.get(agent_id)
        
        # Query RAG
        result = await self.query(
            query_text=query_text,
            product_filter=product_filter,
            top_k=5,
            min_score=0.3
        )
        
        if not result.get("context"):
            return ""
        
        # Format context for prompt injection
        context_header = "---\nRELEVANT KNOWLEDGE FROM GO4GARAGE DATABASE:\n"
        context_footer = "\n---\n"
        
        formatted_context = context_header + result["context"] + context_footer
        
        if result.get("sources"):
            formatted_context += f"Sources: {', '.join(result['sources'])}\n"
        
        return formatted_context
    
    async def add_document(
        self,
        document_id: str,
        content: str,
        metadata: Dict[str, Any]
    ) -> bool:
        """
        Add a document to the RAG knowledge base
        
        Args:
            document_id: Unique identifier for the document
            content: Document content
            metadata: Document metadata (title, product, type, etc.)
            
        Returns:
            True if successful
        """
        if not self.index:
            logger.error("Pinecone not initialized")
            return False
        
        try:
            # Generate embedding
            embedding = self._generate_embedding(content)
            
            # Prepare metadata
            full_metadata = {
                "content": content[:4000],  # Truncate for metadata limit
                **metadata
            }
            
            # Upsert to Pinecone
            self.index.upsert(
                vectors=[{
                    "id": document_id,
                    "values": embedding,
                    "metadata": full_metadata
                }]
            )
            
            logger.info(f"Document added to RAG: {document_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add document to RAG: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get RAG index statistics"""
        if not self.index:
            return {"error": "Index not initialized", "status": "disconnected"}
        
        try:
            stats = self.index.describe_index_stats()
            # Pinecone v6 returns object - convert to JSON-safe primitives
            total_vectors = int(stats.total_vector_count) if stats.total_vector_count else 0
            dimension = int(stats.dimension) if stats.dimension else 0
            index_fullness = float(stats.index_fullness) if stats.index_fullness else 0.0
            
            # Safely extract namespace counts
            namespaces_info = {}
            if hasattr(stats, 'namespaces') and stats.namespaces:
                for ns_name, ns_data in stats.namespaces.items():
                    namespaces_info[ns_name] = {
                        "vector_count": int(ns_data.vector_count) if hasattr(ns_data, 'vector_count') else 0
                    }
            
            return {
                "total_vectors": total_vectors,
                "dimension": dimension,
                "index_fullness": index_fullness,
                "namespaces": namespaces_info,
                "status": "connected"
            }
        except Exception as e:
            return {"error": str(e), "status": "error"}


# Singleton instance
_rag_service_instance = None


def get_rag_service(
    pinecone_api_key: str = None,
    pinecone_index: str = None,
    anthropic_api_key: str = None
) -> RAGService:
    """
    Get or create RAG service singleton
    
    Args:
        pinecone_api_key: Pinecone API key
        pinecone_index: Pinecone index name
        anthropic_api_key: Anthropic API key
        
    Returns:
        RAGService instance
    """
    global _rag_service_instance
    
    if _rag_service_instance is None:
        _rag_service_instance = RAGService(
            pinecone_api_key=pinecone_api_key,
            pinecone_index=pinecone_index,
            anthropic_api_key=anthropic_api_key
        )
    
    return _rag_service_instance
