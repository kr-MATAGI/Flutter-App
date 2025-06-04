from typing import List, Dict, Any, Optional
from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    access_token: str
    token_type: str

    class Config:
        schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
            }
        }


class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str

    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "username": "johndoe",
                "password": "strongpassword123",
            }
        }


class RequestBase(BaseModel):
    user_id: Optional[str] = None
    store_name: Optional[str] = None
