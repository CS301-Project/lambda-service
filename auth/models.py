"""
Data models for CRM User Management API
"""
import re
from enum import Enum
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator


class UserRole(str, Enum):
    """User roles in the CRM system"""
    ADMIN = "admin"
    AGENT = "agent"


class UserResponse(BaseModel):
    """User response model"""
    email: EmailStr
    role: UserRole
    enabled: bool = True
    
    class Config:
        use_enum_values = True

class CreateUserRequest(BaseModel):
    """Request model for creating a new user"""
    email: EmailStr
    role: UserRole
    temporary_password: str = Field(..., min_length=8)
    
class CreateUserResponse(BaseModel):
    """Response model for successful user creation"""
    message: str
    user: UserResponse
    code: int