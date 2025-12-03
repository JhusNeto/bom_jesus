"""
Repository para Cliente
"""
from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.cliente import Cliente, TipoCliente
from app.repositories.base import BaseRepository


class ClienteRepository(BaseRepository[Cliente]):
    """Repository para operações com Clientes"""

    def __init__(self, db: Session):
        super().__init__(Cliente, db)

    def get_by_tipo(self, tipo: TipoCliente, skip: int = 0, limit: int = 100) -> List[Cliente]:
        """Buscar clientes por tipo"""
        return self.db.query(Cliente).filter(
            Cliente.tipo == tipo
        ).offset(skip).limit(limit).all()

    def get_ativos(self, skip: int = 0, limit: int = 100) -> List[Cliente]:
        """Buscar apenas clientes ativos"""
        return self.db.query(Cliente).filter(
            Cliente.ativo == True
        ).offset(skip).limit(limit).all()

    def search_by_nome(self, nome: str, skip: int = 0, limit: int = 100) -> List[Cliente]:
        """Buscar clientes por nome (busca parcial)"""
        return self.db.query(Cliente).filter(
            Cliente.nome.ilike(f"%{nome}%")
        ).offset(skip).limit(limit).all()

