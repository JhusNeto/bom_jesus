"""
Sistema de Auditoria
Registra ações críticas (criação, edição, exclusão) para auditoria
"""
import json
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.log_operacional import LogOperacional, TipoLog
from app.repositories.log_operacional import LogOperacionalRepository
from app.core.logging import get_logger

logger = get_logger(__name__)


class AuditService:
    """Serviço para registrar ações de auditoria"""
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = LogOperacionalRepository(db)
    
    def log_create(
        self,
        entity_type: str,
        entity_id: UUID,
        user_id: Optional[UUID] = None,
        data: Optional[Dict[str, Any]] = None,
        details: Optional[str] = None
    ) -> LogOperacional:
        """
        Registra criação de uma entidade
        
        Args:
            entity_type: Tipo da entidade (ex: "Carga", "Pedido", "Cliente")
            entity_id: ID da entidade criada
            user_id: ID do usuário que realizou a ação
            data: Dados da entidade criada (opcional)
            details: Detalhes adicionais (opcional)
        """
        return self._log_action(
            action="CREATE",
            entity_type=entity_type,
            entity_id=entity_id,
            user_id=user_id,
            data=data,
            details=details
        )
    
    def log_update(
        self,
        entity_type: str,
        entity_id: UUID,
        user_id: Optional[UUID] = None,
        old_data: Optional[Dict[str, Any]] = None,
        new_data: Optional[Dict[str, Any]] = None,
        details: Optional[str] = None
    ) -> LogOperacional:
        """
        Registra atualização de uma entidade
        
        Args:
            entity_type: Tipo da entidade
            entity_id: ID da entidade atualizada
            user_id: ID do usuário que realizou a ação
            old_data: Dados antes da atualização (opcional)
            new_data: Dados após a atualização (opcional)
            details: Detalhes adicionais (opcional)
        """
        # Preparar dados de mudança
        change_data = {}
        if old_data and new_data:
            # Identificar campos alterados
            changed_fields = {}
            for key in set(old_data.keys()) | set(new_data.keys()):
                old_value = old_data.get(key)
                new_value = new_data.get(key)
                if old_value != new_value:
                    changed_fields[key] = {
                        "old": old_value,
                        "new": new_value
                    }
            if changed_fields:
                change_data["changed_fields"] = changed_fields
        
        return self._log_action(
            action="UPDATE",
            entity_type=entity_type,
            entity_id=entity_id,
            user_id=user_id,
            data=change_data if change_data else new_data,
            details=details
        )
    
    def log_delete(
        self,
        entity_type: str,
        entity_id: UUID,
        user_id: Optional[UUID] = None,
        data: Optional[Dict[str, Any]] = None,
        details: Optional[str] = None
    ) -> LogOperacional:
        """
        Registra exclusão de uma entidade
        
        Args:
            entity_type: Tipo da entidade
            entity_id: ID da entidade excluída
            user_id: ID do usuário que realizou a ação
            data: Dados da entidade excluída (opcional)
            details: Detalhes adicionais (opcional)
        """
        return self._log_action(
            action="DELETE",
            entity_type=entity_type,
            entity_id=entity_id,
            user_id=user_id,
            data=data,
            details=details
        )
    
    def log_error(
        self,
        error_type: str,
        error_message: str,
        stack_trace: Optional[str] = None,
        user_id: Optional[UUID] = None,
        request_path: Optional[str] = None,
        request_method: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[LogOperacional]:
        """
        Registra erro ou exceção no sistema
        
        Args:
            error_type: Tipo do erro (ex: "HTTPException", "ValueError", "DatabaseError")
            error_message: Mensagem do erro
            stack_trace: Stack trace completo (opcional)
            user_id: ID do usuário (se disponível)
            request_path: Path da requisição que causou o erro
            request_method: Método HTTP (GET, POST, etc.)
            ip_address: IP de origem
            user_agent: User agent do navegador
            context: Contexto adicional (opcional)
        """
        try:
            # Preparar detalhes do log
            log_details = {
                "action": "ERROR",
                "error_type": error_type,
                "error_message": error_message,
                "timestamp": datetime.utcnow().isoformat(),
            }
            
            if stack_trace:
                log_details["stack_trace"] = stack_trace
            
            if request_path:
                log_details["request_path"] = request_path
            if request_method:
                log_details["request_method"] = request_method
            if ip_address:
                log_details["ip_address"] = ip_address
            if user_agent:
                log_details["user_agent"] = user_agent[:200]  # Limitar tamanho
            
            if context:
                log_details["context"] = self._make_serializable(context)
            
            # Criar log com tipo OUTRO (erros não são ações operacionais específicas)
            log_data = {
                "tipo": TipoLog.OUTRO,
                "usuario_id": user_id,
                "referencia_id": None,  # Erros não têm referência específica
                "data": datetime.utcnow(),
                "detalhes": json.dumps(log_details, ensure_ascii=False, default=str)
            }
            
            log_entry = self.repository.create(log_data)
            
            # Log também no sistema de logging
            logger.error(
                f"ERRO REGISTRADO: {error_type} - {error_message} | "
                f"Path: {request_path or 'N/A'} | "
                f"User: {user_id or 'N/A'}"
            )
            
            return log_entry
            
        except Exception as e:
            # Não falhar se o log de erro falhar
            logger.error(f"Erro ao registrar log de erro: {e}", exc_info=True)
            return None
    
    def log_login(
        self,
        email: str,
        success: bool,
        user_id: Optional[UUID] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        failure_reason: Optional[str] = None
    ) -> LogOperacional:
        """
        Registra tentativa de login
        
        Args:
            email: Email usado na tentativa de login
            success: True se login foi bem-sucedido, False caso contrário
            user_id: ID do usuário (apenas se sucesso)
            ip_address: IP de origem da tentativa
            user_agent: User agent do navegador
            failure_reason: Motivo da falha (apenas se success=False)
        """
        try:
            # Preparar detalhes do log
            log_details = {
                "action": "LOGIN",
                "success": success,
                "email": email,
                "timestamp": datetime.utcnow().isoformat(),
            }
            
            if ip_address:
                log_details["ip_address"] = ip_address
            if user_agent:
                log_details["user_agent"] = user_agent[:200]  # Limitar tamanho
            
            if success:
                log_details["user_id"] = str(user_id) if user_id else None
            else:
                log_details["failure_reason"] = failure_reason or "Credenciais inválidas"
            
            # Criar log com tipo LOGIN
            log_data = {
                "tipo": TipoLog.LOGIN,
                "usuario_id": user_id if success else None,
                "referencia_id": user_id,  # Referência ao usuário (mesmo que None se falhou)
                "data": datetime.utcnow(),
                "detalhes": json.dumps(log_details, ensure_ascii=False, default=str)
            }
            
            log_entry = self.repository.create(log_data)
            
            # Log também no sistema de logging
            status_text = "SUCESSO" if success else "FALHA"
            logger.info(
                f"AUDIT LOGIN {status_text}: {email} "
                f"de {ip_address or 'IP desconhecido'} "
                f"({failure_reason or 'autenticado'})"
            )
            
            return log_entry
            
        except Exception as e:
            # Não falhar a operação principal se o log falhar
            logger.error(f"Erro ao registrar log de login: {e}", exc_info=True)
            return None
    
    def _log_action(
        self,
        action: str,
        entity_type: str,
        entity_id: UUID,
        user_id: Optional[UUID] = None,
        data: Optional[Dict[str, Any]] = None,
        details: Optional[str] = None
    ) -> LogOperacional:
        """
        Método interno para registrar ação de auditoria
        """
        try:
            # Preparar detalhes do log
            log_details = {
                "action": action,
                "entity_type": entity_type,
                "entity_id": str(entity_id),
                "timestamp": datetime.utcnow().isoformat(),
            }
            
            if data:
                # Serializar dados (remover valores não serializáveis)
                serializable_data = self._make_serializable(data)
                log_details["data"] = serializable_data
            
            if details:
                log_details["details"] = details
            
            # Determinar tipo de log baseado na entidade
            tipo_log = self._get_tipo_log(entity_type, action)
            
            # Criar log
            log_data = {
                "tipo": tipo_log,
                "usuario_id": user_id,
                "referencia_id": entity_id,
                "data": datetime.utcnow(),
                "detalhes": json.dumps(log_details, ensure_ascii=False, default=str)
            }
            
            log_entry = self.repository.create(log_data)
            
            # Log também no sistema de logging
            logger.info(
                f"AUDIT {action}: {entity_type} (ID: {entity_id}) "
                f"por usuário {user_id or 'sistema'}"
            )
            
            return log_entry
            
        except Exception as e:
            # Não falhar a operação principal se o log falhar
            logger.error(f"Erro ao registrar auditoria: {e}", exc_info=True)
            # Retornar None em caso de erro, mas não levantar exceção
            return None
    
    def _get_tipo_log(self, entity_type: str, action: str) -> TipoLog:
        """
        Determina o tipo de log baseado na entidade e ação
        """
        entity_type_lower = entity_type.lower()
        
        # Mapear tipos específicos
        if "pesagem" in entity_type_lower:
            return TipoLog.PESAGEM
        elif "movimentacao" in entity_type_lower or "camara" in entity_type_lower:
            return TipoLog.MOVIMENTACAO
        elif "devolucao" in entity_type_lower:
            return TipoLog.DEVOLUCAO
        elif "carga" in entity_type_lower and action == "CREATE":
            return TipoLog.CARREGAMENTO
        elif action == "UPDATE":
            return TipoLog.ATUALIZACAO
        else:
            return TipoLog.OUTRO
    
    def _make_serializable(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Converte dados para formato serializável (JSON)
        """
        serializable = {}
        for key, value in data.items():
            if value is None:
                serializable[key] = None
            elif isinstance(value, (str, int, float, bool)):
                serializable[key] = value
            elif isinstance(value, (UUID, datetime)):
                serializable[key] = str(value)
            elif isinstance(value, dict):
                serializable[key] = self._make_serializable(value)
            elif isinstance(value, list):
                serializable[key] = [
                    self._make_serializable(item) if isinstance(item, dict) else str(item)
                    for item in value
                ]
            else:
                # Para outros tipos, converter para string
                serializable[key] = str(value)
        
        return serializable


def get_audit_service(db: Session) -> AuditService:
    """
    Factory function para obter instância do AuditService
    """
    return AuditService(db)

