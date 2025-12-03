"""Schemas Pydantic para GastoInterno"""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field
from decimal import Decimal
from app.models.gasto_interno import TipoGasto

class GastoInternoBase(BaseModel):
    data: datetime
    tipo: TipoGasto
    valor: Decimal = Field(..., ge=0)
    descricao: Optional[str] = None

class GastoInternoCreate(GastoInternoBase):
    pass

class GastoInternoUpdate(BaseModel):
    data: Optional[datetime] = None
    tipo: Optional[TipoGasto] = None
    valor: Optional[Decimal] = Field(None, ge=0)
    descricao: Optional[str] = None

class GastoInternoRead(GastoInternoBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True
