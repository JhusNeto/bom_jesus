"""Schemas Pydantic para LogOperacional"""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel
from app.models.log_operacional import TipoLog

class LogOperacionalBase(BaseModel):
    tipo: TipoLog
    usuario_id: Optional[UUID] = None
    referencia_id: Optional[UUID] = None
    data: datetime
    detalhes: Optional[str] = None

class LogOperacionalCreate(LogOperacionalBase):
    pass

class LogOperacionalRead(LogOperacionalBase):
    id: UUID
    created_at: datetime
    class Config:
        from_attributes = True
