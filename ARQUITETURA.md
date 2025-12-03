# Arquitetura do Backend - Sistema Operacional Bom Jesus

## Decisão de Stack

### FastAPI (Python)

**Motivação:**
- **Performance**: FastAPI é um dos frameworks Python mais rápidos, comparável a Node.js e Go
- **Simplicidade**: Sintaxe Python limpa e intuitiva
- **Compatibilidade com IA**: Python é a linguagem padrão para IA/ML, facilitando integrações futuras
- **Documentação Automática**: Swagger/OpenAPI integrado
- **Type Hints**: Suporte nativo a type hints, melhorando qualidade do código
- **Assíncrono**: Suporte nativo a async/await para operações I/O

## Arquitetura em Camadas

### 1. API Layer (`app/api/`)

**Responsabilidade**: Exposição de endpoints HTTP

- **Routers**: Definem os endpoints da API
- **Dependencies**: Dependências reutilizáveis (autenticação, database, etc.)
- **Versionamento**: Estrutura preparada para múltiplas versões (v1, v2, etc.)

**Exemplo de uso**:
```python
from fastapi import APIRouter, Depends
from app.db.session import get_db

router = APIRouter(prefix="/users", tags=["users"])

@router.get("")
async def list_users(db: Session = Depends(get_db)):
    # Lógica aqui
    pass
```

### 2. Service Layer (`app/services/`)

**Responsabilidade**: Lógica de negócio

- Contém a lógica de negócio da aplicação
- Orquestra chamadas a repositórios
- Valida regras de negócio
- Não conhece detalhes de HTTP ou banco de dados

**Exemplo de uso**:
```python
class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
    
    def create_user(self, user_data: UserCreate) -> User:
        # Validações de negócio
        # Chama repositório
        return self.user_repo.create(user_data)
```

### 3. Repository Layer (`app/repositories/`)

**Responsabilidade**: Abstração de acesso a dados

- Abstrai operações de banco de dados
- Facilita testes (mock de repositórios)
- Centraliza queries complexas

**Exemplo de uso**:
```python
class UserRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, user: User) -> User:
        self.db.add(user)
        self.db.commit()
        return user
```

### 4. Database Layer (`app/db/`, `app/models/`)

**Responsabilidade**: Configuração e models do banco

- **Session**: Configuração SQLAlchemy
- **Models**: Definição das tabelas do banco
- **Base**: Base para todos os models

### 5. Schemas (`app/schemas/`)

**Responsabilidade**: Validação e serialização

- Schemas Pydantic para request/response
- Validação automática de dados
- Serialização para JSON

**Exemplo**:
```python
from pydantic import BaseModel

class UserCreate(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
```

### 6. Core (`app/core/`)

**Responsabilidade**: Configurações e utilitários centrais

- **config.py**: Configurações da aplicação (Pydantic Settings)
- **security.py**: JWT, hash de senhas, autenticação

## Fluxo de Dados

```
Request HTTP
    ↓
Router (app/api/v1/routers/)
    ↓
Schema Validation (app/schemas/)
    ↓
Service (app/services/)
    ↓
Repository (app/repositories/)
    ↓
Database (app/db/, app/models/)
    ↓
Response HTTP
```

## Convenções de Nomenclatura

### Arquivos
- **Routers**: `snake_case.py` (ex: `user_router.py`)
- **Services**: `snake_case.py` (ex: `user_service.py`)
- **Repositories**: `snake_case.py` (ex: `user_repository.py`)
- **Models**: `snake_case.py` (ex: `user.py`)
- **Schemas**: `snake_case.py` (ex: `user_schema.py`)

### Classes
- **Models**: `PascalCase` (ex: `User`, `Product`)
- **Schemas**: `PascalCase` com sufixo (ex: `UserCreate`, `UserResponse`)
- **Services**: `PascalCase` com sufixo `Service` (ex: `UserService`)
- **Repositories**: `PascalCase` com sufixo `Repository` (ex: `UserRepository`)

### Funções e Variáveis
- `snake_case` (ex: `get_user`, `user_id`)

## Estrutura de Pastas Detalhada

