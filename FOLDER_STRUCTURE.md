# 📁 Estrutura de Pastas - Sistema Operacional Bom Jesus

## Visão Geral

Estrutura completa do projeto, organizada para desenvolvimento e deploy.

---

## 📂 Estrutura Raiz

```
bom_jesus/
├── app/                          # Backend FastAPI
│   ├── api/                      # Camada de API
│   ├── core/                     # Configurações core
│   ├── db/                       # Database (SQLAlchemy)
│   ├── models/                   # Models do banco
│   ├── repositories/             # Repositórios
│   ├── schemas/                  # Schemas Pydantic
│   └── services/                 # Serviços
├── frontend/                     # Frontend Next.js
│   ├── app/                      # App Router
│   ├── components/               # Componentes UI
│   ├── features/                 # Módulos/Features
│   ├── hooks/                    # Custom hooks
│   ├── lib/                      # Utilitários
│   ├── services/                 # Serviços de API
│   ├── store/                    # Estado global (Zustand)
│   └── types/                    # TypeScript types
├── alembic/                      # Migrações do banco
│   ├── versions/                 # Arquivos de migração
│   ├── env.py                    # Config Alembic
│   └── script.py.mako            # Template
├── nginx/                        # Configuração Nginx
│   └── nginx.conf                # Reverse proxy
├── scripts/                      # Scripts auxiliares
│   ├── db-setup.sh              # Setup do banco
│   ├── init-migrations.sh       # Criar migrations
│   └── init-db.sql              # SQL inicial
├── .github/                      # GitHub Actions
│   └── workflows/
│       └── deploy.yml            # Deploy automático
├── logs/                         # Logs da aplicação
├── backups/                      # Backups do banco
├── Dockerfile.backend            # Dockerfile backend
├── Dockerfile                    # Dockerfile legacy (deprecated)
├── docker-compose.yml            # Compose desenvolvimento
├── docker-compose.prod.yml       # Compose produção
├── alembic.ini                   # Config Alembic
├── requirements.txt              # Dependências Python
├── env.example                   # Exemplo env vars
├── .env.prod.example             # Exemplo env prod
├── .gitignore                    # Git ignore
├── README.md                     # Documentação principal
├── DEPLOY.md                     # Guia de deploy
├── DOCKER_GUIDE.md              # Guia Docker
├── DATABASE.md                   # Documentação do banco
└── FOLDER_STRUCTURE.md          # Este arquivo
```

---

## 🎯 Backend (`/app`)

```
app/
├── __init__.py
├── api/                          # Camada de API
│   ├── __init__.py
│   └── v1/                       # API v1
│       ├── __init__.py
│       ├── api.py               # Agregador de routers
│       ├── dependencies.py      # Dependências comuns
│       └── routers/             # Routers
│           ├── health.py        # Health check
│           ├── auth.py          # Autenticação
│           └── db_health.py     # DB health check
├── core/                         # Core
│   ├── __init__.py
│   ├── config.py                # Configurações
│   └── security.py              # Segurança (JWT)
├── db/                           # Database
│   ├── __init__.py
│   ├── base.py                  # Base SQLAlchemy
│   └── session.py               # Sessão
├── models/                       # Models
│   ├── __init__.py
│   ├── user.py                  # Model User
│   └── auth_token.py            # Model AuthToken
├── repositories/                 # Repositórios
│   └── __init__.py
├── schemas/                      # Schemas Pydantic
│   └── __init__.py
└── services/                     # Serviços
    └── __init__.py
```

---

## 🎨 Frontend (`/frontend`)

```
frontend/
├── app/                          # Next.js App Router
│   ├── (auth)/                   # Rotas autenticadas
│   │   ├── layout.tsx
│   │   └── dashboard/
│   │       └── page.tsx
│   ├── (public)/                 # Rotas públicas
│   │   ├── layout.tsx
│   │   └── login/
│   │       └── page.tsx
│   ├── globals.css              # Estilos globais
│   ├── layout.tsx               # Layout root
│   ├── page.tsx                 # Página inicial
│   └── providers.tsx            # Providers
├── components/                   # Componentes
│   └── ui/                      # Componentes shadcn/ui
│       ├── button.tsx
│       ├── card.tsx
│       ├── input.tsx
│       └── label.tsx
├── features/                     # Features/Módulos
│   └── .gitkeep
├── hooks/                        # Custom hooks
│   └── use-api.ts
├── lib/                          # Utilitários
│   └── utils.ts
├── services/                     # Serviços de API
│   ├── api.ts                   # Cliente Axios
│   └── auth.service.ts          # Serviço auth
├── store/                        # Estado global
│   └── auth.store.ts            # Store auth
├── types/                        # Types TypeScript
│   └── index.ts
├── middleware.ts                 # Middleware Next.js
├── Dockerfile.frontend          # Dockerfile frontend
├── next.config.ts               # Config Next.js
├── tailwind.config.ts           # Config Tailwind
├── tsconfig.json                # Config TypeScript
└── package.json                 # Dependências
```

