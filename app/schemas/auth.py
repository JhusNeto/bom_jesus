"""
Schemas Pydantic para Autenticação
"""
from pydantic import BaseModel
from app.schemas.user import UserRead


class TokenResponse(BaseModel):
    """Response com tokens de autenticação"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserRead


class RefreshTokenRequest(BaseModel):
    """Request para refresh token"""
    refresh_token: str


class RefreshTokenResponse(BaseModel):
    """Response do refresh token"""
    access_token: str
    token_type: str = "bearer"

