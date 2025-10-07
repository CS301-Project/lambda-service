"""
Data models for CRM User Management API
"""
from enum import Enum
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, validator


class UserRole(str, Enum):
    """User roles in the CRM system"""
    ADMIN = "admin"
    AGENT = "agent"


class UserResponse(BaseModel):
    """User response model"""
    username: str
    email: EmailStr
    role: UserRole
    enabled: bool = True
    
    class Config:
        use_enum_values = True