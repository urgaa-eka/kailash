from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime
import logging

from ..models.user import User
from ..core.mongodb import get_db
from ..core.security import get_password_hash
from ..api.deps import get_current_active_user
from ..core.rbac import require_permission, UserRole, Permission

router = APIRouter(prefix="/users", tags=["users"])
logger = logging.getLogger("kailash.users")


class UserCreate(BaseModel):
    email: EmailStr
    kailash_code: str
    full_name: str
    password: str
    role: str = "viewer"
    is_2fa_enabled: bool = False


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = None
    is_2fa_enabled: Optional[bool] = None


class UserResponse(BaseModel):
    id: str
    email: str
    kailash_code: str
    full_name: str
    role: str
    is_admin: bool
    is_active: bool
    is_2fa_enabled: bool
    created_at: Optional[str] = None


@router.get("/", response_model=dict)
async def list_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user)
):
    """List all users (requires users.view permission)"""
    # Check permission manually
    from ..core.rbac import has_permission, get_user_permissions
    user_permissions = get_user_permissions(current_user.role)
    if not has_permission(user_permissions, Permission.USERS_VIEW.value):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission 'users.view' required"
        )
    
    try:
        db = get_db()
        
        users_cursor = db.users.find().skip(skip).limit(limit)
        users_list = await users_cursor.to_list(length=limit)
        
        # Format users for response
        formatted_users = []
        for user_dict in users_list:
            formatted_users.append({
                "id": user_dict.get("id"),
                "email": user_dict.get("email"),
                "kailash_code": user_dict.get("kailash_code"),
                "full_name": user_dict.get("full_name", ""),
                "role": user_dict.get("role", "viewer"),
                "is_admin": user_dict.get("is_admin", False),
                "is_active": user_dict.get("is_active", True),
                "is_2fa_enabled": user_dict.get("is_2fa_enabled", False),
                "created_at": user_dict.get("created_at", "").isoformat() if hasattr(user_dict.get("created_at", ""), 'isoformat') else None
            })
        
        total = await db.users.count_documents({})
        
        return {
            "users": formatted_users,
            "total": total,
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        logger.error(f"Error listing users: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve users"
        )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get user by ID (requires users.view permission)"""
    # Check permission
    from ..core.rbac import has_permission, get_user_permissions
    user_permissions = get_user_permissions(current_user.role)
    if not has_permission(user_permissions, Permission.USERS_VIEW.value):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission 'users.view' required"
        )
    
    try:
        db = get_db()
        user_dict = await db.users.find_one({"id": user_id})
        
        if not user_dict:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return UserResponse(
            id=user_dict.get("id"),
            email=user_dict.get("email"),
            kailash_code=user_dict.get("kailash_code"),
            full_name=user_dict.get("full_name", ""),
            role=user_dict.get("role", "viewer"),
            is_admin=user_dict.get("is_admin", False),
            is_active=user_dict.get("is_active", True),
            is_2fa_enabled=user_dict.get("is_2fa_enabled", False),
            created_at=user_dict.get("created_at", "").isoformat() if hasattr(user_dict.get("created_at", ""), 'isoformat') else None
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user"
        )


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(get_current_active_user)
):
    """Create new user (requires users.create permission)"""
    # Check permission
    from ..core.rbac import has_permission, get_user_permissions
    user_permissions = get_user_permissions(current_user.role)
    if not has_permission(user_permissions, Permission.USERS_CREATE.value):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission 'users.create' required"
        )
    
    try:
        db = get_db()
        
        # Check if user already exists
        existing_email = await db.users.find_one({"email": user_data.email})
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        existing_code = await db.users.find_one({"kailash_code": user_data.kailash_code})
        if existing_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Kailash Code already registered"
            )
        
        # Create new user
        new_user = User(
            email=user_data.email,
            kailash_code=user_data.kailash_code,
            full_name=user_data.full_name,
            hashed_password=get_password_hash(user_data.password),
            role=user_data.role,
            is_2fa_enabled=user_data.is_2fa_enabled
        )
        
        user_dict = new_user.model_dump()
        await db.users.insert_one(user_dict)
        
        logger.info(f"User created: {user_data.email} by {current_user.email}")
        
        return UserResponse(
            id=new_user.id,
            email=new_user.email,
            kailash_code=new_user.kailash_code,
            full_name=new_user.full_name,
            role=new_user.role,
            is_admin=new_user.is_admin,
            is_active=new_user.is_active,
            is_2fa_enabled=new_user.is_2fa_enabled,
            created_at=new_user.created_at.isoformat() if hasattr(new_user.created_at, 'isoformat') else None
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """Update user (requires users.update permission)"""
    # Check permission
    from ..core.rbac import has_permission, get_user_permissions
    user_permissions = get_user_permissions(current_user.role)
    if not has_permission(user_permissions, Permission.USERS_UPDATE.value):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission 'users.update' required"
        )
    
    try:
        db = get_db()
        
        # Check if user exists
        existing_user = await db.users.find_one({"id": user_id})
        if not existing_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Prepare update data
        update_data = {}
        if user_data.full_name is not None:
            update_data["full_name"] = user_data.full_name
        if user_data.password is not None:
            update_data["hashed_password"] = get_password_hash(user_data.password)
        if user_data.role is not None:
            update_data["role"] = user_data.role
        if user_data.is_2fa_enabled is not None:
            update_data["is_2fa_enabled"] = user_data.is_2fa_enabled
        
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )
        
        # Update user
        await db.users.update_one(
            {"id": user_id},
            {"$set": update_data}
        )
        
        # Get updated user
        updated_user = await db.users.find_one({"id": user_id})
        
        logger.info(f"User updated: {updated_user.get('email')} by {current_user.email}")
        
        return UserResponse(
            id=updated_user.get("id"),
            email=updated_user.get("email"),
            kailash_code=updated_user.get("kailash_code"),
            full_name=updated_user.get("full_name", ""),
            role=updated_user.get("role", "viewer"),
            is_admin=updated_user.get("is_admin", False),
            is_active=updated_user.get("is_active", True),
            is_2fa_enabled=updated_user.get("is_2fa_enabled", False),
            created_at=updated_user.get("created_at", "").isoformat() if hasattr(updated_user.get("created_at", ""), 'isoformat') else None
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user"
        )


@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Delete user (requires users.delete permission)"""
    # Check permission
    from ..core.rbac import has_permission, get_user_permissions
    user_permissions = get_user_permissions(current_user.role)
    if not has_permission(user_permissions, Permission.USERS_DELETE.value):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission 'users.delete' required"
        )
    
    try:
        db = get_db()
        
        # Check if user exists
        existing_user = await db.users.find_one({"id": user_id})
        if not existing_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Prevent self-deletion
        if user_id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete your own account"
            )
        
        # Delete user
        await db.users.delete_one({"id": user_id})
        
        logger.info(f"User deleted: {existing_user.get('email')} by {current_user.email}")
        
        return {
            "deleted": True,
            "id": user_id,
            "message": "User deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user"
        )
