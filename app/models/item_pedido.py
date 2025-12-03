"""
Model: ItemPedido
Itens do pedido (cada tipo de banana/tipo de fruta).
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, Numeric, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.models.carga import TipoBanana


class ItemPedido(Base):
    __tablename__ = "itens_pedido"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    pedido_id = Column(
        UUID(as_uuid=True),
        ForeignKey("pedidos.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    tipo_banana = Column(
        Enum(TipoBanana),
        nullable=False,
        index=True,
    )
    quantidade_caixas = Column(Integer, nullable=False)
    preco_unitario = Column(Numeric(10, 2), nullable=False)
    preco_total = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    # Relacionamentos
    pedido = relationship("Pedido", back_populates="itens")

    def __repr__(self):
        return f"<ItemPedido(id={self.id}, pedido_id={self.pedido_id}, tipo={self.tipo_banana.value})>"

