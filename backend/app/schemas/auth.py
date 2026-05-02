from pydantic import BaseModel, EmailStr
from typing import Optional

class UserRegister(BaseModel):
    email: EmailStr
    kailash_code: str
    full_name: str
    password: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "vivek@Kailash.com",
                "kailash_code": "<REDACTED_kailash_code>",
                "full_name": "Vivek Kumar",
                "password": "<REDACTED_PASSWORD>"
            }
        }

class UserLogin(BaseModel):
    login_id: str
    password: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "login_id": "KAILASH001",
                "password": "Kailash@2026"
            }
        }

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict

class TokenData(BaseModel):
    user_id: Optional[str] = None
    kailash_code: Optional[str] = None
