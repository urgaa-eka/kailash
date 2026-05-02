#!/usr/bin/env python3
"""
RAG Upload Script - Upload documents to GANESHA knowledge base
"""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

UPLOAD_QUEUE = [
    # Add documents here
    # {
    #     "path": "/path/to/document.pdf",
    #     "category": "operations",
    #     "department": "SURYA",
    #     "metadata": {"priority": "high", "version": "1.0"}
    # }
]

def upload_document(doc_config):
    """Upload a single document to RAG"""
    path = doc_config["path"]
    category = doc_config.get("category", "general")
    department = doc_config.get("department", "GENERAL")
    metadata = doc_config.get("metadata", {})
    
    if not os.path.exists(path):
        print(f"❌ File not found: {path}")
        return False
    
    print(f"📄 Uploading: {os.path.basename(path)}")
    print(f"   Category: {category}")
    print(f"   Department: {department}")
    
    # TODO: Implement actual RAG upload logic
    # This would integrate with your vector database (Pinecone/Weaviate/etc)
    
    print(f"✅ Uploaded successfully")
    return True

def main():
    """Main upload process"""
    print("🚀 RAG Upload Script")
    print(f"📊 Documents in queue: {len(UPLOAD_QUEUE)}")
    print("-" * 50)
    
    if not UPLOAD_QUEUE:
        print("⚠️  No documents in upload queue")
        print("   Edit UPLOAD_QUEUE in this script to add documents")
        return
    
    success_count = 0
    for doc in UPLOAD_QUEUE:
        if upload_document(doc):
            success_count += 1
    
    print("-" * 50)
    print(f"✅ Uploaded: {success_count}/{len(UPLOAD_QUEUE)}")

if __name__ == "__main__":
    main()
