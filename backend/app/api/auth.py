from fastapi import APIRouter, HTTPException, status, Depends, Request
from datetime import timedelta
import logging
import pyotp
import secrets

from ..schemas.auth import UserRegister, UserLogin, Token
from ..models.user import User
from ..core.mongodb import get_db
from ..core.security import verify_password, get_password_hash, create_access_token, decode_token
from ..core.config import settings
from ..api.deps import get_current_active_user
from ..middleware.security import security_middleware
from ..middleware.error_handler import error_handler
from ..core.permissions import UserRole, has_permission

router = APIRouter(prefix="/auth", tags=["authentication"])
logger = logging.getLogger("kailash.auth")

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister):
    """Register a new user"""
    db = get_db()
    
    # Check if user already exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if Kailash Code already exists
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
        hashed_password=get_password_hash(user_data.password)
    )
    
    # Convert to dict for MongoD
    user_dict = new_user.model_dump()
    await db.users.insert_one(user_dict)
    
    # Create access token
    access_token = create_access_token(
        data={"sub": new_user.id, "kailash_code": new_user.kailash_code}
    )
    
    # Return token and user info
    user_response = {
        "id": new_user.id,
        "email": new_user.email,
        "kailash_code": new_user.kailash_code,
        "full_name": new_user.full_name,
        "is_admin": new_user.is_admin
    }
    
    return Token(access_token=access_token, user=user_response)

@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, request: Request):
    """
    Login with login_id (kailash_code) and optional password
    """
    try:
        login_id = credentials.login_id
        
        # Check for device lockout BEFORE attempting login
        await security_middleware.check_device_lockout(
            login_id,
            request
        )
        
        db = get_db()
        
        # Find user by kailash_code (login_id)
        user_dict = await db.users.find_one({"kailash_code": login_id})
        
        if not user_dict:
            security_middleware.record_failed_login(login_id, request)
            error_handler.log_authentication(
                login_id,
                request.client.host if request.client else "unknown",
                False,
                security_middleware.get_device_fingerprint(request)
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Login ID. Access denied.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user = User(**user_dict)
        
        # Verify password if provided
        if credentials.password:
            if not verify_password(credentials.password, user.hashed_password):
                security_middleware.record_failed_login(login_id, request)
                error_handler.log_authentication(
                    login_id,
                    request.client.host if request.client else "unknown",
                    False,
                    security_middleware.get_device_fingerprint(request)
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid Login ID or Password. Access denied.",
                    headers={"WWW-Authenticate": "Bearer"},
                )
        
        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user account"
            )
        
        # Check if temporary user has expired
        if user_dict.get('is_temporary') and user_dict.get('expires_at'):
            from datetime import datetime, timezone
            expires_at = user_dict.get('expires_at')
            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=timezone.utc)
            if datetime.now(timezone.utc) > expires_at:
                await db.users.update_one(
                    {"kailash_code": login_id},
                    {"$set": {"is_active": False}}
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="This temporary access has expired. Please contact administrator.",
                    headers={"WWW-Authenticate": "Bearer"},
                )
        
        # Clear failed attempts on successful login
        security_middleware.clear_failed_logins(login_id, request)
        
        # Log successful authentication
        error_handler.log_authentication(
            login_id,
            request.client.host if request.client else "unknown",
            True,
            security_middleware.get_device_fingerprint(request)
        )
        
        # Create access token
        access_token = create_access_token(
            data={"sub": user.id, "kailash_code": user.kailash_code},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        # Return token and user info
        user_response = {
            "id": user.id,
            "email": user.email,
            "kailash_code": user.kailash_code,
            "full_name": user.full_name,
            "is_admin": user.is_admin
        }
        
        return Token(access_token=access_token, user=user_response)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        
        # Check if it's a MongoDB authorization error (code 13)
        error_msg = str(e).lower()
        if "not authorized" in error_msg or "unauthorized" in error_msg or (hasattr(e, 'code') and e.code == 13):
            logger.critical("MongoDB permission error detected. Atlas user lacks read permissions on users collection.")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database configuration error. Please contact system administrator. Atlas MongoDB user requires read/write permissions on kailash database."
            )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication error"
        )

