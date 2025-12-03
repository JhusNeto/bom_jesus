"""Service para Pesagem"""
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from app.repositories.pesagem import PesagemRepository
from app.schemas.pesagem import PesagemCreate, PesagemUpdate
from app.models.pesagem import Pesagem

class PesagemService:
    def __init__(self, db: Session):
        self.repository = PesagemRepository(db)
    
    def create(self, pesagem: PesagemCreate) -> Pesagem:
        return self.repository.create(pesagem.dict())
    
    def get(self, id: UUID) -> Optional[Pesagem]:
        return self.repository.get(id)
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Pesagem]:
        return self.repository.get_all(skip, limit)
    
    def update(self, id: UUID, pesagem: PesagemUpdate) -> Optional[Pesagem]:
        update_data = pesagem.dict(exclude_unset=True)
        return self.repository.update(id, update_data)
    
    def delete(self, id: UUID) -> bool:
        return self.repository.delete(id)
