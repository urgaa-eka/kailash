from enum import Enum
from functools import wraps
from typing import List, Optional, Union
from fastapi import HTTPException, status, Depends

class UserRole(str, Enum):
    """User roles with hierarchical access levels"""
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    MANAGER = "manager"
    OPERATOR = "operator"
    VIEWER = "viewer"

class Permission(str, Enum):
    """Granular permissions for fine-grained access control"""
    # Departments
    DEPARTMENTS_VIEW = "departments.view"
    DEPARTMENTS_INVOKE = "departments.invoke"
    DEPARTMENTS_MANAGE = "departments.manage"
    
    # Guardians
    GUARDIANS_VIEW = "guardians.view"
    GUARDIANS_MANAGE = "guardians.manage"
    GUARDIANS_CONFIGURE = "guardians.configure"
    
    # Users
    USERS_VIEW = "users.view"
    USERS_CREATE = "users.create"
    USERS_UPDATE = "users.update"
    USERS_DELETE = "users.delete"
    
    # Analytics
    ANALYTICS_VIEW = "analytics.view"
    ANALYTICS_EXPORT = "analytics.export"
    ANALYTICS_CONFIGURE = "analytics.configure"
    
    # Automobile/Pricing
    PRICING_VIEW = "pricing.view"
    PRICING_MANAGE = "pricing.manage"
    MARKET_DATA_VIEW = "market_data.view"
    MARKET_DATA_MANAGE = "market_data.manage"
    JOB_CARDS_VIEW = "job_cards.view"
    JOB_CARDS_ANALYZE = "job_cards.analyze"
    
    # Settings
    SETTINGS_VIEW = "settings.view"
    SETTINGS_UPDATE = "settings.update"
    
    # Tasks
    TASKS_VIEW = "tasks.view"
    TASKS_CREATE = "tasks.create"
    TASKS_ASSIGN = "tasks.assign"
    TASKS_DELETE = "tasks.delete"

# Role hierarchy (higher number = more access)
ROLE_HIERARCHY = {
    UserRole.SUPER_ADMIN: 100,
    UserRole.ADMIN: 80,
    UserRole.MANAGER: 60,
    UserRole.OPERATOR: 40,
    UserRole.VIEWER: 20
}

# Role to permissions mapping
ROLE_PERMISSIONS = {
    UserRole.SUPER_ADMIN: ["*"],
    
    UserRole.ADMIN: [
        "departments.*",
        "guardians.view", "guardians.manage",
        "users.*",
        "analytics.*",
        "pricing.*",
        "market_data.*",
        "job_cards.*",
        "settings.*",
        "tasks.*"
    ],
    
    UserRole.MANAGER: [
        "departments.view", "departments.invoke",
        "guardians.view",
        "users.view",
        "analytics.view", "analytics.export",
        "pricing.view",
        "market_data.view",
        "job_cards.view", "job_cards.analyze",
        "tasks.view", "tasks.create", "tasks.assign"
    ],
    
    UserRole.OPERATOR: [
        "departments.view", "departments.invoke",
        "guardians.view",
        "analytics.view",
        "pricing.view",
        "job_cards.view",
        "tasks.view", "tasks.create"
    ],
    
    UserRole.VIEWER: [
        "departments.view",
        "guardians.view",
        "analytics.view",
        "pricing.view",
        "tasks.view"
    ]
}

def get_role_level(role: Union[UserRole, str]) -> int:
    """Get numeric level for a role"""
    if isinstance(role, str):
        try:
            role = UserRole(role)
        except ValueError:
            return 0
    return ROLE_HIERARCHY.get(role, 0)

def has_permission(user_permissions: List[str], required: str) -> bool:
    """Check if user has a specific permission"""
    if "*" in user_permissions:
        return True
    if required in user_permissions:
        return True
    
    # Check wildcard patterns
    category = required.split(".")[0]
    if f"{category}.*" in user_permissions:
        return True
    
    return False

def get_user_permissions(role: Union[UserRole, str]) -> List[str]:
    """Get all permissions for a role"""
    if isinstance(role, str):
        try:
            role = UserRole(role)
        except ValueError:
            return []
    return ROLE_PERMISSIONS.get(role, [])

def expand_permissions(permissions: List[str]) -> List[str]:
    """Expand wildcard permissions to explicit list"""
    expanded = []
    for perm in permissions:
        if perm == "*":
            expanded.extend([p.value for p in Permission])
        elif perm.endswith(".*"):
            category = perm[:-2]
            expanded.extend([p.value for p in Permission if p.value.startswith(category)])
        else:
            expanded.append(perm)
    return list(set(expanded))

def require_role(min_role: Union[UserRole, str]):
    """Decorator to require minimum role level"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user=None, **kwargs):
            if current_user is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            user_level = get_role_level(current_user.role)
            required_level = get_role_level(min_role)
            
            if user_level < required_level:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Role '{min_role}' or higher required"
                )
            
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator

def require_permission(permission: Union[Permission, str]):
    """Decorator to require specific permission"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user=None, **kwargs):
            if current_user is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            user_permissions = get_user_permissions(current_user.role)
            perm_value = permission.value if isinstance(permission, Permission) else permission
            
            if not has_permission(user_permissions, perm_value):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission '{perm_value}' required"
                )
            
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator

def require_any_permission(*permissions: Union[Permission, str]):
    """Decorator to require any one of multiple permissions"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user=None, **kwargs):
            if current_user is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            user_permissions = get_user_permissions(current_user.role)
            
            for permission in permissions:
                perm_value = permission.value if isinstance(permission, Permission) else permission
                if has_permission(user_permissions, perm_value):
                    return await func(*args, current_user=current_user, **kwargs)
            
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return wrapper
    return decorator

class PermissionChecker:
    """Dependency class for checking permissions in routes"""
    
    def __init__(self, required_permissions: List[str]):
        self.required_permissions = required_permissions
    
    async def __call__(self, current_user):
        # Import here to avoid circular imports
        from app.api.deps import get_current_active_user
        
        # Get the current user if not provided
        if current_user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        
        user_permissions = get_user_permissions(current_user.role)
        
        for required in self.required_permissions:
            if not has_permission(user_permissions, required):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission '{required}' required"
                )
        
        return current_user

def is_admin(user) -> bool:
    """Check if user is admin or super_admin"""
    return get_role_level(user.role) >= get_role_level(UserRole.ADMIN)

def is_manager_or_above(user) -> bool:
    """Check if user is manager or above"""
    return get_role_level(user.role) >= get_role_level(UserRole.MANAGER)

def can_manage_users(user) -> bool:
    """Check if user can manage other users"""
    permissions = get_user_permissions(user.role)
    return has_permission(permissions, "users.create") or has_permission(permissions, "users.update")
