"""
Model: Pesagem
Cada operação de pesagem para separar caixas por cliente.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, Numeric, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from app.db.base import Base


class StatusPesagem(str, enum.Enum):
    PENDENTE = "pendente"
    CARREGADO = "carregado"
    ENVIADO = "enviado"


class Pesagem(Base):
    __tablename__ = "pesagens"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    data = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    cliente_id = Column(
        UUID(as_uuid=True),
        ForeignKey("clientes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    carga_id = Column(
        UUID(as_uuid=True),
        ForeignKey("cargas.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    quantidade_caixas = Column(Integer, nullable=False)
    peso_total = Column(Numeric(10, 2), nullable=False)  # Em kg
    operador_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    status = Column(
        Enum(StatusPesagem),
        nullable=False,
        default=StatusPesagem.PENDENTE,
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
    cliente = relationship("Cliente", back_populates="pesagens")
    carga = relationship("Carga", back_populates="pesagens")
    operador = relationship("User", foreign_keys=[operador_id])

    def __repr__(self):
        return f"<Pesagem(id={self.id}, cliente_id={self.cliente_id}, quantidade={self.quantidade_caixas})>"

