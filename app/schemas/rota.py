"""Schemas Pydantic para Rota"""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field
from app.models.rota import StatusRota

class RotaBase(BaseModel):
    motorista: Optional[str] = Field(None, max_length=255)
    veiculo: Optional[str] = Field(None, max_length=100)
    data: datetime
    horario_saida: Optional[datetime] = None
    status: StatusRota = StatusRota.PLANEJADA
    observacoes: Optional[str] = Field(None, max_length=500)

class RotaCreate(RotaBase):
    pass

class RotaUpdate(BaseModel):
    motorista: Optional[str] = Field(None, max_length=255)
    veiculo: Optional[str] = Field(None, max_length=100)
    data: Optional[datetime] = None
    horario_saida: Optional[datetime] = None
    status: Optional[StatusRota] = None
    observacoes: Optional[str] = Field(None, max_length=500)

class RotaRead(RotaBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True