```
app/
├── api/                    # Camada de API
│   └── v1/                # Versão 1 da API
│       ├── api.py         # Agregador de routers
│       ├── dependencies.py
│       └── routers/       # Routers por domínio
│
├── core/                   # Módulo core
│   ├── config.py          # Configurações
│   └── security.py        # Segurança
│
├── db/                     # Database
│   ├── base.py            # Base para models
│   └── session.py         # Sessão SQLAlchemy
│
├── models/                 # Models SQLAlchemy
│   └── [domain]_model.py
│
├── schemas/                # Schemas Pydantic
│   └── [domain]_schema.py
│
├── services/               # Camada de serviços
│   └── [domain]_service.py
│
└── repositories/           # Camada de repositórios
    └── [domain]_repository.py
```

## Padrões de Código

### Dependency Injection

FastAPI usa dependency injection nativa:

```python
from fastapi import Depends
from app.db.session import get_db

@router.get("")
async def endpoint(db: Session = Depends(get_db)):
    # db é injetado automaticamente
    pass
```

### Async/Await

Preferir async para operações I/O:

```python
@router.get("")
async def get_users(db: Session = Depends(get_db)):
    # Operações assíncronas
    pass
```

### Type Hints

Sempre usar type hints:

```python
def create_user(user_data: UserCreate, db: Session) -> UserResponse:
    pass
```

## Segurança

### Autenticação JWT

- Tokens JWT para autenticação
- Refresh tokens para renovação
- Middleware de autenticação via dependencies

### Hash de Senhas

- Bcrypt para hash de senhas
- Nunca armazenar senhas em texto plano

### CORS

- Configurável via variáveis de ambiente
- Restrito a origens permitidas

## Background Tasks

### Preparação para Celery

Estrutura preparada para integração com Celery:

- Redis configurado no docker-compose
- Variável `REDIS_URL` no config
- Estrutura de pastas pronta para workers

### Uso Futuro

```python
from celery import Celery

celery_app = Celery(
    "bom_jesus",
    broker=settings.REDIS_URL
)

@celery_app.task
def process_data(data):
    # Tarefa assíncrona
    pass
```

## Testes

### Estrutura

```
tests/
├── __init__.py
├── conftest.py          # Fixtures pytest
├── test_api/            # Testes de API
├── test_services/       # Testes de serviços
└── test_repositories/   # Testes de repositórios
```

### Padrões

- Usar pytest
- Fixtures para database de teste
- Mock de dependências externas

## Migrações

### Alembic

- Migrações versionadas
- Auto-generate de migrations
- Rollback suportado

### Comandos

```bash
# Criar migração
alembic revision --autogenerate -m "description"

# Aplicar migrações
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Logging

### Configuração

- Logging estruturado
- Níveis configuráveis
- Suporte a JSON logs (futuro)

### Uso

```python
import logging

logger = logging.getLogger(__name__)

logger.info("Mensagem de log")
logger.error("Erro", exc_info=True)
```

## Deploy

### Docker

- Multi-stage build (futuro)
- Health checks
- Usuário não-root
- Variáveis de ambiente

### Docker Compose

- Backend, PostgreSQL, Redis
- Networks isoladas
- Volumes persistentes
- Health checks

## Expansão Futura

### Integração com IA

- Estrutura preparada para APIs de IA
- Python como linguagem padrão
- Suporte a processamento assíncrono

### Microserviços

- Estrutura modular facilita separação
- APIs versionadas
- Comunicação via HTTP/REST

### WebSockets

- FastAPI suporta WebSockets nativamente
- Preparado para comunicação em tempo real

## Boas Práticas

1. **Separação de Responsabilidades**: Cada camada tem uma responsabilidade clara
2. **Dependency Injection**: Usar dependencies do FastAPI
3. **Type Hints**: Sempre usar type hints
4. **Validação**: Pydantic para validação automática
5. **Error Handling**: Tratamento de erros consistente
6. **Logging**: Log adequado de operações importantes
7. **Testes**: Cobertura de testes adequada
8. **Documentação**: Docstrings e documentação automática

## Referências

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)

