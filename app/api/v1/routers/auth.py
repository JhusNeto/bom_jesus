"""
Router de autenticação
Endpoints para login, refresh, logout, me
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.security import get_current_user, requires_role
from app.services.auth_service import AuthService
from app.schemas.auth import TokenResponse, RefreshTokenRequest, RefreshTokenResponse
from app.schemas.user import UserLogin, UserRead
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def login(
    credentials: UserLogin,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Endpoint de login
    
    Autentica usuário com email e senha, retorna access token e refresh token.
    
    - **Access Token**: Expira em 10 minutos
    - **Refresh Token**: Expira em 7 dias, salvo no Redis (whitelist)
    """
    auth_service = AuthService(db)
    
    # Obtém user agent e IP
    user_agent = request.headers.get("user-agent")
    ip_address = request.client.host if request.client else None
    
    return auth_service.login(credentials, user_agent, ip_address)


@router.post("/refresh", response_model=RefreshTokenResponse, status_code=status.HTTP_200_OK)
async def refresh_token(
    refresh_request: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Endpoint para refresh token
    
    Gera novo access token a partir do refresh token.
    O refresh token deve estar válido no Redis (whitelist).
    """
    auth_service = AuthService(db)
    return auth_service.refresh_token(refresh_request.refresh_token)


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    refresh_request: RefreshTokenRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Endpoint de logout
    
    Revoga o refresh token, removendo-o da whitelist no Redis.
    Se refresh_token não for fornecido, revoga todos os tokens do usuário.
    """
    auth_service = AuthService(db)
    if refresh_request.refresh_token:
        auth_service.logout(str(current_user.id), refresh_request.refresh_token)
    else:
        # Se não forneceu refresh token, revoga todos
        from app.core.redis import revoke_all_refresh_tokens
        revoke_all_refresh_tokens(str(current_user.id))
    return {"message": "Logout realizado com sucesso"}


@router.get("/me", response_model=UserRead, status_code=status.HTTP_200_OK)
async def get_me(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Endpoint para obter informações do usuário atual
    
    Retorna dados do usuário autenticado.
    """
    auth_service = AuthService(db)
    return auth_service.get_current_user_info(current_user)


@router.get("/admin-only", status_code=status.HTTP_200_OK)
@requires_role(["ADMIN"])
async def admin_only_endpoint(
    current_user: User = Depends(get_current_user)
):
    """
    Endpoint de exemplo que requer role ADMIN
    
    Demonstra o funcionamento do sistema de roles.
    Apenas usuários com role ADMIN podem acessar este endpoint.
    """
    return {
        "message": "Acesso permitido - Você é um administrador",
        "user": {
            "email": current_user.email,
            "name": current_user.name,
            "role": current_user.role.value
        },
        "note": "Este é um endpoint de exemplo para demonstrar o sistema de roles"
    }


@router.get("/manager-or-admin", status_code=status.HTTP_200_OK)
@requires_role(["ADMIN", "MANAGER"])
async def manager_or_admin_endpoint(
    current_user: User = Depends(get_current_user)
):
    """
    Endpoint de exemplo que requer role ADMIN ou MANAGER
    
    Demonstra o funcionamento do sistema de roles com múltiplas roles permitidas.
    Usuários com role ADMIN ou MANAGER podem acessar este endpoint.
    """
    return {
        "message": "Acesso permitido - Você é um administrador ou gerente",
        "user": {
            "email": current_user.email,
            "name": current_user.name,
            "role": current_user.role.value
        },
        "note": "Este é um endpoint de exemplo para demonstrar o sistema de roles"
    }
