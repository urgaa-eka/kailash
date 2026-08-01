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
                "email": "you@example.com",
                "kailash_code": "<your-kailash-code>",
                "full_name": "Your Name",
                "password": "<your-password>"
            }
        }

class UserLogin(BaseModel):
    login_id: str
    password: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "login_id": "<your-kailash-code-or-email>",
                "password": "<your-password>"
            }
        }

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict

class TokenData(BaseModel):
    user_id: Optional[str] = None
    kailash_code: Optional[str] = None
