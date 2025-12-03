"""Schemas Pydantic para EntregaCliente"""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field

class EntregaClienteBase(BaseModel):
    rota_id: UUID
    cliente_id: UUID
    pedido_id: Optional[UUID] = None
    quantidade_caixas: int = Field(..., ge=0)
    devolucao: bool = False
    horario: Optional[datetime] = None

class EntregaClienteCreate(EntregaClienteBase):
    pass

class EntregaClienteUpdate(BaseModel):
    rota_id: Optional[UUID] = None
    cliente_id: Optional[UUID] = None
    pedido_id: Optional[UUID] = None
    quantidade_caixas: Optional[int] = Field(None, ge=0)
    devolucao: Optional[bool] = None
    horario: Optional[datetime] = None

class EntregaClienteRead(EntregaClienteBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True
