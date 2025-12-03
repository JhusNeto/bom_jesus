"""
Agregador de routers da API v1
"""
from fastapi import APIRouter
from app.api.v1.routers import health, auth, db_health

api_router = APIRouter()

# Incluir todos os routers
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(db_health.router)

