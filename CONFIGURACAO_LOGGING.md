# ✅ Configuração de Logging - Sistema Operacional Bom Jesus

**Data:** 2025-12-06  
**Status:** ✅ **IMPLEMENTADO E FUNCIONANDO**

---

## 📋 Resumo

Sistema de logging robusto configurado para a aplicação FastAPI, com suporte a:
- ✅ Logs em arquivo e console
- ✅ Rotação automática de arquivos
- ✅ Logs separados por tipo (app, errors, access)
- ✅ Middleware de requisições HTTP
- ✅ Formatação estruturada
- ✅ Configuração via variáveis de ambiente

---

## 🔧 Arquitetura

### Módulo de Logging
**Arquivo:** `app/core/logging.py`

O módulo `setup_logging()` configura o sistema de logs com:

1. **Logs em Arquivo:**
   - `app.log` - Todos os logs da aplicação
   - `errors.log` - Apenas erros (ERROR e acima)
   - `access.log` - Requisições HTTP

2. **Rotação Automática:**
   - Tamanho máximo: 10MB por arquivo
   - Backup: 5 arquivos de backup
   - Encoding: UTF-8

3. **Formato de Log:**
   ```
   YYYY-MM-DD HH:MM:SS | LEVEL | logger | filename:lineno | message
   ```

---

## 📁 Estrutura de Arquivos

```
/app/logs/
├── app.log          # Logs gerais da aplicação
├── app.log.1         # Backup 1
├── app.log.2         # Backup 2
├── errors.log        # Apenas erros
├── errors.log.1      # Backup 1
├── access.log        # Requisições HTTP
└── access.log.1      # Backup 1
```

---

## ⚙️ Configurações

### Variáveis de Ambiente

Adicione ao `.env`:

```bash
# Logging
LOG_LEVEL=INFO                    # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_DIR=/app/logs                 # Diretório para arquivos de log
ENABLE_FILE_LOGGING=True          # Habilitar logs em arquivo
ENABLE_CONSOLE_LOGGING=True        # Habilitar logs no console
```

### Settings (`app/core/config.py`)

```python
LOG_LEVEL: str = Field(default="INFO", description="Nível de log")
LOG_DIR: str = Field(default="/app/logs", description="Diretório para arquivos de log")
ENABLE_FILE_LOGGING: bool = Field(default=True, description="Habilitar logs em arquivo")
ENABLE_CONSOLE_LOGGING: bool = Field(default=True, description="Habilitar logs no console")
```

---

## 🔄 Integração com FastAPI

### 1. Middleware de Requisições HTTP

O middleware `log_requests` registra todas as requisições HTTP:

```python
@app.middleware("http")
async def log_requests(request: Request, call_next):
    # Registra: método, URL, status, tempo, IP, user-agent
```

**Exemplo de log:**
```
2025-12-06 21:48:58 | INFO | access | GET http://localhost:8000/api/v1/health | Status: 200 | Time: 0.012s | IP: 172.18.0.1 | User-Agent: curl/7.64.1
```

### 2. Lifespan Events

Logs de inicialização e shutdown da aplicação:

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logs
    logger.info("Iniciando Sistema Operacional Bom Jesus v1.0.0")
    logger.info("✅ Redis conectado com sucesso")
    logger.info("✅ Banco de dados conectado com sucesso")
    
    yield
    
    # Shutdown logs
    logger.info("Encerrando aplicação...")
```

---

## 📊 Níveis de Log

### Hierarquia:
1. **DEBUG** - Informações detalhadas para debug
2. **INFO** - Informações gerais (padrão)
3. **WARNING** - Avisos (não críticos)
4. **ERROR** - Erros que precisam atenção
5. **CRITICAL** - Erros críticos que podem parar a aplicação

### Configuração por Logger:

```python
# Reduzir verbosidade de bibliotecas externas
logging.getLogger("uvicorn").setLevel(logging.WARNING)
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
logging.getLogger("fastapi").setLevel(logging.INFO)
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
```

---

## 🎯 Uso na Aplicação

### Obter Logger

```python
from app.core.logging import get_logger

logger = get_logger(__name__)

# Usar
logger.info("Operação realizada com sucesso")
logger.warning("Atenção: valor pode estar incorreto")
logger.error("Erro ao processar requisição", exc_info=True)
```

### Exemplos de Logs

```python
# Info
logger.info(f"Usuário {user_id} autenticado com sucesso")

# Warning
logger.warning(f"Tentativa de acesso não autorizado: {user_id}")

