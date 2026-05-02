from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from datetime import datetime
from bson import ObjectId
from app.core.mongodb import MongoD
from app.api.deps import get_current_active_user

router = APIRouter(prefix="/conversations", tags=["Conversations"])

@router.get("/")
async def list_conversations(
    limit: int = Query(default=20, ge=1, le=100),
    skip: int = Query(default=0, ge=0),
    current_user = Depends(get_current_active_user)
):
    """List user's conversations"""
    db = MongoD.get_database()
    conversations = await db.conversations.find(
        {"user_id": str(current_user.id)}
    ).sort("updated_at", -1).skip(skip).limit(limit).to_list(limit)
    
    return {
        "conversations": [
            {
                "id": str(c["_id"]),
                "created_at": c["created_at"].isoformat(),
                "updated_at": c["updated_at"].isoformat(),
                "message_count": len(c.get("messages", [])),
                "preview": c.get("messages", [{}])[0].get("content", "")[:100] if c.get("messages") else ""
            }
            for c in conversations
        ],
        "total": await db.conversations.count_documents({"user_id": str(current_user.id)})
    }

@router.get("/{conversation_id}")
async def get_conversation(
    conversation_id: str,
    current_user = Depends(get_current_active_user)
):
    """Get conversation details with messages"""
    db = MongoD.get_database()
    try:
        conv = await db.conversations.find_one({
            "_id": ObjectId(conversation_id),
            "user_id": str(current_user.id)
        })
    except:
        raise HTTPException(status_code=400, detail="Invalid conversation ID")
    
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return {
        "id": str(conv["_id"]),
        "messages": [
            {
                "role": m["role"],
                "content": m["content"],
                "timestamp": m["timestamp"].isoformat() if isinstance(m.get("timestamp"), datetime) else m.get("timestamp")
            }
            for m in conv.get("messages", [])
        ],
        "created_at": conv["created_at"].isoformat(),
        "updated_at": conv["updated_at"].isoformat()
    }

@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    current_user = Depends(get_current_active_user)
):
    """Delete a conversation"""
    db = MongoD.get_database()
    try:
        result = await db.conversations.delete_one({
            "_id": ObjectId(conversation_id),
            "user_id": str(current_user.id)
        })
    except:
        raise HTTPException(status_code=400, detail="Invalid conversation ID")
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return {"deleted": True, "id": conversation_id}

@router.post("/{conversation_id}/clear")
async def clear_conversation(
    conversation_id: str,
    current_user = Depends(get_current_active_user)
):
    """Clear all messages in a conversation"""
    db = MongoD.get_database()
    try:
        result = await db.conversations.update_one(
            {"_id": ObjectId(conversation_id), "user_id": str(current_user.id)},
            {"$set": {"messages": [], "updated_at": datetime.utcnow()}}
        )
    except:
        raise HTTPException(status_code=400, detail="Invalid conversation ID")
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return {"cleared": True, "id": conversation_id}
