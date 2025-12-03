"""
Schemas Pydantic para Carga
"""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field
from decimal import Decimal

from app.models.carga import TipoBanana, StatusCarga


# Base
class CargaBase(BaseModel):
    data_chegada: datetime
    fornecedor: str = Field(..., max_length=255)
    fazenda: Optional[str] = Field(None, max_length=255)
    tipo_banana: TipoBanana
    qualidade_inicial: Optional[str] = Field(None, max_length=50)
    quantidade_caixas: int = Field(..., ge=0)
    preco_compra: Decimal = Field(..., ge=0)
    status: StatusCarga = StatusCarga.EM_ESTOQUE


# Create
class CargaCreate(CargaBase):
    pass


# Update
class CargaUpdate(BaseModel):
    data_chegada: Optional[datetime] = None
    fornecedor: Optional[str] = Field(None, max_length=255)
    fazenda: Optional[str] = Field(None, max_length=255)
    tipo_banana: Optional[TipoBanana] = None
    qualidade_inicial: Optional[str] = Field(None, max_length=50)
    quantidade_caixas: Optional[int] = Field(None, ge=0)
    preco_compra: Optional[Decimal] = Field(None, ge=0)
    status: Optional[StatusCarga] = None


# Read
class CargaRead(CargaBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

