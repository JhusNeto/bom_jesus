"""
Integração com Redis
Gerencia conexão e operações com Redis para cache e sessões
"""
import redis
from typing import Optional
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Cliente Redis global
_redis_client: Optional[redis.Redis] = None


def get_redis() -> redis.Redis:
    """
    Obtém ou cria cliente Redis
    Singleton pattern para reutilizar conexão
    """
    global _redis_client
    
    if _redis_client is None:
        try:
            _redis_client = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
            )
            # Testa conexão
            _redis_client.ping()
            logger.info("Redis conectado com sucesso")
        except Exception as e:
            logger.error(f"Erro ao conectar Redis: {e}")
            raise
    
    return _redis_client


def close_redis():
    """Fecha conexão Redis"""
    global _redis_client
    if _redis_client:
        _redis_client.close()
        _redis_client = None
        logger.info("Redis desconectado")


# Funções auxiliares para refresh tokens
def save_refresh_token(user_id: str, refresh_token: str, expires_in_seconds: int = 604800) -> bool:
    """
    Salva refresh token no Redis (whitelist)
    
    Args:
        user_id: ID do usuário
        refresh_token: Token de refresh
        expires_in_seconds: Tempo de expiração em segundos (padrão: 7 dias)
    
    Returns:
        True se salvou com sucesso
    """
    try:
        redis_client = get_redis()
        key = f"refresh_token:{user_id}:{refresh_token}"
        redis_client.setex(key, expires_in_seconds, "1")
        return True
    except Exception as e:
        logger.error(f"Erro ao salvar refresh token: {e}")
        return False


def verify_refresh_token(user_id: str, refresh_token: str) -> bool:
    """
    Verifica se refresh token está na whitelist
    
    Args:
        user_id: ID do usuário
        refresh_token: Token de refresh
    
    Returns:
        True se token está válido
    """
    try:
        redis_client = get_redis()
        key = f"refresh_token:{user_id}:{refresh_token}"
        return redis_client.exists(key) == 1
    except Exception as e:
        logger.error(f"Erro ao verificar refresh token: {e}")
        return False


def revoke_refresh_token(user_id: str, refresh_token: str) -> bool:
    """
    Remove refresh token da whitelist (logout)
    
    Args:
        user_id: ID do usuário
        refresh_token: Token de refresh
    
    Returns:
        True se removeu com sucesso
    """
    try:
        redis_client = get_redis()
        key = f"refresh_token:{user_id}:{refresh_token}"
        redis_client.delete(key)
        return True
    except Exception as e:
        logger.error(f"Erro ao revogar refresh token: {e}")
        return False


def revoke_all_refresh_tokens(user_id: str) -> bool:
    """
    Remove todos os refresh tokens de um usuário
    
    Args:
        user_id: ID do usuário
    
    Returns:
        True se removeu com sucesso
    """
    try:
        redis_client = get_redis()
        pattern = f"refresh_token:{user_id}:*"
        keys = redis_client.keys(pattern)
        if keys:
            redis_client.delete(*keys)
        return True
    except Exception as e:
        logger.error(f"Erro ao revogar todos os refresh tokens: {e}")
        return False

