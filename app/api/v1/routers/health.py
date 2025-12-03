"""
Router de health check
Endpoint básico para verificar se a API está funcionando
"""
from fastapi import APIRouter
from datetime import datetime
from app.core.config import settings

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
async def health_check():
    """
    Health check endpoint
    Retorna status da aplicação
    """
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/ready")
async def readiness_check():
    """
    Readiness check endpoint
    Verifica se a aplicação está pronta para receber requisições
    TODO: Adicionar verificação de conexão com banco de dados
    """
    return {
        "status": "ready",
        "timestamp": datetime.utcnow().isoformat(),
    }

