"""Repository para Rota"""
from typing import List
from sqlalchemy.orm import Session
from app.models.rota import Rota, StatusRota
from app.repositories.base import BaseRepository

class RotaRepository(BaseRepository[Rota]):
    def __init__(self, db: Session):
        super().__init__(Rota, db)
    
    def get_by_status(self, status: StatusRota) -> List[Rota]:
        return self.db.query(Rota).filter(Rota.status == status).all()
