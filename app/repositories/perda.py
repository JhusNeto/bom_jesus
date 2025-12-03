"""Repository para Perda"""
from typing import List
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.perda import Perda
from app.repositories.base import BaseRepository

class PerdaRepository(BaseRepository[Perda]):
    def __init__(self, db: Session):
        super().__init__(Perda, db)
    
    def get_by_carga(self, carga_id: UUID) -> List[Perda]:
        return self.db.query(Perda).filter(Perda.carga_id == carga_id).all()
