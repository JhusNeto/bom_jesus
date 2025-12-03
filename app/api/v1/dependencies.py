"""
Dependências comuns para os routers da API v1
"""
from fastapi import Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.security import get_current_user

# Dependências reutilizáveis
def get_database() -> Session:
    """Dependência para obter sessão do banco"""
    return Depends(get_db)


def get_authenticated_user():
    """Dependência para obter usuário autenticado"""
    return Depends(get_current_user)

