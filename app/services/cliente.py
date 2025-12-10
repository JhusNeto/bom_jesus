"""Service para Cliente"""
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from app.repositories.cliente import ClienteRepository
from app.schemas.cliente import ClienteCreate, ClienteUpdate
from app.models.cliente import Cliente
from app.core.audit import AuditService

class ClienteService:
    def __init__(self, db: Session, user_id: Optional[UUID] = None):
        self.repository = ClienteRepository(db)
        self.audit = AuditService(db)
        self.user_id = user_id
    
    def create(self, cliente: ClienteCreate) -> Cliente:
        cliente_data = cliente.dict()
        result = self.repository.create(cliente_data)
        
        # Registrar auditoria
        self.audit.log_create(
            entity_type="Cliente",
            entity_id=result.id,
            user_id=self.user_id,
            data=cliente_data
        )
        
        return result
    
    def get(self, id: UUID) -> Optional[Cliente]:
        return self.repository.get(id)
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Cliente]:
        return self.repository.get_all(skip, limit)
    
    def update(self, id: UUID, cliente: ClienteUpdate) -> Optional[Cliente]:
        # Buscar dados antigos para auditoria
        old_cliente = self.repository.get(id)
        old_data = None
        if old_cliente:
            old_data = {
                "nome": old_cliente.nome,
                "tipo": old_cliente.tipo.value if old_cliente.tipo else None,
                "ativo": old_cliente.ativo,
            }
        
        update_data = cliente.dict(exclude_unset=True)
        result = self.repository.update(id, update_data)
        
        if result:
            # Registrar auditoria
            new_data = {
                "nome": result.nome,
                "tipo": result.tipo.value if result.tipo else None,
                "ativo": result.ativo,
            }
            
            self.audit.log_update(
                entity_type="Cliente",
                entity_id=result.id,
                user_id=self.user_id,
                old_data=old_data,
                new_data=new_data
            )
        
        return result
    
    def delete(self, id: UUID) -> bool:
        # Buscar dados antes de deletar para auditoria
        cliente = self.repository.get(id)
        cliente_data = None
        if cliente:
            cliente_data = {
                "nome": cliente.nome,
                "tipo": cliente.tipo.value if cliente.tipo else None,
            }
        
        result = self.repository.delete(id)
        
        if result and cliente:
            # Registrar auditoria
            self.audit.log_delete(
                entity_type="Cliente",
                entity_id=id,
                user_id=self.user_id,
                data=cliente_data
            )
        
        return result
    
    def get_ativos(self) -> List[Cliente]:
        return self.repository.get_ativos()
    
    def search(self, nome: str) -> List[Cliente]:
        return self.repository.search_by_nome(nome)
