"""Schemas Pydantic para Perda"""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field
from decimal import Decimal

class PerdaBase(BaseModel):
    carga_id: UUID
    data: datetime
    quantidade_caixas: int = Field(..., ge=0)
    motivo: str = Field(..., max_length=255)
    valor_estimado: Decimal = Field(..., ge=0)

class PerdaCreate(PerdaBase):
    pass

class PerdaUpdate(BaseModel):
    carga_id: Optional[UUID] = None
    data: Optional[datetime] = None
    quantidade_caixas: Optional[int] = Field(None, ge=0)
    motivo: Optional[str] = Field(None, max_length=255)
    valor_estimado: Optional[Decimal] = Field(None, ge=0)

class PerdaRead(PerdaBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True
