from enum import Enum
from typing import List, Dict
from functools import wraps
from fastapi import HTTPException, status

class UserRole(str, Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    MANAGER = "manager"
    OPERATOR = "operator"
    VIEWER = "viewer"

class Permission(str, Enum):
    DEPARTMENTS_VIEW = "departments.view"
    DEPARTMENTS_INVOKE = "departments.invoke"
    DEPARTMENTS_MANAGE = "departments.manage"
    GUARDIANS_VIEW = "guardians.view"
    GUARDIANS_MANAGE = "guardians.manage"
    USERS_VIEW = "users.view"
    USERS_CREATE = "users.create"
    USERS_UPDATE = "users.update"
    USERS_DELETE = "users.delete"
    ANALYTICS_VIEW = "analytics.view"
    SETTINGS_VIEW = "settings.view"
    SETTINGS_UPDATE = "settings.update"
    TASKS_VIEW = "tasks.view"
    TASKS_CREATE = "tasks.create"
    TASKS_OWN = "tasks.own"

ROLE_PERMISSIONS: Dict[UserRole, List[Permission]] = {
    UserRole.SUPER_ADMIN: list(Permission),
    UserRole.ADMIN: [
        Permission.DEPARTMENTS_VIEW,
        Permission.DEPARTMENTS_INVOKE,
        Permission.DEPARTMENTS_MANAGE,
        Permission.GUARDIANS_VIEW,
        Permission.USERS_VIEW,
        Permission.USERS_CREATE,
        Permission.USERS_UPDATE,
        Permission.ANALYTICS_VIEW,
        Permission.SETTINGS_VIEW,
        Permission.SETTINGS_UPDATE,
        Permission.TASKS_VIEW,
        Permission.TASKS_CREATE,
    ],
    UserRole.MANAGER: [
        Permission.DEPARTMENTS_VIEW,
        Permission.DEPARTMENTS_INVOKE,
        Permission.ANALYTICS_VIEW,
        Permission.TASKS_VIEW,
        Permission.TASKS_CREATE,
    ],
    UserRole.OPERATOR: [
        Permission.DEPARTMENTS_VIEW,
        Permission.DEPARTMENTS_INVOKE,
        Permission.TASKS_VIEW,
        Permission.TASKS_OWN,
    ],
    UserRole.VIEWER: [
        Permission.DEPARTMENTS_VIEW,
        Permission.ANALYTICS_VIEW,
        Permission.TASKS_VIEW,
    ]
}

def has_permission(user_role: str, required_permission: Permission) -> bool:
    """Check if user role has permission"""
    try:
        role = UserRole(user_role)
        permissions = ROLE_PERMISSIONS.get(role, [])
        return required_permission in permissions or role == UserRole.SUPER_ADMIN
    except ValueError:
        return False

def require_permission(permission: Permission):
    """Decorator to require permission"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user: dict = None, **kwargs):
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            user_role = current_user.get("role", "viewer")
            if not has_permission(user_role, permission):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission denied: {permission.value}"
                )
            
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator
