"""
Models do SQLAlchemy
Aqui ficarão os models do banco de dados
"""
from app.models.user import User, UserRole
from app.models.auth_token import AuthToken

__all__ = ["User", "UserRole", "AuthToken"]
