"""Service para Carga"""
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from app.repositories.carga import CargaRepository
from app.schemas.carga import CargaCreate, CargaUpdate
from app.models.carga import Carga
from app.core.audit import AuditService

class CargaService:
    def __init__(self, db: Session, user_id: Optional[UUID] = None):
        self.repository = CargaRepository(db)
        self.audit = AuditService(db)
        self.user_id = user_id
    
    def create(self, carga: CargaCreate) -> Carga:
        carga_data = carga.dict()
        result = self.repository.create(carga_data)
        
        # Registrar auditoria
        self.audit.log_create(
            entity_type="Carga",
            entity_id=result.id,
            user_id=self.user_id,
            data=carga_data
        )
        
        return result
    
    def get(self, id: UUID) -> Optional[Carga]:
        return self.repository.get(id)
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Carga]:
        return self.repository.get_all(skip, limit)
    
    def update(self, id: UUID, carga: CargaUpdate) -> Optional[Carga]:
        # Buscar dados antigos para auditoria
        old_carga = self.repository.get(id)
        old_data = None
        if old_carga:
            old_data = {
                "fornecedor": old_carga.fornecedor,
                "tipo_banana": old_carga.tipo_banana.value if old_carga.tipo_banana else None,
                "quantidade_caixas": old_carga.quantidade_caixas,
                "preco_compra": float(old_carga.preco_compra) if old_carga.preco_compra else None,
                "status": old_carga.status.value if old_carga.status else None,
            }
        
        update_data = carga.dict(exclude_unset=True)
        result = self.repository.update(id, update_data)
        
        if result:
            # Registrar auditoria
            new_data = {
                "fornecedor": result.fornecedor,
                "tipo_banana": result.tipo_banana.value if result.tipo_banana else None,
                "quantidade_caixas": result.quantidade_caixas,
                "preco_compra": float(result.preco_compra) if result.preco_compra else None,
                "status": result.status.value if result.status else None,
            }
            
            self.audit.log_update(
                entity_type="Carga",
                entity_id=result.id,
                user_id=self.user_id,
                old_data=old_data,
                new_data=new_data
            )
        
        return result
    
    def delete(self, id: UUID) -> bool:
        # Buscar dados antes de deletar para auditoria
        carga = self.repository.get(id)
        carga_data = None
        if carga:
            carga_data = {
                "fornecedor": carga.fornecedor,
                "tipo_banana": carga.tipo_banana.value if carga.tipo_banana else None,
                "quantidade_caixas": carga.quantidade_caixas,
            }
        
        result = self.repository.delete(id)
        
        if result and carga:
            # Registrar auditoria
            self.audit.log_delete(
                entity_type="Carga",
                entity_id=id,
                user_id=self.user_id,
                data=carga_data
            )
        
        return result
    
    def get_em_estoque(self) -> List[Carga]:
        return self.repository.get_em_estoque()
