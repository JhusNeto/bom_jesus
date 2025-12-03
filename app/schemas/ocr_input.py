"""Schemas Pydantic para OCRInput"""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field
from decimal import Decimal

class OCRInputBase(BaseModel):
    imagem_url: str = Field(..., max_length=500)
    texto_extraido: Optional[str] = None
    confianca: Optional[Decimal] = Field(None, ge=0, le=100)
    cliente_id: Optional[UUID] = None
    data: datetime

class OCRInputCreate(OCRInputBase):
    pass

class OCRInputUpdate(BaseModel):
    imagem_url: Optional[str] = Field(None, max_length=500)
    texto_extraido: Optional[str] = None
    confianca: Optional[Decimal] = Field(None, ge=0, le=100)
    cliente_id: Optional[UUID] = None
    data: Optional[datetime] = None

class OCRInputRead(OCRInputBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True
