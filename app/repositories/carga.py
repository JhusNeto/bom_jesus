"""
Repository para Carga
"""
from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.carga import Carga, StatusCarga, TipoBanana
from app.repositories.base import BaseRepository


class CargaRepository(BaseRepository[Carga]):
    """Repository para operações com Cargas"""

    def __init__(self, db: Session):
        super().__init__(Carga, db)

    def get_by_status(self, status: StatusCarga, skip: int = 0, limit: int = 100) -> List[Carga]:
        """Buscar cargas por status"""
        return self.db.query(Carga).filter(
            Carga.status == status
        ).offset(skip).limit(limit).all()

    def get_by_tipo_banana(self, tipo: TipoBanana, skip: int = 0, limit: int = 100) -> List[Carga]:
        """Buscar cargas por tipo de banana"""
        return self.db.query(Carga).filter(
            Carga.tipo_banana == tipo
        ).offset(skip).limit(limit).all()

    def get_em_estoque(self, skip: int = 0, limit: int = 100) -> List[Carga]:
        """Buscar apenas cargas em estoque"""
        return self.get_by_status(StatusCarga.EM_ESTOQUE, skip, limit)

