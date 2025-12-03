"""
Router para health check do banco de dados
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.session import get_db

router = APIRouter(prefix="/db", tags=["database"])


@router.get("/health")
async def db_health_check(db: Session = Depends(get_db)):
    """
    Health check do banco de dados
    Retorna 'ok' se o banco estiver respondendo
    """
    try:
        # Testa conexão executando uma query simples
        result = db.execute(text("SELECT 1"))
        result.fetchone()
        
        # Verifica versão do PostgreSQL
        version_result = db.execute(text("SELECT version()"))
        version = version_result.fetchone()[0]
        
        return {
            "status": "ok",
            "database": "connected",
            "version": version.split(",")[0] if version else "unknown",
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Database connection failed: {str(e)}"
        )

