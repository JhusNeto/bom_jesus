"""Repository para Pesagem"""
from typing import List
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.pesagem import Pesagem, StatusPesagem
from app.repositories.base import BaseRepository

class PesagemRepository(BaseRepository[Pesagem]):
    def __init__(self, db: Session):
        super().__init__(Pesagem, db)
    
    def get_by_cliente(self, cliente_id: UUID) -> List[Pesagem]:
        return self.db.query(Pesagem).filter(Pesagem.cliente_id == cliente_id).all()
    
    def get_by_status(self, status: StatusPesagem) -> List[Pesagem]:
        return self.db.query(Pesagem).filter(Pesagem.status == status).all()
