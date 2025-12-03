"""
Model: Perda
Quando a fruta estraga, amolece, ou é separada.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class Perda(Base):
    __tablename__ = "perdas"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    carga_id = Column(
        UUID(as_uuid=True),
        ForeignKey("cargas.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    data = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    quantidade_caixas = Column(Integer, nullable=False)
    motivo = Column(String(255), nullable=False)  # passou, madura, machucada, etc.
    valor_estimado = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    # Relacionamentos
    carga = relationship("Carga", back_populates="perdas")

    def __repr__(self):
        return f"<Perda(id={self.id}, carga_id={self.carga_id}, quantidade={self.quantidade_caixas})>"

