"""
Model: EntregaCliente
Relacionamento rota → cliente.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Boolean, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from app.db.base import Base


class StatusEntrega(str, enum.Enum):
    """Status da entrega"""
    PENDENTE = "pendente"  # Ainda não saiu
    EM_TRANSITO = "em_transito"  # Caminhão saiu, em trânsito
    ENTREGUE = "entregue"  # Entregue ao cliente
    DEVOLVIDA = "devolvida"  # Devolvida (já tem campo devolucao, mas status é mais específico)
    CANCELADA = "cancelada"  # Cancelada


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
    carga_id = Column(
        UUID(as_uuid=True),
        ForeignKey("cargas.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )  # Rastreamento: qual carga específica foi entregue
    quantidade_caixas = Column(Integer, nullable=False)
    devolucao = Column(Boolean, default=False, nullable=False)
    status_entrega = Column(
        Enum(StatusEntrega),
        nullable=False,
        default=StatusEntrega.PENDENTE,
        index=True,
    )  # Status da entrega em tempo real
    horario = Column(DateTime, nullable=True)  # Horário de entrega (quando status = ENTREGUE)
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
    carga = relationship("Carga", foreign_keys=[carga_id])

    def __repr__(self):
        return f"<EntregaCliente(id={self.id}, rota_id={self.rota_id}, cliente_id={self.cliente_id})>"

