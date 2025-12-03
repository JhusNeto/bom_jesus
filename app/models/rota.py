"""
Model: Rota
Prepara estrutura para o módulo de rota do Derson.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from app.db.base import Base


class StatusRota(str, enum.Enum):
    PLANEJADA = "planejada"
    EM_ANDAMENTO = "em_andamento"
    CONCLUIDA = "concluida"
    CANCELADA = "cancelada"


class Rota(Base):
    __tablename__ = "rotas"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    motorista = Column(String(255), nullable=True)
    veiculo = Column(String(100), nullable=True)
    data = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    status = Column(
        Enum(StatusRota),
        nullable=False,
        default=StatusRota.PLANEJADA,
        index=True,
    )
    observacoes = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    # Relacionamentos
    entregas = relationship("EntregaCliente", back_populates="rota", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Rota(id={self.id}, motorista={self.motorista}, status={self.status.value})>"

