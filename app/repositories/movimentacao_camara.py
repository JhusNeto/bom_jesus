"""Repository para MovimentacaoCamara"""
from typing import List
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.movimentacao_camara import MovimentacaoCamara, TipoMovimento
from app.repositories.base import BaseRepository

class MovimentacaoCamaraRepository(BaseRepository[MovimentacaoCamara]):
    def __init__(self, db: Session):
        super().__init__(MovimentacaoCamara, db)
    
    def get_by_camara(self, camara_id: UUID) -> List[MovimentacaoCamara]:
        return self.db.query(MovimentacaoCamara).filter(
            MovimentacaoCamara.camara_id == camara_id
        ).all()
    
    def get_by_tipo(self, tipo: TipoMovimento) -> List[MovimentacaoCamara]:
        return self.db.query(MovimentacaoCamara).filter(
            MovimentacaoCamara.tipo_movimento == tipo
        ).all()
