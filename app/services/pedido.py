"""Service para Pedido"""
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from app.repositories.pedido import PedidoRepository
from app.schemas.pedido import PedidoCreate, PedidoUpdate
from app.models.pedido import Pedido, StatusPedido

class PedidoService:
    def __init__(self, db: Session):
        self.repository = PedidoRepository(db)
    
    def create(self, pedido: PedidoCreate) -> Pedido:
        return self.repository.create(pedido.dict())
    
    def get(self, id: UUID) -> Optional[Pedido]:
        return self.repository.get(id)
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Pedido]:
        return self.repository.get_all(skip, limit)
    
    def update(self, id: UUID, pedido: PedidoUpdate) -> Optional[Pedido]:
        update_data = pedido.dict(exclude_unset=True)
        return self.repository.update(id, update_data)
    
    def delete(self, id: UUID) -> bool:
        return self.repository.delete(id)
    
    def get_by_cliente(self, cliente_id: UUID) -> List[Pedido]:
        return self.repository.get_by_cliente(cliente_id)
    
    def update_status(self, id: UUID, status: StatusPedido) -> Optional[Pedido]:
        return self.repository.update(id, {"status": status})
