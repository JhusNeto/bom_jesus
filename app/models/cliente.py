"""
Model: Cliente
Mercados, CEASA, Veneza, Açaí, etc.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from app.db.base import Base


class TipoCliente(str, enum.Enum):
    CEASA = "ceasa"
    MERCADO = "mercado"
    ATACADO = "atacado"
    SACOLAO = "sacolao"
    OUTRO = "outro"


class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    nome = Column(String(255), nullable=False, index=True)
    tipo = Column(
        Enum(TipoCliente),
        nullable=False,
        default=TipoCliente.OUTRO,
        index=True,
    )
    cidade = Column(String(100), nullable=True)
    bairro = Column(String(100), nullable=True)
    endereco = Column(String(255), nullable=True)
    telefone = Column(String(20), nullable=True)
    ativo = Column(Boolean, default=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    # Relacionamentos
    pedidos = relationship("Pedido", back_populates="cliente", cascade="all, delete-orphan")
    pesagens = relationship("Pesagem", back_populates="cliente", cascade="all, delete-orphan")
    devolucoes = relationship("Devolucao", back_populates="cliente", cascade="all, delete-orphan")
    entregas = relationship("EntregaCliente", back_populates="cliente", cascade="all, delete-orphan")
    ocr_inputs = relationship("OCRInput", back_populates="cliente", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Cliente(id={self.id}, nome={self.nome}, tipo={self.tipo.value})>"

