"""Service para Pedido"""
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.repositories.pedido import PedidoRepository
from app.repositories.item_pedido import ItemPedidoRepository
from app.schemas.pedido import PedidoCreate, PedidoUpdate
from app.models.pedido import Pedido, StatusPedido
from app.core.audit import AuditService

class PedidoService:
    def __init__(self, db: Session, user_id: Optional[UUID] = None):
        self.repository = PedidoRepository(db)
        self.item_repository = ItemPedidoRepository(db)
        self.audit = AuditService(db)
        self.user_id = user_id
    
    def create(self, pedido: PedidoCreate) -> Pedido:
        pedido_data = pedido.dict()
        result = self.repository.create(pedido_data)
        
        # Registrar auditoria
        self.audit.log_create(
            entity_type="Pedido",
            entity_id=result.id,
            user_id=self.user_id,
            data=pedido_data
        )
        
        return result
    
    def validate_has_itens(self, pedido_id: UUID) -> bool:
        """
        Valida se o pedido tem itens.
        Levanta HTTPException se não tiver itens.
        """
        itens = self.item_repository.get_by_pedido(pedido_id)
        if not itens:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Pedido deve ter pelo menos um item"
            )
        return True
    
    def get(self, id: UUID) -> Optional[Pedido]:
        return self.repository.get(id)
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Pedido]:
        return self.repository.get_all(skip, limit)
    
    def update(self, id: UUID, pedido: PedidoUpdate) -> Optional[Pedido]:
        # Buscar dados antigos para auditoria
        old_pedido = self.repository.get(id)
        old_data = None
        if old_pedido:
            old_data = {
                "cliente_id": str(old_pedido.cliente_id) if old_pedido.cliente_id else None,
                "status": old_pedido.status.value if old_pedido.status else None,
                "origem_pedido": old_pedido.origem_pedido.value if old_pedido.origem_pedido else None,
            }
        
        update_data = pedido.dict(exclude_unset=True)
        result = self.repository.update(id, update_data)
        
        if result:
            # Registrar auditoria
            new_data = {
                "cliente_id": str(result.cliente_id) if result.cliente_id else None,
                "status": result.status.value if result.status else None,
                "origem_pedido": result.origem_pedido.value if result.origem_pedido else None,
            }
            
            self.audit.log_update(
                entity_type="Pedido",
                entity_id=result.id,
                user_id=self.user_id,
                old_data=old_data,
                new_data=new_data
            )
        
        return result
    
    def delete(self, id: UUID) -> bool:
        # Buscar dados antes de deletar para auditoria
        pedido = self.repository.get(id)
        pedido_data = None
        if pedido:
            pedido_data = {
                "cliente_id": str(pedido.cliente_id) if pedido.cliente_id else None,
                "status": pedido.status.value if pedido.status else None,
            }
        
        result = self.repository.delete(id)
        
        if result and pedido:
            # Registrar auditoria
            self.audit.log_delete(
                entity_type="Pedido",
                entity_id=id,
                user_id=self.user_id,
                data=pedido_data
            )
        
        return result
    
    def get_by_cliente(self, cliente_id: UUID) -> List[Pedido]:
        return self.repository.get_by_cliente(cliente_id)
    
    def update_status(self, id: UUID, status: StatusPedido) -> Optional[Pedido]:
        """
        Atualiza o status do pedido.
        Valida se o pedido tem itens antes de mudar para status que requer itens.
        """
        # Buscar dados antigos para auditoria
        old_pedido = self.repository.get(id)
        old_status = old_pedido.status.value if old_pedido and old_pedido.status else None
        
        # Status que requerem itens (não pode estar vazio)
        status_que_requerem_itens = [
            StatusPedido.SEPARADO,
            StatusPedido.ENVIADO,
            StatusPedido.ENCERRADO
        ]
        
        if status in status_que_requerem_itens:
            self.validate_has_itens(id)
        
        result = self.repository.update(id, {"status": status})
        
        if result:
            # Registrar auditoria de mudança de status
            self.audit.log_update(
                entity_type="Pedido",
                entity_id=result.id,
                user_id=self.user_id,
                old_data={"status": old_status},
                new_data={"status": status.value},
                details=f"Mudança de status: {old_status} → {status.value}"
            )
        
        return result
