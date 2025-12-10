"""
Dependências comuns para os routers da API v1
"""
from typing import Optional
from uuid import UUID
from fastapi import Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.security import get_current_user
from app.models.user import User

# Dependências reutilizáveis
def get_database() -> Session:
    """Dependência para obter sessão do banco"""
    return Depends(get_db)


def get_authenticated_user():
    """Dependência para obter usuário autenticado"""
    return Depends(get_current_user)


def get_user_id(current_user: User = Depends(get_current_user)) -> Optional[UUID]:
    """
    Dependência para obter apenas o ID do usuário autenticado.
    Útil para passar para services que precisam do user_id para auditoria.
    """
    return current_user.id if current_user else None
