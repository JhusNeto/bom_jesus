"""
Schemas Pydantic para Pedido
"""
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field

from app.models.pedido import OrigemPedido, StatusPedido
from app.schemas.item_pedido import ItemPedidoRead


# Base
class PedidoBase(BaseModel):
    data: datetime
    cliente_id: UUID
    origem_pedido: OrigemPedido = OrigemPedido.MANUAL
    status: StatusPedido = StatusPedido.ABERTO
    observacoes: Optional[str] = Field(None, max_length=500)


# Create
class PedidoCreate(PedidoBase):
    pass


# Update
class PedidoUpdate(BaseModel):
    data: Optional[datetime] = None
    cliente_id: Optional[UUID] = None
    origem_pedido: Optional[OrigemPedido] = None
    status: Optional[StatusPedido] = None
    observacoes: Optional[str] = Field(None, max_length=500)


# Read
class PedidoRead(PedidoBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    itens: List[ItemPedidoRead] = []

    class Config:
        from_attributes = True

