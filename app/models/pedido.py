"""
Model: Pedido
O pedido feito pelo cliente (WhatsApp, telefone, manual, OCR).
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from app.db.base import Base


class OrigemPedido(str, enum.Enum):
    MANUAL = "manual"
    OCR = "ocr"
    WHATSAPP = "whatsapp"
    TELEFONE = "telefone"
    OUTRO = "outro"


class StatusPedido(str, enum.Enum):
    ABERTO = "aberto"
    SEPARADO = "separado"
    ENVIADO = "enviado"
    DEVOLUCAO = "devolucao"
    ENCERRADO = "encerrado"


class Pedido(Base):
    __tablename__ = "pedidos"

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
    origem_pedido = Column(
        Enum(OrigemPedido),
        nullable=False,
        default=OrigemPedido.MANUAL,
        index=True,
    )
    status = Column(
        Enum(StatusPedido),
        nullable=False,
        default=StatusPedido.ABERTO,
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
    cliente = relationship("Cliente", back_populates="pedidos")
    itens = relationship("ItemPedido", back_populates="pedido", cascade="all, delete-orphan")
    devolucoes = relationship("Devolucao", back_populates="pedido", cascade="all, delete-orphan")
    entregas = relationship("EntregaCliente", back_populates="pedido", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Pedido(id={self.id}, cliente_id={self.cliente_id}, status={self.status.value})>"

