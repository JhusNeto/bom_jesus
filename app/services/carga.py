"""Service para Carga"""
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from app.repositories.carga import CargaRepository
from app.schemas.carga import CargaCreate, CargaUpdate
from app.models.carga import Carga

class CargaService:
    def __init__(self, db: Session):
        self.repository = CargaRepository(db)
    
    def create(self, carga: CargaCreate) -> Carga:
        return self.repository.create(carga.dict())
    
    def get(self, id: UUID) -> Optional[Carga]:
        return self.repository.get(id)
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Carga]:
        return self.repository.get_all(skip, limit)
    
    def update(self, id: UUID, carga: CargaUpdate) -> Optional[Carga]:
        update_data = carga.dict(exclude_unset=True)
        return self.repository.update(id, update_data)
    
    def delete(self, id: UUID) -> bool:
        return self.repository.delete(id)
    
    def get_em_estoque(self) -> List[Carga]:
        return self.repository.get_em_estoque()
