"""
Model: Camara
Representa cada câmara fria física.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from app.db.base import Base


class StatusCamara(str, enum.Enum):
    DISPONIVEL = "disponivel"
    OCUPADA = "ocupada"
    MANUTENCAO = "manutencao"


class Camara(Base):
    __tablename__ = "camaras"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    nome = Column(String(100), nullable=False, unique=True, index=True)
    capacidade = Column(Integer, nullable=False)  # Capacidade em caixas
    status = Column(
        Enum(StatusCamara),
        nullable=False,
        default=StatusCamara.DISPONIVEL,
        index=True,
    )
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    # Relacionamentos
    movimentacoes = relationship("MovimentacaoCamara", back_populates="camara", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Camara(id={self.id}, nome={self.nome}, capacidade={self.capacidade})>"

