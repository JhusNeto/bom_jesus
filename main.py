"""
Sistema Operacional Bom Jesus - Backend
Ponto de entrada da aplicação FastAPI
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import time
import traceback

from app.core.config import settings
from app.core.logging import setup_logging, get_logger
from app.core.audit import AuditService
from app.api.v1.api import api_router
from app.db.session import SessionLocal

# Configurar logging
logger = setup_logging(
    log_dir=settings.LOG_DIR,
    log_level=settings.LOG_LEVEL,
    enable_file_logging=settings.ENABLE_FILE_LOGGING,
    enable_console_logging=settings.ENABLE_CONSOLE_LOGGING,
)
access_logger = get_logger("access")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan events da aplicação
    Executado na inicialização e shutdown
    """
    # Startup
    logger.info("=" * 60)
    logger.info(f"Iniciando {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Ambiente: {settings.ENVIRONMENT}")
    logger.info(f"Debug: {settings.DEBUG}")
    logger.info(f"Log Level: {settings.LOG_LEVEL}")
    logger.info(f"Log Dir: {settings.LOG_DIR}")
    logger.info("=" * 60)
    
    # Inicializar Redis
    try:
        from app.core.redis import get_redis
        get_redis()  # Testa conexão
        logger.info("✅ Redis conectado com sucesso")
    except Exception as e:
        logger.warning(f"⚠️  Redis não disponível: {e}")
    
    # Testar conexão com banco
    try:
        from app.db.session import SessionLocal
        from sqlalchemy import text
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        logger.info("✅ Banco de dados conectado com sucesso")
    except Exception as e:
        logger.error(f"❌ Erro ao conectar com banco de dados: {e}")
    
    yield
    
    # Shutdown
    logger.info("=" * 60)
    logger.info("Encerrando aplicação...")
    # Fechar conexões
    try:
        from app.core.redis import close_redis
        close_redis()
        logger.info("✅ Redis desconectado")
    except Exception as e:
        logger.warning(f"⚠️  Erro ao desconectar Redis: {e}")
    logger.info("=" * 60)


# Criar aplicação FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Backend do Sistema Operacional Bom Jesus",
    docs_url="/docs",  # Swagger UI
    redoc_url=None,  # ReDoc desabilitado devido a problemas com CDN e headers de segurança
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Middleware de logging de requisições HTTP
class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware para registrar todas as requisições HTTP"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Informações da requisição
        method = request.method
        url = str(request.url)
        client_host = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")[:100]  # Limitar tamanho
        
        # Processar requisição
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            status_code = response.status_code
            
            # Log de acesso
            try:
                access_logger.info(
                    f"{method} {url} | "
                    f"Status: {status_code} | "
                    f"Time: {process_time:.3f}s | "
                    f"IP: {client_host} | "
                    f"User-Agent: {user_agent}"
                )
            except Exception as log_error:
                # Se falhar o log, pelo menos logar no logger principal
                logger.warning(f"Erro ao logar acesso: {log_error}")
            
            # Adicionar header com tempo de processamento
            try:
                response.headers["X-Process-Time"] = f"{process_time:.3f}"
            except Exception:
                pass  # Se não conseguir adicionar header, continua
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            error_trace = traceback.format_exc()
            
            # Log de erro
            logger.error(
                f"Erro ao processar requisição: {method} {url} | "
                f"IP: {client_host} | "
                f"Time: {process_time:.3f}s | "
                f"Error: {str(e)} | "
                f"Traceback: {error_trace}"
            )
            
            # Retornar erro 500
            return JSONResponse(
                status_code=500,
                content={
                    "detail": "Erro interno do servidor",
                    "error": str(e) if settings.DEBUG else "Erro interno"
                }
            )


# Registrar middleware de logging (deve ser após CORS, antes dos routers)
try:
    app.add_middleware(LoggingMiddleware)
    logger.info("✅ Middleware de logging registrado com sucesso")
except Exception as e:
    logger.error(f"❌ Erro ao registrar middleware de logging: {e}")
    import traceback
    logger.error(traceback.format_exc())

