"""
Model: Devolucao
Quando o cliente devolve caixas.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, Numeric, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class Devolucao(Base):
    __tablename__ = "devolucoes"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    cliente_id = Column(
        UUID(as_uuid=True),
        ForeignKey("clientes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    pedido_id = Column(
        UUID(as_uuid=True),
        ForeignKey("pedidos.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    data = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    quantidade_caixas = Column(Integer, nullable=False)
    motivo = Column(Text, nullable=False)
    valor_estornado = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    # Relacionamentos
    cliente = relationship("Cliente", back_populates="devolucoes")
    pedido = relationship("Pedido", back_populates="devolucoes")

    def __repr__(self):
        return f"<Devolucao(id={self.id}, cliente_id={self.cliente_id}, quantidade={self.quantidade_caixas})>"

