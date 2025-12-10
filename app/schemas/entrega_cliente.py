"""Schemas Pydantic para EntregaCliente"""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field
from app.models.entrega_cliente import StatusEntrega

class EntregaClienteBase(BaseModel):
    rota_id: UUID
    cliente_id: UUID
    pedido_id: Optional[UUID] = None
    carga_id: Optional[UUID] = None
    quantidade_caixas: int = Field(..., ge=0)
    devolucao: bool = False
    status_entrega: StatusEntrega = StatusEntrega.PENDENTE
    horario: Optional[datetime] = None

class EntregaClienteCreate(EntregaClienteBase):
    pass

class EntregaClienteUpdate(BaseModel):
    rota_id: Optional[UUID] = None
    cliente_id: Optional[UUID] = None
    pedido_id: Optional[UUID] = None
    carga_id: Optional[UUID] = None
    quantidade_caixas: Optional[int] = Field(None, ge=0)
    devolucao: Optional[bool] = None
    status_entrega: Optional[StatusEntrega] = None
    horario: Optional[datetime] = None

class EntregaClienteRead(EntregaClienteBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True
