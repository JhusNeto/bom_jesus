"""
Router de autenticação
Endpoints para login, registro, etc.
"""
from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/login")
async def login():
    """
    Endpoint de login
    TODO: Implementar lógica de autenticação
    """
    return {"message": "Login endpoint - Em implementação"}


@router.post("/register")
async def register():
    """
    Endpoint de registro
    TODO: Implementar lógica de registro
    """
    return {"message": "Register endpoint - Em implementação"}


@router.post("/refresh")
async def refresh_token():
    """
    Endpoint para refresh token
    TODO: Implementar lógica de refresh token
    """
    return {"message": "Refresh token endpoint - Em implementação"}

