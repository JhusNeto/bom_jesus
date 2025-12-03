"""Repository para EntregaCliente"""
from typing import List
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.entrega_cliente import EntregaCliente
from app.repositories.base import BaseRepository

class EntregaClienteRepository(BaseRepository[EntregaCliente]):
    def __init__(self, db: Session):
        super().__init__(EntregaCliente, db)
    
    def get_by_rota(self, rota_id: UUID) -> List[EntregaCliente]:
        return self.db.query(EntregaCliente).filter(EntregaCliente.rota_id == rota_id).all()
    
    def get_by_cliente(self, cliente_id: UUID) -> List[EntregaCliente]:
        return self.db.query(EntregaCliente).filter(EntregaCliente.cliente_id == cliente_id).all()
