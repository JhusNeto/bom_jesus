"""
Schemas Pydantic para User
"""
from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from app.models.user import UserRole


class UserBase(BaseModel):
    """Schema base para User"""
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    role: UserRole = UserRole.VIEWER


class UserCreate(UserBase):
    """Schema para criar User"""
    password: str = Field(..., min_length=6, max_length=100)


class UserUpdate(BaseModel):
    """Schema para atualizar User"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
    is_active: Optional[str] = Field(None, pattern="^[YN]$")


class UserRead(UserBase):
    """Schema para ler User (response)"""
    id: UUID
    is_active: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """Schema para login"""
    email: EmailStr
    password: str

