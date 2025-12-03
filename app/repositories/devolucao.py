"""Repository para Devolucao"""
from typing import List
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.devolucao import Devolucao
from app.repositories.base import BaseRepository

class DevolucaoRepository(BaseRepository[Devolucao]):
    def __init__(self, db: Session):
        super().__init__(Devolucao, db)
    
    def get_by_cliente(self, cliente_id: UUID) -> List[Devolucao]:
        return self.db.query(Devolucao).filter(Devolucao.cliente_id == cliente_id).all()
