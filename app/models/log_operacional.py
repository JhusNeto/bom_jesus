"""
Model: LogOperacional
Registro mínimo de auditoria e ações.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from app.db.base import Base


class TipoLog(str, enum.Enum):
    LOGIN = "login"
    PESAGEM = "pesagem"
    CARREGAMENTO = "carregamento"
    ATUALIZACAO = "atualizacao"
    DEVOLUCAO = "devolucao"
    MOVIMENTACAO = "movimentacao"
    OUTRO = "outro"


class LogOperacional(Base):
    __tablename__ = "logs_operacionais"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    tipo = Column(
        Enum(TipoLog),
        nullable=False,
        index=True,
    )
    usuario_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    referencia_id = Column(UUID(as_uuid=True), nullable=True, index=True)  # ID genérico da entidade relacionada
    data = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    detalhes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relacionamentos
    usuario = relationship("User", foreign_keys=[usuario_id])

    def __repr__(self):
        return f"<LogOperacional(id={self.id}, tipo={self.tipo.value}, usuario_id={self.usuario_id})>"

