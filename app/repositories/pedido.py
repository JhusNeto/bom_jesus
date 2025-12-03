"""
Repository para Pedido
"""
from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.pedido import Pedido, StatusPedido, OrigemPedido
from app.repositories.base import BaseRepository


class PedidoRepository(BaseRepository[Pedido]):
    """Repository para operações com Pedidos"""

    def __init__(self, db: Session):
        super().__init__(Pedido, db)

    def get_by_cliente(self, cliente_id: UUID, skip: int = 0, limit: int = 100) -> List[Pedido]:
        """Buscar pedidos de um cliente"""
        return self.db.query(Pedido).filter(
            Pedido.cliente_id == cliente_id
        ).offset(skip).limit(limit).all()

    def get_by_status(self, status: StatusPedido, skip: int = 0, limit: int = 100) -> List[Pedido]:
        """Buscar pedidos por status"""
        return self.db.query(Pedido).filter(
            Pedido.status == status
        ).offset(skip).limit(limit).all()

    def get_by_origem(self, origem: OrigemPedido, skip: int = 0, limit: int = 100) -> List[Pedido]:
        """Buscar pedidos por origem"""
        return self.db.query(Pedido).filter(
            Pedido.origem_pedido == origem
        ).offset(skip).limit(limit).all()

