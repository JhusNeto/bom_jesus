"""Repository para OCRInput"""
from typing import List
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.ocr_input import OCRInput
from app.repositories.base import BaseRepository

class OCRInputRepository(BaseRepository[OCRInput]):
    def __init__(self, db: Session):
        super().__init__(OCRInput, db)
    
    def get_by_cliente(self, cliente_id: UUID) -> List[OCRInput]:
        return self.db.query(OCRInput).filter(OCRInput.cliente_id == cliente_id).all()