---

## 🗄️ Database (`/alembic`)

```
alembic/
├── versions/                     # Migrations
│   ├── README.md
│   └── [migration files].py
├── env.py                        # Configuração Alembic
└── script.py.mako                # Template de migrations
```

---

## 🔧 Configuração

### Docker

```
Dockerfile.backend               # Backend (produção)
Dockerfile                       # Backend (legacy, deprecated)
frontend/Dockerfile.frontend     # Frontend
docker-compose.yml               # Desenvolvimento
docker-compose.prod.yml          # Produção
.dockerignore                    # Ignore Docker
```

### Nginx

```
nginx/
└── nginx.conf                   # Configuração reverse proxy
```

### GitHub Actions

```
.github/
└── workflows/
    └── deploy.yml               # Pipeline de deploy
```

---

## 📝 Scripts

```
scripts/
├── db-setup.sh                  # Setup do banco
├── init-migrations.sh           # Criar migrations
└── init-db.sql                  # SQL inicial
```

---

## 📚 Documentação

```
README.md                        # Documentação principal
DEPLOY.md                        # Guia de deploy
DOCKER_GUIDE.md                  # Guia Docker
DATABASE.md                      # Documentação do banco
ARQUITETURA.md                   # Arquitetura do sistema
DECISAO_STACK.md                 # Decisões técnicas
FOLDER_STRUCTURE.md             # Este arquivo
```

---

## 🔐 Configuração e Secrets

### Desenvolvimento

```
.env                             # Variáveis de ambiente (não commitado)
env.example                      # Exemplo de variáveis
```

### Produção

```
.env.prod                        # Variáveis de produção (não commitado)
.env.prod.example                # Exemplo (commitado)
```

**IMPORTANTE**: Nunca commitar arquivos `.env` ou `.env.prod` com secrets reais!

---

## 📦 Artefatos de Build

### Backend

- Imagem Docker: `bomjesus/backend:latest`
- Build context: `/`
- Dockerfile: `Dockerfile.backend`

### Frontend

- Imagem Docker: `bomjesus/frontend:latest`
- Build context: `/frontend`
- Dockerfile: `frontend/Dockerfile.frontend`

---

## 🗂️ Volumes Docker

### Desenvolvimento

- `postgres_data` - Dados PostgreSQL
- `redis_data` - Dados Redis
- `pgadmin_data` - Dados PGAdmin
- `./app:/app/app` - Código backend (hot reload)
- `./frontend:/app` - Código frontend (hot reload)
- `./logs:/app/logs` - Logs

### Produção

- `postgres_data_prod` - Dados PostgreSQL
- `redis_data_prod` - Dados Redis
- `./logs:/app/logs` - Logs estruturados

---

## 🌐 Redes Docker

### Desenvolvimento e Produção

- `bomjesus-net` (bridge) - Rede interna dos serviços

---

## 📊 Logs

```
logs/
├── backend/                     # Logs do backend
├── frontend/                    # Logs do frontend
└── nginx/                       # Logs do Nginx (produção)
```

---

## 🔄 Backups

```
backups/                         # Backups do banco de dados
└── backup_YYYYMMDD_HHMMSS.sql.gz
```

---

## 🎯 Convenções

### Nomenclatura de Arquivos

- **Python**: `snake_case.py`
- **TypeScript/React**: `PascalCase.tsx` (componentes), `camelCase.ts` (utilitários)
- **Docker**: `Dockerfile.backend`, `Dockerfile.frontend`
- **Compose**: `docker-compose.yml`, `docker-compose.prod.yml`
- **Scripts**: `kebab-case.sh`

### Estrutura de Pastas

- **Backend**: Organizado por camada (api, services, repositories)
- **Frontend**: Organizado por tipo (components, features, hooks)
- **Database**: Alembic para migrations

---

## 🚀 Expansão Futura

### Workers (Futuro)

```
workers/
├── ocr-worker/
│   ├── Dockerfile
│   └── [código]
└── ia-worker/
    ├── Dockerfile
    └── [código]
```

### Kubernetes (Futuro)

```
k8s/
├── deployments/
├── services/
├── configmaps/
└── secrets/
```

---

**Versão**: 1.0.0  
**Última atualização**: 2024

