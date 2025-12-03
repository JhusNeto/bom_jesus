"""Schemas Pydantic para Pesagem"""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field
from decimal import Decimal
from app.models.pesagem import StatusPesagem

class PesagemBase(BaseModel):
    data: datetime
    cliente_id: UUID
    carga_id: UUID
    quantidade_caixas: int = Field(..., ge=0)
    peso_total: Decimal = Field(..., ge=0)
    operador_id: Optional[UUID] = None
    status: StatusPesagem = StatusPesagem.PENDENTE

class PesagemCreate(PesagemBase):
    pass

class PesagemUpdate(BaseModel):
    data: Optional[datetime] = None
    cliente_id: Optional[UUID] = None
    carga_id: Optional[UUID] = None
    quantidade_caixas: Optional[int] = Field(None, ge=0)
    peso_total: Optional[Decimal] = Field(None, ge=0)
    operador_id: Optional[UUID] = None
    status: Optional[StatusPesagem] = None

class PesagemRead(PesagemBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True
