"""
Service de Autenticação
Lógica de negócio para autenticação
"""
from typing import Optional
from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.user import User
from app.repositories.user import UserRepository
from app.core.security import (
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
)
from app.core.redis import (
    save_refresh_token,
    verify_refresh_token,
    revoke_refresh_token,
)
from app.core.audit import AuditService
from app.schemas.auth import TokenResponse, RefreshTokenResponse
from app.schemas.user import UserLogin, UserRead


class AuthService:
    """Service para operações de autenticação"""

    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.audit = AuditService(db)

    def login(self, credentials: UserLogin, user_agent: Optional[str] = None, ip_address: Optional[str] = None) -> TokenResponse:
        """
        Autentica usuário e retorna tokens
        
        Args:
            credentials: Email e senha
            user_agent: User agent do navegador
            ip_address: IP de origem
        
        Returns:
            TokenResponse com access_token, refresh_token e user
        """
        email = credentials.email
        failure_reason = None
        
        try:
            # Busca usuário
            user = self.user_repo.get_active_by_email(email)
            if not user:
                failure_reason = "Usuário não encontrado"
                # Registrar tentativa de login falhada
                self.audit.log_login(
                    email=email,
                    success=False,
                    user_id=None,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    failure_reason=failure_reason
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Email ou senha incorretos"
                )
            
            # Verifica senha
            if not verify_password(credentials.password, user.hashed_password):
                failure_reason = "Senha incorreta"
                # Registrar tentativa de login falhada
                self.audit.log_login(
                    email=email,
                    success=False,
                    user_id=user.id,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    failure_reason=failure_reason
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Email ou senha incorretos"
                )
            
            # Gera tokens
            access_token = create_access_token(
                data={"sub": user.email, "user_id": str(user.id), "role": user.role.value}
            )
            refresh_token = create_refresh_token(
                data={"sub": user.email, "user_id": str(user.id)}
            )
            
            # Salva refresh token no Redis (whitelist)
            from app.core.config import settings
            expires_in_seconds = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
            save_refresh_token(str(user.id), refresh_token, expires_in_seconds)
            
            # Registrar tentativa de login bem-sucedida
            self.audit.log_login(
                email=email,
                success=True,
                user_id=user.id,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            # Retorna resposta
            return TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer",
                user=UserRead.model_validate(user)
            )
            
        except HTTPException:
            # Re-raise HTTPException (já registrado acima)
            raise
        except Exception as e:
            # Registrar erro inesperado
            failure_reason = f"Erro inesperado: {str(e)}"
            self.audit.log_login(
                email=email,
                success=False,
                user_id=None,
                ip_address=ip_address,
                user_agent=user_agent,
                failure_reason=failure_reason
            )
            raise

    def refresh_token(self, refresh_token: str) -> RefreshTokenResponse:
        """
        Gera novo access token a partir do refresh token
        
        Args:
            refresh_token: Token de refresh
        
        Returns:
            RefreshTokenResponse com novo access_token
        """
        # Decodifica refresh token
        payload = decode_refresh_token(refresh_token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token inválido"
            )
        
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token inválido"
            )
        
        # Verifica se refresh token está na whitelist (Redis)
        if not verify_refresh_token(user_id, refresh_token):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token revogado ou expirado"
            )
        
        # Busca usuário (user_id do payload é UUID string)
        from uuid import UUID
        try:
            user_uuid = UUID(user_id)
            user = self.user_repo.get(user_uuid)
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token inválido"
            )
        
        if not user or user.is_active != "Y":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário não encontrado ou inativo"
            )
        
        # Gera novo access token
        access_token = create_access_token(
            data={"sub": user.email, "user_id": str(user.id), "role": user.role.value}
        )
        
        return RefreshTokenResponse(
            access_token=access_token,
            token_type="bearer"
        )

    def logout(self, user_id: str, refresh_token: Optional[str] = None) -> bool:
        """
        Faz logout revogando refresh token
        
        Args:
            user_id: ID do usuário
            refresh_token: Token de refresh a ser revogado
        
        Returns:
            True se logout foi bem-sucedido
        """
        return revoke_refresh_token(user_id, refresh_token)

    def get_current_user_info(self, user: User) -> UserRead:
        """
        Retorna informações do usuário atual
        
        Args:
            user: Objeto User
        
        Returns:
            UserRead com informações do usuário
        """
        return UserRead.model_validate(user)

