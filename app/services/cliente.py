"""Service para Cliente"""
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from app.repositories.cliente import ClienteRepository
from app.schemas.cliente import ClienteCreate, ClienteUpdate
from app.models.cliente import Cliente

class ClienteService:
    def __init__(self, db: Session):
        self.repository = ClienteRepository(db)
    
    def create(self, cliente: ClienteCreate) -> Cliente:
        return self.repository.create(cliente.dict())
    
    def get(self, id: UUID) -> Optional[Cliente]:
        return self.repository.get(id)
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Cliente]:
        return self.repository.get_all(skip, limit)
    
    def update(self, id: UUID, cliente: ClienteUpdate) -> Optional[Cliente]:
        update_data = cliente.dict(exclude_unset=True)
        return self.repository.update(id, update_data)
    
    def delete(self, id: UUID) -> bool:
        return self.repository.delete(id)
    
    def get_ativos(self) -> List[Cliente]:
        return self.repository.get_ativos()
    
    def search(self, nome: str) -> List[Cliente]:
        return self.repository.search_by_nome(nome)
