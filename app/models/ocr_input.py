"""
Model: OCR_Input
Para armazenar imagens e extração OCR dos pedidos manuscritos.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Numeric, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class OCRInput(Base):
    __tablename__ = "ocr_inputs"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    imagem_url = Column(String(500), nullable=False)
    texto_extraido = Column(Text, nullable=True)
    confianca = Column(Numeric(5, 2), nullable=True)  # 0.00 a 100.00
    cliente_id = Column(
        UUID(as_uuid=True),
        ForeignKey("clientes.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    data = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    # Relacionamentos
    cliente = relationship("Cliente", back_populates="ocr_inputs")

    def __repr__(self):
        return f"<OCRInput(id={self.id}, confianca={self.confianca})>"