# Error
logger.error(f"Erro ao salvar no banco: {str(e)}", exc_info=True)

# Critical
logger.critical(f"Sistema de pagamento indisponível")
```

---

## 📝 Exemplos de Logs Gerados

### app.log
```
2025-12-06 21:48:58 | INFO     | main | main.py:33 | Iniciando Sistema Operacional Bom Jesus v1.0.0
2025-12-06 21:48:58 | INFO     | main | main.py:34 | Ambiente: development
2025-12-06 21:48:58 | INFO     | app.core.redis | redis.py:34 | Redis conectado com sucesso
2025-12-06 21:48:58 | INFO     | main | main.py:41 | ✅ Redis conectado com sucesso
```

### errors.log
```
2025-12-06 21:50:12 | ERROR    | main | main.py:118 | Erro ao processar requisição: POST /api/v1/auth/login | IP: 172.18.0.1 | Error: Invalid credentials
```

### access.log
```
2025-12-06 21:48:58 | INFO | access | GET http://localhost:8000/api/v1/health | Status: 200 | Time: 0.012s | IP: 172.18.0.1 | User-Agent: curl/7.64.1
2025-12-06 21:49:05 | INFO | access | POST http://localhost:8000/api/v1/auth/login | Status: 200 | Time: 0.045s | IP: 172.18.0.1 | User-Agent: Mozilla/5.0
```

---

## 🔍 Monitoramento

### Ver Logs em Tempo Real

```bash
# Logs gerais
docker exec bom_jesus_backend_dev tail -f /app/logs/app.log

# Apenas erros
docker exec bom_jesus_backend_dev tail -f /app/logs/errors.log

# Requisições HTTP
docker exec bom_jesus_backend_dev tail -f /app/logs/access.log

# Últimas 50 linhas
docker exec bom_jesus_backend_dev tail -50 /app/logs/app.log
```

### Logs do Container

```bash
# Logs do uvicorn (console)
docker logs bom_jesus_backend_dev --tail 100 -f
```

---

## 🛠️ Troubleshooting

### Logs não aparecem

1. Verificar permissões do diretório:
```bash
docker exec bom_jesus_backend_dev ls -la /app/logs
```

2. Verificar configurações:
```bash
docker exec bom_jesus_backend_dev python -c "from app.core.config import settings; print(settings.LOG_DIR, settings.LOG_LEVEL)"
```

3. Verificar se o diretório existe:
```bash
docker exec bom_jesus_backend_dev mkdir -p /app/logs
```

### Logs muito verbosos

Ajustar `LOG_LEVEL` no `.env`:
```bash
LOG_LEVEL=WARNING  # Apenas warnings e erros
```

### Arquivos de log muito grandes

A rotação automática mantém apenas 5 backups de 10MB cada. Para limpar manualmente:

```bash
docker exec bom_jesus_backend_dev find /app/logs -name "*.log.*" -mtime +7 -delete
```

---

## ✅ Validação

### Testes Realizados:
- ✅ Logs em arquivo funcionando
- ✅ Logs no console funcionando
- ✅ Rotação de arquivos funcionando
- ✅ Middleware de requisições funcionando
- ✅ Logs de erro funcionando
- ✅ Logs de acesso funcionando
- ✅ Formatação correta
- ✅ Configuração via variáveis de ambiente

---

## 📚 Próximos Passos (Futuro)

1. **Logs Estruturados (JSON):**
   - Usar `python-json-logger` para logs em formato JSON
   - Facilita integração com ferramentas de monitoramento

2. **Integração com ELK Stack:**
   - Enviar logs para Elasticsearch
   - Dashboard no Kibana

3. **Alertas:**
   - Alertar em caso de muitos erros
   - Alertar em caso de requisições lentas

4. **Métricas:**
   - Contador de requisições por endpoint
   - Tempo médio de resposta
   - Taxa de erro

---

## ✅ Conclusão

**Status:** ✅ **100% IMPLEMENTADO E FUNCIONANDO**

O sistema de logging está completamente configurado e funcionando:
- ✅ Logs em arquivo e console
- ✅ Rotação automática
- ✅ Logs separados por tipo
- ✅ Middleware de requisições
- ✅ Formatação estruturada
- ✅ Configuração flexível

O sistema agora possui rastreabilidade completa de todas as operações, facilitando:
- Debug de problemas
- Auditoria de requisições
- Monitoramento de performance
- Análise de erros

---

**Última atualização:** 2025-12-06

