# Sistema Operacional Bom Jesus - Backend

Backend do Sistema Operacional Bom Jesus construído com **FastAPI (Python)**.

## 📋 Índice

- [Stack Tecnológica](#stack-tecnológica)
- [Arquitetura](#arquitetura)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Instalação e Execução](#instalação-e-execução)
- [Banco de Dados](#banco-de-dados)
- [Documentação da API](#documentação-da-api)
- [Deploy com Docker](#deploy-com-docker)
- [Próximos Passos](#próximos-passos)

## 🚀 Stack Tecnológica

### Framework Principal
- **FastAPI**: Framework web moderno, rápido e assíncrono para Python
- **Uvicorn**: Servidor ASGI de alta performance

### Banco de Dados
- **PostgreSQL 14+**: Banco de dados relacional
- **SQLAlchemy 2.0+**: ORM para Python
- **Alembic**: Migrações de banco de dados

### Autenticação e Segurança
- **JWT (python-jose)**: Tokens de autenticação
- **Passlib**: Hash de senhas (bcrypt)

### Background Tasks
- **Celery**: Processamento assíncrono de tarefas
- **Redis**: Broker de mensagens para Celery

### Outras Ferramentas
- **Pydantic**: Validação de dados e configurações
- **python-dotenv**: Gerenciamento de variáveis de ambiente

## 🏗️ Arquitetura

A aplicação segue uma arquitetura em camadas, separando responsabilidades:

```
┌─────────────────────────────────────┐
│         API Layer (Routers)         │  ← Endpoints HTTP
├─────────────────────────────────────┤
│      Service Layer (Services)       │  ← Lógica de Negócio
├─────────────────────────────────────┤
│   Repository Layer (Repositories)   │  ← Acesso a Dados
├─────────────────────────────────────┤
│      Database Layer (SQLAlchemy)    │  ← Models e Sessões
└─────────────────────────────────────┘
```

### Camadas

1. **API Layer** (`app/api/`): Routers FastAPI que expõem endpoints HTTP
2. **Service Layer** (`app/services/`): Lógica de negócio da aplicação
3. **Repository Layer** (`app/repositories/`): Abstração de acesso ao banco de dados
4. **Database Layer** (`app/db/`, `app/models/`): Configuração SQLAlchemy e models
5. **Schemas** (`app/schemas/`): Validação e serialização com Pydantic
6. **Core** (`app/core/`): Configurações, segurança e utilitários centrais

## 📁 Estrutura do Projeto

```
bom_jesus/
├── app/                          # Aplicação principal
│   ├── __init__.py
│   ├── api/                      # Camada de API
│   │   ├── __init__.py
│   │   └── v1/                   # API versão 1
│   │       ├── __init__.py
│   │       ├── api.py            # Agregador de routers
│   │       ├── dependencies.py   # Dependências comuns
│   │       └── routers/          # Routers da API
│   │           ├── __init__.py
│   │           ├── health.py     # Health check
│   │           ├── auth.py       # Autenticação
│   │           └── db_health.py  # Health check do banco
│   ├── core/                     # Módulo core
│   │   ├── __init__.py
│   │   ├── config.py             # Configurações (Pydantic Settings)
│   │   └── security.py           # JWT e hash de senhas
│   ├── db/                       # Database
│   │   ├── __init__.py
│   │   ├── base.py               # Base para models
│   │   └── session.py            # Sessão SQLAlchemy
│   ├── models/                   # Models SQLAlchemy
│   │   ├── __init__.py
│   │   ├── user.py               # Model User
│   │   └── auth_token.py         # Model AuthToken
│   ├── schemas/                  # Schemas Pydantic
│   │   └── __init__.py
│   ├── services/                 # Camada de serviços
│   │   └── __init__.py
│   └── repositories/             # Camada de repositórios
│       └── __init__.py
├── alembic/                      # Migrações do banco
│   ├── versions/                 # Arquivos de migração
│   ├── env.py                    # Configuração Alembic
│   └── script.py.mako            # Template de migrations
├── scripts/                      # Scripts auxiliares
│   ├── db-setup.sh              # Setup do banco
│   ├── init-migrations.sh       # Inicializar migrations
│   └── init-db.sql              # Script SQL inicial
├── tests/                        # Testes
│   └── __init__.py
├── main.py                       # Ponto de entrada
├── requirements.txt              # Dependências Python
├── Dockerfile                    # Imagem Docker
├── docker-compose.yml            # Orquestração Docker
├── alembic.ini                   # Configuração Alembic
├── env.example                   # Exemplo de variáveis de ambiente
├── DATABASE.md                   # Documentação do banco
├── .gitignore
└── README.md
```

## 🚀 Instalação e Execução

### Pré-requisitos

- Python 3.11+
- PostgreSQL 14+
- Redis (opcional, para background tasks)
- Docker e Docker Compose (opcional)

### Instalação Local

1. **Clone o repositório** (se aplicável)

2. **Crie um ambiente virtual**:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

3. **Instale as dependências**:
```bash
pip install -r requirements.txt
```

4. **Configure as variáveis de ambiente**:
```bash
cp env.example .env
# Edite o arquivo .env com suas configurações
```

5. **Configure o banco de dados**:
```bash
# Certifique-se de que o PostgreSQL está rodando
# Crie o banco de dados:
createdb bom_jesus_db

# Execute as migrações:
alembic upgrade head
```

6. **Execute a aplicação**:
```bash
# Modo desenvolvimento (com reload)
uvicorn main:app --reload

# Ou execute diretamente:
python main.py
```

A aplicação estará disponível em: `http://localhost:8000`

### Documentação Interativa

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

## 🗄️ Banco de Dados

### PostgreSQL 14+

O sistema utiliza PostgreSQL 14+ como banco de dados principal. Consulte **[DATABASE.md](./DATABASE.md)** para documentação completa.

### Quick Start

```bash
# 1. Setup do banco (Docker)
./scripts/db-setup.sh

# 2. Criar migration inicial
./scripts/init-migrations.sh

# 3. Aplicar migrations
alembic upgrade head

# 4. Verificar conexão
curl http://localhost:8000/api/v1/db/health
```

### Estrutura do Banco

**Tabelas principais**:
- `users` - Usuários do sistema
- `auth_tokens` - Tokens de autenticação

Ver [DATABASE.md](./DATABASE.md) para detalhes completos sobre:
- Arquitetura do banco
- Diagramas de entidades
- Migrações
- Scripts úteis

## 🐳 Deploy com Docker

### Início Rápido (Recomendado)

```bash
# Execute o script automatizado
./run-docker.sh
```

O script irá:
- ✅ Verificar se Docker está instalado
- ✅ Criar arquivo `.env` se não existir
- ✅ Fazer build das imagens
- ✅ Iniciar todos os serviços
- ✅ Mostrar status e endpoints

### Comandos Manuais

1. **Configure o arquivo `.env`**:
```bash
cp env.example .env
# Edite conforme necessário
```

2. **Execute com Docker Compose**:
```bash
# Build e start de todos os serviços
docker compose up -d --build

# Ver logs
docker compose logs -f backend

# Parar serviços
docker compose down

# Parar e remover volumes (limpar dados)
docker compose down -v
```

**Nota**: Use `docker compose` (v2) ou `docker-compose` (v1) conforme sua instalação.

### Build Manual da Imagem

```bash
# Build da imagem
docker build -t bom-jesus-backend .

# Execute o container
docker run -p 8000:8000 --env-file .env bom-jesus-backend
```

### Serviços no Docker Compose

- **backend**: Aplicação FastAPI (porta 8000)
- **db**: PostgreSQL 14 (porta 5433 externa, 5432 interna)
- **redis**: Redis 7 (porta 6379)

## 📚 Documentação da API

A documentação automática está disponível em:

- **Swagger UI**: `/docs` - Interface interativa para testar endpoints
- **ReDoc**: `/redoc` - Documentação alternativa

### Endpoints Disponíveis

#### Health Check
- `GET /api/v1/health` - Status da aplicação
- `GET /api/v1/health/ready` - Readiness check
- `GET /api/v1/db/health` - Health check do banco de dados ✅

#### Autenticação (Em implementação)
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/register` - Registro
- `POST /api/v1/auth/refresh` - Refresh token

## 🔧 Configurações

### Variáveis de Ambiente

Principais variáveis configuráveis (veja `env.example`):

- `DATABASE_URL`: URL de conexão PostgreSQL
- `POSTGRES_USER`: Usuário do PostgreSQL
- `POSTGRES_PASSWORD`: Senha do PostgreSQL
- `POSTGRES_DB`: Nome do banco de dados
- `POSTGRES_PORT`: Porta externa do PostgreSQL
- `SECRET_KEY`: Chave secreta para JWT (altere em produção!)
- `DEBUG`: Modo debug (True/False)
- `ENVIRONMENT`: Ambiente (development/production)
- `REDIS_URL`: URL de conexão Redis
- `CORS_ORIGINS`: Lista de origens permitidas para CORS

## 📝 Convenções de Nomenclatura

- **Routers**: `snake_case.py` (ex: `health.py`, `auth.py`)
- **Models**: `PascalCase` (ex: `User`, `Product`)
- **Schemas**: `PascalCase` com sufixo (ex: `UserCreate`, `UserResponse`)
- **Services**: `snake_case.py` (ex: `user_service.py`)
- **Repositories**: `snake_case.py` (ex: `user_repository.py`)

## 🔐 Segurança

- JWT para autenticação
- Hash de senhas com bcrypt
- CORS configurável
- Validação de dados com Pydantic
- Suporte a variáveis de ambiente para secrets

## 🧪 Testes

Estrutura preparada em `tests/`. Para executar:

```bash
pytest
```

## 🚧 Próximos Passos

### Tarefas Pendentes

1. **Implementar autenticação completa** ✅ **PARCIAL**
   - ✅ Model de User criado
   - ⏳ Endpoints de login/registro funcionais (parcialmente implementado)
   - ✅ Middleware de autenticação preparado

2. **Configurar migrações Alembic** ✅ **CONCLUÍDO**
   - ✅ Alembic inicializado e configurado
   - ✅ Migration inicial criada (ver `alembic/versions/`)
   - ✅ Auto-generate configurado
   - 📚 Ver [DATABASE.md](./DATABASE.md) para detalhes

3. **Implementar background tasks**
   - Configurar Celery
   - Criar workers
   - Exemplos de tarefas assíncronas

4. **Adicionar logging estruturado**
   - Configurar formato JSON
   - Integração com serviços de log

5. **Criar testes**
   - Testes unitários
   - Testes de integração
   - Testes de API

### Expansão Futura

- Integração com IA (preparado para APIs de IA)
- Rotas inteligentes e processamento de dados
- WebSockets para comunicação em tempo real
- Cache com Redis
- Rate limiting
- Monitoramento e métricas

## 📚 Documentação Adicional

- **[DATABASE.md](./DATABASE.md)** - Documentação completa do banco de dados
- **[ARQUITETURA.md](./ARQUITETURA.md)** - Arquitetura detalhada do sistema
- **[DECISAO_STACK.md](./DECISAO_STACK.md)** - Decisões técnicas
- **[DOCKER.md](./DOCKER.md)** - Guia Docker completo

## 📄 Licença

[Adicionar licença conforme necessário]

## 👥 Contribuição

[Adicionar guidelines de contribuição]

---

**Versão**: 1.0.0  
**Última atualização**: 2024
