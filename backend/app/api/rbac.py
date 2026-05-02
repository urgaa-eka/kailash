from fastapi import APIRouter, Depends, HTTPException
from app.api.deps import get_current_active_user
from app.core.rbac import (
    UserRole, Permission, ROLE_PERMISSIONS,
    get_user_permissions, expand_permissions, is_admin
)

router = APIRouter(prefix="/rbac", tags=["RBAC"])

@router.get("/roles")
async def list_roles():
    """List all available roles"""
    return {
        "roles": [
            {"name": role.value, "description": f"{role.value.replace('_', ' ').title()} role"}
            for role in UserRole
        ]
    }

@router.get("/permissions")
async def list_permissions():
    """List all available permissions"""
    return {
        "permissions": [
            {"name": perm.value, "category": perm.value.split(".")[0]}
            for perm in Permission
        ]
    }

@router.get("/roles/{role_name}/permissions")
async def get_role_permissions(role_name: str):
    """Get permissions for a specific role"""
    try:
        role = UserRole(role_name)
    except ValueError:
        raise HTTPException(status_code=404, detail="Role not found")
    
    permissions = ROLE_PERMISSIONS.get(role, [])
    expanded = expand_permissions(permissions)
    
    return {
        "role": role_name,
        "permissions": permissions,
        "expanded_permissions": expanded
    }

@router.get("/my-permissions")
async def get_my_permissions(current_user = Depends(get_current_active_user)):
    """Get current user's permissions"""
    permissions = get_user_permissions(current_user.role)
    expanded = expand_permissions(permissions)
    
    return {
        "role": current_user.role.value if hasattr(current_user.role, 'value') else current_user.role,
        "permissions": permissions,
        "expanded_permissions": expanded,
        "is_admin": is_admin(current_user)
    }

@router.get("/check/{permission}")
async def check_permission(permission: str, current_user = Depends(get_current_active_user)):
    """Check if current user has a specific permission"""
    from app.core.rbac import has_permission
    
    user_permissions = get_user_permissions(current_user.role)
    has_perm = has_permission(user_permissions, permission)
    
    return {
        "permission": permission,
        "granted": has_perm
    }
