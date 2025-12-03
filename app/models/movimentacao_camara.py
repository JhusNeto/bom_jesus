"""
Model: MovimentacaoCamara
Tudo que entra e sai da câmara.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, Enum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from app.db.base import Base


class TipoMovimento(str, enum.Enum):
    ENTRADA = "entrada"
    SAIDA = "saida"


class MovimentacaoCamara(Base):
    __tablename__ = "movimentacoes_camara"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    camara_id = Column(
        UUID(as_uuid=True),
        ForeignKey("camaras.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    carga_id = Column(
        UUID(as_uuid=True),
        ForeignKey("cargas.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    data = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    tipo_movimento = Column(
        Enum(TipoMovimento),
        nullable=False,
        index=True,
    )
    quantidade_caixas = Column(Integer, nullable=False)
    observacao = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    # Relacionamentos
    camara = relationship("Camara", back_populates="movimentacoes")
    carga = relationship("Carga", back_populates="movimentacoes")

    def __repr__(self):
        return f"<MovimentacaoCamara(id={self.id}, tipo={self.tipo_movimento.value}, quantidade={self.quantidade_caixas})>"