# ReDoc desabilitado devido a problemas com CDN (jsdelivr) e headers de segurança
# O navegador bloqueia o script por causa de X-Content-Type-Options: nosniff
# Use /docs (Swagger UI) que funciona perfeitamente
@app.get("/redoc", include_in_schema=False)
async def redoc_info():
    """Informa que ReDoc está desabilitado e redireciona para Swagger"""
    from fastapi.responses import HTMLResponse
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>ReDoc Desabilitado - Sistema Operacional Bom Jesus</title>
        <meta charset="utf-8"/>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
                background: #f5f5f5;
            }
            .container {
                background: white;
                padding: 30px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            h1 { color: #333; }
            p { color: #666; line-height: 1.6; }
            a {
                display: inline-block;
                margin-top: 20px;
                padding: 10px 20px;
                background: #007bff;
                color: white;
                text-decoration: none;
                border-radius: 4px;
            }
            a:hover { background: #0056b3; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>ReDoc Temporariamente Desabilitado</h1>
            <p>O ReDoc está desabilitado devido a problemas com o CDN (jsdelivr) e headers de segurança do navegador.</p>
            <p><strong>Use o Swagger UI que funciona perfeitamente:</strong></p>
            <a href="/docs">Abrir Swagger UI</a>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

# Exception Handlers Globais
from fastapi import Request, HTTPException
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """
    Handler para HTTPException (erros HTTP conhecidos)
    """
    # Obter informações da requisição
    client_host = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")[:200]
    
    # Tentar obter user_id se houver token
    user_id = None
    try:
        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            from app.core.security import decode_access_token
            payload = decode_access_token(token)
            if payload:
                from uuid import UUID
                user_id_str = payload.get("user_id")
                if user_id_str:
                    try:
                        user_id = UUID(user_id_str)
                    except (ValueError, TypeError):
                        pass
    except Exception:
        pass  # Se não conseguir obter user_id, continua sem ele
    
    # Registrar erro no sistema de auditoria
    try:
        db = SessionLocal()
        audit = AuditService(db)
        audit.log_error(
            error_type="HTTPException",
            error_message=exc.detail,
            stack_trace=None,  # HTTPException não tem stack trace útil
            user_id=user_id,
            request_path=str(request.url.path),
            request_method=request.method,
            ip_address=client_host,
            user_agent=user_agent,
            context={
                "status_code": exc.status_code,
                "headers": dict(request.headers)
            }
        )
        db.close()
    except Exception as e:
        logger.error(f"Erro ao registrar HTTPException: {e}")
    
    # Log no sistema de logging
    logger.warning(
        f"HTTPException {exc.status_code}: {exc.detail} | "
        f"Path: {request.url.path} | "
        f"Method: {request.method} | "
        f"IP: {client_host}"
    )
    
    # Retornar resposta padrão do FastAPI
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handler para erros de validação (Pydantic)
    """
    client_host = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")[:200]
    
    # Registrar erro
    try:
        db = SessionLocal()
        audit = AuditService(db)
        audit.log_error(
            error_type="ValidationError",
            error_message=str(exc.errors()),
            stack_trace=None,
            user_id=None,
            request_path=str(request.url.path),
            request_method=request.method,
            ip_address=client_host,
            user_agent=user_agent,
            context={
                "validation_errors": exc.errors()
            }
        )
        db.close()
    except Exception as e:
        logger.error(f"Erro ao registrar ValidationError: {e}")
    
    logger.warning(
        f"ValidationError: {exc.errors()} | "
        f"Path: {request.url.path} | "
        f"Method: {request.method}"
    )
    
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Handler para exceções não tratadas (erros inesperados)
    """
    import traceback
    
    client_host = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")[:200]
    error_trace = traceback.format_exc()
    
    # Tentar obter user_id
    user_id = None
    try:
        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            from app.core.security import decode_access_token
            payload = decode_access_token(token)
            if payload:
                from uuid import UUID
                user_id_str = payload.get("user_id")
                if user_id_str:
                    try:
                        user_id = UUID(user_id_str)
                    except (ValueError, TypeError):
                        pass
    except Exception:
        pass
    
    # Registrar erro no sistema de auditoria
    try:
        db = SessionLocal()
        audit = AuditService(db)
        audit.log_error(
            error_type=type(exc).__name__,
            error_message=str(exc),
            stack_trace=error_trace,
            user_id=user_id,
            request_path=str(request.url.path),
            request_method=request.method,
            ip_address=client_host,
            user_agent=user_agent,
            context={
                "exception_type": type(exc).__name__,
                "exception_module": getattr(exc, "__module__", None)
            }
        )
        db.close()
    except Exception as e:
        logger.error(f"Erro ao registrar exceção: {e}")
    
    # Log no sistema de logging
    logger.error(
        f"EXCEÇÃO NÃO TRATADA: {type(exc).__name__} - {str(exc)} | "
        f"Path: {request.url.path} | "
        f"Method: {request.method} | "
        f"IP: {client_host} | "
        f"Traceback: {error_trace}",
        exc_info=True
    )
    
    # Retornar erro 500
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Erro interno do servidor",
            "error": str(exc) if settings.DEBUG else "Erro interno",
            "type": type(exc).__name__
        }
    )


# Incluir routers da API
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Endpoint raiz"""
    return {
        "message": f"Bem-vindo ao {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/api/v1/health",
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )

