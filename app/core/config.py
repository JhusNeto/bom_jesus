"""
Configurações da aplicação usando Pydantic Settings
Suporta variáveis de ambiente via .env
"""
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Configurações da aplicação"""
    
    # Aplicação
    APP_NAME: str = "Sistema Operacional Bom Jesus"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=False, description="Modo debug")
    ENVIRONMENT: str = Field(default="production", description="Ambiente de execução")
    
    # Servidor
    HOST: str = Field(default="0.0.0.0", description="Host do servidor")
    PORT: int = Field(default=8000, description="Porta do servidor")
    
    # Database
    DATABASE_URL: str = Field(
        default="postgresql://postgres:postgres@localhost:5432/bom_jesus_db",
        description="URL de conexão com o banco de dados"
    )
    
    # Segurança
    SECRET_KEY: str = Field(
        default="change-me-in-production",
        description="Chave secreta para JWT"
    )
    ALGORITHM: str = Field(default="HS256", description="Algoritmo de criptografia")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30,
        description="Tempo de expiração do token em minutos"
    )
    
    # CORS
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        description="Origens permitidas para CORS"
    )
    
    # Redis
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        description="URL de conexão com Redis"
    )
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", description="Nível de log")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Instância global das configurações
settings = Settings()

