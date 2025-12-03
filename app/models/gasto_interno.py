"""
Model: GastoInterno
Para vale-transporte, gasolina, custo interno da operação.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Numeric, Enum, Text
from sqlalchemy.dialects.postgresql import UUID
import enum

from app.db.base import Base


class TipoGasto(str, enum.Enum):
    VALE_TRANSPORTE = "vale_transporte"
    GASOLINA = "gasolina"
    ADMINISTRATIVO = "administrativo"
    MANUTENCAO = "manutencao"
    OUTRO = "outro"


class GastoInterno(Base):
    __tablename__ = "gastos_internos"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    data = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    tipo = Column(
        Enum(TipoGasto),
        nullable=False,
        index=True,
    )
    valor = Column(Numeric(10, 2), nullable=False)
    descricao = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    def __repr__(self):
        return f"<GastoInterno(id={self.id}, tipo={self.tipo.value}, valor={self.valor})>"

