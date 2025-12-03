"""
Model: EntregaCliente
Relacionamento rota → cliente.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class EntregaCliente(Base):
    __tablename__ = "entregas_cliente"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    rota_id = Column(
        UUID(as_uuid=True),
        ForeignKey("rotas.id", ondelete="CASCADE"),
        nullable=False,
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
    quantidade_caixas = Column(Integer, nullable=False)
    devolucao = Column(Boolean, default=False, nullable=False)
    horario = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    # Relacionamentos
    rota = relationship("Rota", back_populates="entregas")
    cliente = relationship("Cliente", back_populates="entregas")
    pedido = relationship("Pedido", back_populates="entregas")

    def __repr__(self):
        return f"<EntregaCliente(id={self.id}, rota_id={self.rota_id}, cliente_id={self.cliente_id})>"

