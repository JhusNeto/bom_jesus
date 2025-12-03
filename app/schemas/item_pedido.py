"""
Schemas Pydantic para ItemPedido
"""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field
from decimal import Decimal

from app.models.carga import TipoBanana


# Base
class ItemPedidoBase(BaseModel):
    pedido_id: UUID
    tipo_banana: TipoBanana
    quantidade_caixas: int = Field(..., ge=0)
    preco_unitario: Decimal = Field(..., ge=0)
    preco_total: Decimal = Field(..., ge=0)


# Create
class ItemPedidoCreate(ItemPedidoBase):
    pass


# Update
class ItemPedidoUpdate(BaseModel):
    pedido_id: Optional[UUID] = None
    tipo_banana: Optional[TipoBanana] = None
    quantidade_caixas: Optional[int] = Field(None, ge=0)
    preco_unitario: Optional[Decimal] = Field(None, ge=0)
    preco_total: Optional[Decimal] = Field(None, ge=0)


# Read
class ItemPedidoRead(ItemPedidoBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

