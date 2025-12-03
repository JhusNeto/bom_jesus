"""Schemas Pydantic para Devolucao"""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field
from decimal import Decimal

class DevolucaoBase(BaseModel):
    cliente_id: UUID
    pedido_id: Optional[UUID] = None
    data: datetime
    quantidade_caixas: int = Field(..., ge=0)
    motivo: str
    valor_estornado: Decimal = Field(..., ge=0)

class DevolucaoCreate(DevolucaoBase):
    pass

class DevolucaoUpdate(BaseModel):
    cliente_id: Optional[UUID] = None
    pedido_id: Optional[UUID] = None
    data: Optional[datetime] = None
    quantidade_caixas: Optional[int] = Field(None, ge=0)
    motivo: Optional[str] = None
    valor_estornado: Optional[Decimal] = Field(None, ge=0)

class DevolucaoRead(DevolucaoBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True
