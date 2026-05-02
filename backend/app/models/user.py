from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
import uuid

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    kailash_code: str  # e.g., <REDACTED_kailash_code>
    full_name: str
    hashed_password: str
    is_active: bool = True
    is_admin: bool = False
    role: str = "viewer"  # Role for RAC
    
    # 2FA Fields
    totp_secret: Optional[str] = None
    is_2fa_enabled: bool = False
    backup_codes: List[str] = Field(default_factory=list)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@Kailash.com",
                "kailash_code": "<REDACTED_kailash_code>",
                "full_name": "Vivek Kumar",
                "is_active": True,
                "is_admin": False
            }
        }
