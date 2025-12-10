"""
Repository para User
"""
from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository para operações com User"""

    def __init__(self, db: Session):
        super().__init__(User, db)

    def get_by_email(self, email: str) -> Optional[User]:
        """Busca usuário por email"""
        return self.db.query(User).filter(User.email == email).first()

    def get_active_by_email(self, email: str) -> Optional[User]:
        """Busca usuário ativo por email"""
        return (
            self.db.query(User)
            .filter(User.email == email, User.is_active == "Y")
            .first()
        )

