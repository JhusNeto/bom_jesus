"""Service para MovimentacaoCamara"""
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.repositories.movimentacao_camara import MovimentacaoCamaraRepository
from app.schemas.movimentacao_camara import MovimentacaoCamaraCreate, MovimentacaoCamaraUpdate
from app.models.movimentacao_camara import MovimentacaoCamara, TipoMovimento

class MovimentacaoCamaraService:
    def __init__(self, db: Session):
        self.repository = MovimentacaoCamaraRepository(db)
        self.db = db
    
    def _calcular_saldo_camara(self, camara_id: UUID) -> int:
        """
        Calcula o saldo atual de caixas na câmara.
        Retorna: saldo = entradas - saídas
        """
        movimentacoes = self.repository.get_by_camara(camara_id)
        
        total_entradas = sum(
            m.quantidade_caixas 
            for m in movimentacoes 
            if m.tipo_movimento == TipoMovimento.ENTRADA
        )
        
        total_saidas = sum(
            m.quantidade_caixas 
            for m in movimentacoes 
            if m.tipo_movimento == TipoMovimento.SAIDA
        )
        
        return total_entradas - total_saidas
    
    def create(self, movimentacao: MovimentacaoCamaraCreate) -> MovimentacaoCamara:
        """
        Cria uma movimentação com validação de saldo para saídas.
        """
        # Se for saída, valida saldo disponível
        if movimentacao.tipo_movimento == TipoMovimento.SAIDA:
            saldo_atual = self._calcular_saldo_camara(movimentacao.camara_id)
            
            if saldo_atual < movimentacao.quantidade_caixas:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"Saldo insuficiente na câmara. "
                        f"Saldo disponível: {saldo_atual} caixas, "
                        f"Tentativa de saída: {movimentacao.quantidade_caixas} caixas"
                    )
                )
        
        return self.repository.create(movimentacao.dict())
    
    def get(self, id: UUID) -> Optional[MovimentacaoCamara]:
        return self.repository.get(id)
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[MovimentacaoCamara]:
        return self.repository.get_all(skip, limit)
    
    def get_by_camara(self, camara_id: UUID) -> List[MovimentacaoCamara]:
        return self.repository.get_by_camara(camara_id)
    
    def get_saldo_camara(self, camara_id: UUID) -> int:
        """
        Retorna o saldo atual de caixas na câmara.
        """
        return self._calcular_saldo_camara(camara_id)
    
    def update(self, id: UUID, movimentacao: MovimentacaoCamaraUpdate) -> Optional[MovimentacaoCamara]:
        update_data = movimentacao.dict(exclude_unset=True)
        
        # Se estiver atualizando para saída, valida saldo
        if "tipo_movimento" in update_data and update_data["tipo_movimento"] == TipoMovimento.SAIDA:
            movimentacao_existente = self.repository.get(id)
            if movimentacao_existente:
                camara_id = update_data.get("camara_id", movimentacao_existente.camara_id)
                quantidade = update_data.get("quantidade_caixas", movimentacao_existente.quantidade_caixas)
                
                # Recalcula saldo excluindo a movimentação atual
                saldo_atual = self._calcular_saldo_camara(camara_id)
                
                # Se a movimentação atual era entrada, adiciona de volta ao saldo
                if movimentacao_existente.tipo_movimento == TipoMovimento.ENTRADA:
                    saldo_atual += movimentacao_existente.quantidade_caixas
                # Se era saída, subtrai de volta (adiciona ao saldo)
                elif movimentacao_existente.tipo_movimento == TipoMovimento.SAIDA:
                    saldo_atual += movimentacao_existente.quantidade_caixas
                
                if saldo_atual < quantidade:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=(
                            f"Saldo insuficiente na câmara. "
                            f"Saldo disponível: {saldo_atual} caixas, "
                            f"Tentativa de saída: {quantidade} caixas"
                        )
                    )
        
        return self.repository.update(id, update_data)
    
    def delete(self, id: UUID) -> bool:
        return self.repository.delete(id)

