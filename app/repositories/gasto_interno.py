"""Repository para GastoInterno"""
from typing import List
from sqlalchemy.orm import Session
from app.models.gasto_interno import GastoInterno, TipoGasto
from app.repositories.base import BaseRepository

class GastoInternoRepository(BaseRepository[GastoInterno]):
    def __init__(self, db: Session):
        super().__init__(GastoInterno, db)
    
    def get_by_tipo(self, tipo: TipoGasto) -> List[GastoInterno]:
        return self.db.query(GastoInterno).filter(GastoInterno.tipo == tipo).all()
