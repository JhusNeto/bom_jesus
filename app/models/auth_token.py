"""
Model AuthToken - Representa tokens de autenticação
"""
import uuid
from datetime import datetime, timedelta
from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class AuthToken(Base):
    """Model de Token de Autenticação"""
    __tablename__ = "auth_tokens"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    token = Column(String(500), unique=True, index=True, nullable=False)
    token_type = Column(String(50), default="bearer", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_used_at = Column(DateTime, nullable=True)
    user_agent = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)

    # Relationships
    user = relationship("User", back_populates="auth_tokens")

    def is_expired(self) -> bool:
        """Verifica se o token está expirado"""
        return datetime.utcnow() > self.expires_at

    def __repr__(self):
        return f"<AuthToken(id={self.id}, user_id={self.user_id}, is_active={self.is_active})>"