@router.get("/me")
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Get current user information"""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "kailash_code": current_user.kailash_code,
        "full_name": current_user.full_name,
        "is_admin": current_user.is_admin,
        "is_active": current_user.is_active,
        "role": getattr(current_user, "role", "viewer"),
        "is_fa_enabled": getattr(current_user, "is_fa_enabled", False)
    }

@router.post("/refresh")
async def refresh_token(refresh_token: str):
    """Refresh access token"""
    try:
        payload = decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        
        db = await get_db()
        user = await db["users"].find_one({"_id": payload["sub"]})
        
        if not user:
            raise HTTPException(status_code=44, detail="User not found")
        
        access_token = create_access_token(str(user["_id"]))
        new_refresh_token = create_access_token(str(user["_id"]), expires_delta=timedelta(days=1))
        
        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid refresh token")

@router.get("/permissions")
async def get_user_permissions(current_user: User = Depends(get_current_active_user)):
    """Get user permissions"""
    from ..core.permissions import ROLE_PERMISSIONS
    try:
        role_str = getattr(current_user, "role", None) or ("admin" if current_user.is_admin else "viewer")
        role = UserRole(role_str)
        permissions = ROLE_PERMISSIONS.get(role, [])
        return {
            "role": role.value,
            "permissions": [p.value for p in permissions],
            "is_fa_enabled": getattr(current_user, "is_fa_enabled", False)
        }
    except ValueError:
        return {
            "role": "viewer",
            "permissions": [],
            "is_fa_enabled": getattr(current_user, "is_fa_enabled", False)
        }

# ============================================================================
# 2FA ENDPOINTS
# ============================================================================

@router.post("/2fa/setup")
async def setup_2fa(current_user: User = Depends(get_current_active_user)):
    """Setup 2FA for current user"""
    db = get_db()
    
    # Generate TOTP secret
    secret = pyotp.random_base32()
    
    # Update user with secret
    await db.users.update_one(
        {"id": current_user.id},
        {"$set": {"totp_secret": secret}}
    )
    
    # Generate provisioning URI for QR code
    totp = pyotp.TOTP(secret)
    provisioning_uri = totp.provisioning_uri(
        name=current_user.email,
        issuer_name="Kailash"
    )
    
    logger.info(f"2FA setup initiated for user: {current_user.email}")
    
    return {
        "secret": secret,
        "qr_uri": provisioning_uri,
        "status": "setup_initiated"
    }

@router.post("/2fa/verify")
async def verify_2fa_setup(
    code: str,
    current_user: User = Depends(get_current_active_user)
):
    """Verify and enable 2FA"""
    db = get_db()
    
    if not current_user.totp_secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA not set up. Call /2fa/setup first"
        )
    
    # Verify the code
    totp = pyotp.TOTP(current_user.totp_secret)
    if not totp.verify(code):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid 2FA code"
        )
    
    # Generate backup codes
    backup_codes = [secrets.token_hex(4).upper() for _ in range(10)]
    
    # Enable 2FA for user
    await db.users.update_one(
        {"id": current_user.id},
        {"$set": {
            "is_2fa_enabled": True,
            "backup_codes": backup_codes
        }}
    )
    
    logger.info(f"2FA enabled for user: {current_user.email}")
    
    return {
        "enabled": True,
        "backup_codes": backup_codes,
        "message": "2FA successfully enabled. Save your backup codes securely."
    }

@router.post("/2fa/validate")
async def validate_2fa_login(code: str, temp_token: str):
    """Validate 2FA code during login"""
    db = get_db()
    
    try:
        # Decode temp token
        payload = decode_token(temp_token)
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        # Get user
        user_dict = await db.users.find_one({"id": user_id})
        if not user_dict:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user = User(**user_dict)
        
        # Verify 2FA code
        totp = pyotp.TOTP(user.totp_secret)
        is_valid = totp.verify(code)
        
        # Check backup codes if TOTP fails
        if not is_valid and code.upper() in (user.backup_codes or []):
            is_valid = True
            # Remove used backup code
            updated_codes = [c for c in user.backup_codes if c != code.upper()]
            await db.users.update_one(
                {"id": user.id},
                {"$set": {"backup_codes": updated_codes}}
            )
            logger.info(f"Backup code used for user: {user.email}")
        
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid 2FA code"
            )
        
        # Generate full access tokens
        access_token = create_access_token(data={"sub": user.id})
        refresh_token = create_access_token(
            data={"sub": user.id, "type": "refresh"},
            expires_delta=timedelta(days=7)
        )
        
        logger.info(f"2FA validation successful for user: {user.email}")
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "kailash_code": user.kailash_code,
                "full_name": user.full_name,
                "is_admin": user.is_admin
            }
        }
        
    except Exception as e:
        logger.error(f"2FA validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="2FA validation failed"
        )

@router.post("/2fa/disable")
async def disable_2fa(
    password: str,
    current_user: User = Depends(get_current_active_user)
):
    """Disable 2FA (requires password confirmation)"""
    db = get_db()
    
    # Verify password
    if not verify_password(password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password"
        )
    
    # Disable 2FA
    await db.users.update_one(
        {"id": current_user.id},
        {"$set": {
            "is_2fa_enabled": False,
            "totp_secret": None,
            "backup_codes": []
        }}
    )
    
    logger.info(f"2FA disabled for user: {current_user.email}")
    
    return {"disabled": True, "message": "2FA has been disabled"}



# ============================================================================
# PASSWORD RESET ENDPOINTS
# ============================================================================

from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
import hashlib
from ..services.email_service import email_service

class PasswordResetRequest(BaseModel):
    email: str

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str

@router.post("/password/reset-request")
async def request_password_reset(request_data: PasswordResetRequest):
    """
    Request password reset - generates reset token and sends email via AWS SES
    """
    db = get_db()
    
    # Find user by email
    user = await db.users.find_one({"email": request_data.email})
    
    # Always return success to prevent email enumeration
    if not user:
        logger.info(f"Password reset requested for non-existent email: {request_data.email}")
        return {
            "message": "If an account with that email exists, a password reset link has been sent.",
            "status": "sent"
        }
    
    # Generate reset token
    reset_token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(reset_token.encode()).hexdigest()
    expiry = datetime.utcnow() + timedelta(hours=1)
    
    # Store token hash in database
    await db.users.update_one(
        {"id": user["id"]},
        {"$set": {
            "reset_token_hash": token_hash,
            "reset_token_expiry": expiry
        }}
    )
    
    logger.info(f"Password reset token generated for: {request_data.email}")
    
    # Send password reset email via AWS SES
    user_name = user.get("full_name", "User")
    email_sent = await email_service.send_password_reset_email(
        to_email=request_data.email,
        reset_token=reset_token,
        user_name=user_name
    )
    
    if not email_sent:
        logger.warning(f"Failed to send password reset email to: {request_data.email}")
    
    return {
        "message": "If an account with that email exists, a password reset link has been sent.",
        "status": "sent"
    }

@router.post("/password/reset-confirm")
async def confirm_password_reset(reset_data: PasswordResetConfirm):
    """
    Confirm password reset with token and new password
    """
    db = get_db()
    
    # Hash the provided token
    token_hash = hashlib.sha256(reset_data.token.encode()).hexdigest()
    
    # Find user with this token
    user = await db.users.find_one({
        "reset_token_hash": token_hash,
        "reset_token_expiry": {"$gt": datetime.utcnow()}
    })
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    # Validate new password
    if len(reset_data.new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long"
        )
    
    # Update password and clear reset token
    new_hash = get_password_hash(reset_data.new_password)
    await db.users.update_one(
        {"id": user["id"]},
        {
            "$set": {"hashed_password": new_hash},
            "$unset": {"reset_token_hash": "", "reset_token_expiry": ""}
        }
    )
    
    logger.info(f"Password reset completed for user: {user['email']}")
    
    return {
        "message": "Password has been reset successfully",
        "status": "success"
    }

@router.post("/password/change")
async def change_password(
    current_password: str,
    new_password: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Change password for authenticated user
    """
    db = get_db()
    
    # Verify current password
    if not verify_password(current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect"
        )
    
    # Validate new password
    if len(new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long"
        )
    
    # Update password
    new_hash = get_password_hash(new_password)
    await db.users.update_one(
        {"id": current_user.id},
        {"$set": {"hashed_password": new_hash}}
    )
    
    logger.info(f"Password changed for user: {current_user.email}")
    
    return {
        "message": "Password changed successfully",
        "status": "success"
    }
