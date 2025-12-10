"""
Model: Carga
Representa uma entrada de frutas vinda de um fornecedor.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, Numeric, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from app.db.base import Base


class TipoBanana(str, enum.Enum):
    NANICA = "nanica"
    PRATA = "prata"
    MACA = "maca"
    OUTRA = "outra"


class StatusCarga(str, enum.Enum):
    EM_ESTOQUE = "em_estoque"
    ENCERRADA = "encerrada"


class EstadoMaturacao(str, enum.Enum):
    """Estado de maturação da fruta"""
    VERDE = "verde"
    DE_VEZ = "de_vez"
    MADURA = "madura"


class Carga(Base):
    __tablename__ = "cargas"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    data_chegada = Column(DateTime, nullable=False, default=datetime.utcnow)
    fornecedor = Column(String(255), nullable=False)
    fazenda = Column(String(255), nullable=True)
    tipo_banana = Column(
        Enum(TipoBanana),
        nullable=False,
        default=TipoBanana.NANICA,
        index=True,
    )
    qualidade_inicial = Column(String(50), nullable=True)  # A, B, C, etc.
    estado_maturacao = Column(
        Enum(EstadoMaturacao),
        nullable=True,
        index=True,
    )  # verde, de_vez, madura
    quantidade_caixas = Column(Integer, nullable=False, default=0)
    preco_compra = Column(Numeric(10, 2), nullable=False)
    status = Column(
        Enum(StatusCarga),
        nullable=False,
        default=StatusCarga.EM_ESTOQUE,
        index=True,
    )
    responsavel_recebimento_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )  # Quem conferiu/recebeu a carga
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    # Relacionamentos
    movimentacoes = relationship("MovimentacaoCamara", back_populates="carga", cascade="all, delete-orphan")
    pesagens = relationship("Pesagem", back_populates="carga", cascade="all, delete-orphan")
    perdas = relationship("Perda", back_populates="carga", cascade="all, delete-orphan")
    responsavel_recebimento = relationship("User", foreign_keys=[responsavel_recebimento_id])

    def __repr__(self):
        return f"<Carga(id={self.id}, fornecedor={self.fornecedor}, tipo={self.tipo_banana.value})>"

