"""
Schemas Pydantic para Cliente
"""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field

from app.models.cliente import TipoCliente


# Base
class ClienteBase(BaseModel):
    nome: str = Field(..., max_length=255)
    tipo: TipoCliente
    cidade: Optional[str] = Field(None, max_length=100)
    bairro: Optional[str] = Field(None, max_length=100)
    endereco: Optional[str] = Field(None, max_length=255)
    telefone: Optional[str] = Field(None, max_length=20)
    ativo: bool = True


# Create
class ClienteCreate(ClienteBase):
    pass


# Update
class ClienteUpdate(BaseModel):
    nome: Optional[str] = Field(None, max_length=255)
    tipo: Optional[TipoCliente] = None
    cidade: Optional[str] = Field(None, max_length=100)
    bairro: Optional[str] = Field(None, max_length=100)
    endereco: Optional[str] = Field(None, max_length=255)
    telefone: Optional[str] = Field(None, max_length=20)
    ativo: Optional[bool] = None


# Read
class ClienteRead(ClienteBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

