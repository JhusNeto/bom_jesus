"""Schemas Pydantic para Camara"""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field
from app.models.camara import StatusCamara

class CamaraBase(BaseModel):
    nome: str = Field(..., max_length=100)
    capacidade: int = Field(..., ge=0)
    status: StatusCamara = StatusCamara.DISPONIVEL

class CamaraCreate(CamaraBase):
    pass

class CamaraUpdate(BaseModel):
    nome: Optional[str] = Field(None, max_length=100)
    capacidade: Optional[int] = Field(None, ge=0)
    status: Optional[StatusCamara] = None

class CamaraRead(CamaraBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True
