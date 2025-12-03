"""Schemas Pydantic para MovimentacaoCamara"""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field
from app.models.movimentacao_camara import TipoMovimento

class MovimentacaoCamaraBase(BaseModel):
    camara_id: UUID
    carga_id: Optional[UUID] = None
    data: datetime
    tipo_movimento: TipoMovimento
    quantidade_caixas: int = Field(..., ge=0)
    observacao: Optional[str] = None

class MovimentacaoCamaraCreate(MovimentacaoCamaraBase):
    pass

class MovimentacaoCamaraUpdate(BaseModel):
    camara_id: Optional[UUID] = None
    carga_id: Optional[UUID] = None
    data: Optional[datetime] = None
    tipo_movimento: Optional[TipoMovimento] = None
    quantidade_caixas: Optional[int] = Field(None, ge=0)
    observacao: Optional[str] = None

class MovimentacaoCamaraRead(MovimentacaoCamaraBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True
