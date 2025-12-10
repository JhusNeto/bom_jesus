"""
Configuração de Logging da Aplicação
Sistema de logs estruturado com rotação de arquivos
"""
import logging
import logging.handlers
import os
from pathlib import Path
from typing import Optional

from app.core.config import settings


def setup_logging(
    log_dir: Optional[str] = None,
    log_level: Optional[str] = None,
    enable_file_logging: bool = True,
    enable_console_logging: bool = True,
) -> logging.Logger:
    """
    Configura o sistema de logging da aplicação.
    
    Args:
        log_dir: Diretório onde os logs serão salvos (default: ./logs)
        log_level: Nível de log (default: settings.LOG_LEVEL)
        enable_file_logging: Se True, salva logs em arquivo
        enable_console_logging: Se True, exibe logs no console
        
    Returns:
        Logger configurado
    """
    # Diretório de logs
    if log_dir is None:
        log_dir = os.getenv("LOG_DIR", "/app/logs")
    
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)
    
    # Nível de log
    if log_level is None:
        log_level = settings.LOG_LEVEL.upper()
    
    numeric_level = getattr(logging, log_level, logging.INFO)
    
    # Configurar root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Remover handlers existentes para evitar duplicação
    root_logger.handlers.clear()
    
    # Formato de log
    detailed_format = (
        "%(asctime)s | %(levelname)-8s | %(name)s | %(filename)s:%(lineno)d | %(message)s"
    )
    simple_format = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    
    formatter_detailed = logging.Formatter(
        detailed_format,
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    formatter_simple = logging.Formatter(
        simple_format,
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Handler para arquivo (com rotação)
    if enable_file_logging:
        # Log geral (app.log)
        app_log_file = log_path / "app.log"
        file_handler = logging.handlers.RotatingFileHandler(
            app_log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,  # Mantém 5 arquivos de backup
            encoding="utf-8"
        )
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter_detailed)
        root_logger.addHandler(file_handler)
        
        # Log de erros (errors.log)
        error_log_file = log_path / "errors.log"
        error_handler = logging.handlers.RotatingFileHandler(
            error_log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding="utf-8"
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter_detailed)
        root_logger.addHandler(error_handler)
        
        # Log de requisições HTTP (access.log)
        access_log_file = log_path / "access.log"
        access_handler = logging.handlers.RotatingFileHandler(
            access_log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding="utf-8"
        )
        access_handler.setLevel(logging.INFO)
        access_handler.setFormatter(formatter_simple)
        # Criar logger específico para acesso HTTP
        access_logger = logging.getLogger("access")
        access_logger.setLevel(logging.INFO)
        access_logger.addHandler(access_handler)
        access_logger.propagate = False  # Não propagar para root logger
    
    # Handler para console
    if enable_console_logging:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(numeric_level)
        # Em desenvolvimento, usar formato mais simples
        if settings.DEBUG:
            console_handler.setFormatter(formatter_simple)
        else:
            console_handler.setFormatter(formatter_detailed)
        root_logger.addHandler(console_handler)
    
    # Configurar loggers específicos
    # Reduzir verbosidade de bibliotecas externas
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)
    
    # Logger da aplicação
    app_logger = logging.getLogger("app")
    app_logger.setLevel(numeric_level)
    
    return app_logger


def get_logger(name: str) -> logging.Logger:
    """
    Obtém um logger com o nome especificado.
    
    Args:
        name: Nome do logger (geralmente __name__)
        
    Returns:
        Logger configurado
    """
    return logging.getLogger(name)


# Configurar logging na importação do módulo
app_logger = setup_logging()

