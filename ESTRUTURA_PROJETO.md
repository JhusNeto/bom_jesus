# 📐 Estrutura do Projeto - Sistema Operacional Bom Jesus

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Arquitetura do Sistema](#arquitetura-do-sistema)
3. [Estrutura de Diretórios](#estrutura-de-diretórios)
4. [Backend - FastAPI](#backend---fastapi)
5. [Frontend - Next.js](#frontend---nextjs)
6. [Banco de Dados](#banco-de-dados)
7. [Convenções de Nomenclatura](#convenções-de-nomenclatura)
8. [Fluxo de Dados](#fluxo-de-dados)
9. [Organização por Módulos](#organização-por-módulos)

---

## 🎯 Visão Geral

O **Sistema Operacional Bom Jesus** é uma aplicação full-stack desenvolvida para gerenciar operações de uma empresa de distribuição de frutas, com foco em:

- **Gestão de Cargas**: Controle de entrada de frutas de fornecedores
- **Gestão de Câmaras**: Controle de estoque em câmaras frias
- **Gestão de Pedidos**: Processamento de pedidos de clientes
- **Gestão de Pesagens**: Separação de caixas por cliente
- **Gestão Financeira**: Controle de gastos internos e devoluções
- **Auditoria**: Logs operacionais e rastreabilidade

### Stack Tecnológica

**Backend:**
- FastAPI (Python 3.9+)
- SQLAlchemy 2.x (ORM)
- Alembic (Migrations)
- Pydantic v2 (Validação)
- PostgreSQL 14+ (Banco de dados)
- Redis (Cache/Sessões)

**Frontend:**
- Next.js 15 (App Router)
- React 19
- TypeScript
- TailwindCSS
- shadcn/ui
- Zustand (Estado global)
- TanStack Query (Data fetching)

**Infraestrutura:**
- Docker & Docker Compose
- Nginx (Reverse proxy)
- GitHub Actions (CI/CD)

---

## 🏗️ Arquitetura do Sistema

### Arquitetura em Camadas (Backend)

```
┌─────────────────────────────────────────────────┐
│           API Layer (FastAPI Routers)            │
│  - Endpoints HTTP                                │
│  - Validação de entrada                          │
│  - Autenticação e autorização                    │
└──────────────────┬──────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────┐
│         Service Layer (Business Logic)           │
│  - Regras de negócio                            │
│  - Orquestração de operações                    │
│  - Validações complexas                         │
└──────────────────┬──────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────┐
│      Repository Layer (Data Access)              │
│  - Abstração de acesso a dados                  │
│  - Queries complexas                           │
│  - Transações                                  │
└──────────────────┬──────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────┐
│     Database Layer (SQLAlchemy Models)          │
│  - Models ORM                                   │
│  - Relacionamentos                              │
│  - Migrations (Alembic)                         │
└─────────────────────────────────────────────────┘
```

### Fluxo de Requisição

```
1. Cliente (Frontend)
   ↓ HTTP Request
2. Nginx (Reverse Proxy)
   ↓
3. FastAPI Router
   ↓
4. Service Layer
   ↓
5. Repository Layer
   ↓
6. Database (PostgreSQL)
   ↓
7. Response (JSON)
```

---

## 📂 Estrutura de Diretórios

### Estrutura Raiz

```
bom_jesus/
├── app/                          # Backend FastAPI
│   ├── api/                      # Camada de API
│   ├── core/                     # Configurações core
│   ├── db/                       # Database (SQLAlchemy)
│   ├── models/                   # Models do banco (15 entidades)
│   ├── repositories/             # Repositórios (16 arquivos)
│   ├── schemas/                  # Schemas Pydantic (15 entidades)
│   └── services/                 # Serviços (4 principais)
├── frontend/                     # Frontend Next.js
│   ├── app/                      # App Router (Next.js 15)
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
│   ├── apply-indexes.sh         # Aplicar índices
│   ├── db-setup.sh              # Setup do banco
│   ├── init-migrations.sh       # Criar migrations
│   └── init-db.sql              # SQL inicial
├── tests/                        # Testes automatizados
├── logs/                         # Logs da aplicação
├── Dockerfile.backend            # Dockerfile backend
├── docker-compose.yml            # Compose desenvolvimento
├── docker-compose.prod.yml       # Compose produção
├── alembic.ini                   # Config Alembic
├── requirements.txt              # Dependências Python
├── main.py                       # Ponto de entrada FastAPI
└── README.md                     # Documentação principal
```

---

## 🔧 Backend - FastAPI

### Estrutura Detalhada

```
app/
├── __init__.py
│
├── api/                          # Camada de API
│   ├── __init__.py
│   └── v1/                       # API v1
│       ├── __init__.py
│       ├── api.py               # Agregador de routers
│       ├── dependencies.py      # Dependências comuns
│       └── routers/             # Routers
│           ├── __init__.py
│           ├── health.py        # Health check
│           ├── auth.py          # Autenticação
│           └── db_health.py     # DB health check
│
├── core/                         # Core
│   ├── __init__.py
│   ├── config.py                # Configurações (Settings)
│   └── security.py              # Segurança (JWT, hash)
│
├── db/                           # Database
│   ├── __init__.py
│   ├── base.py                  # Base SQLAlchemy
│   └── session.py               # Sessão e engine
│
├── models/                       # Models SQLAlchemy (15 entidades)
│   ├── __init__.py
│   │
│   ├── # Núcleo Técnico
│   ├── user.py                  # Usuários do sistema
│   ├── auth_token.py            # Tokens de autenticação
│   ├── log_operacional.py       # Logs de auditoria
│   │
│   ├── # Núcleo Operacional
│   ├── carga.py                 # Entrada de frutas
│   ├── camara.py                # Câmaras frias
│   ├── movimentacao_camara.py   # Movimentações
│   ├── pesagem.py               # Pesagens/separar
│   ├── perda.py                 # Perdas/estragos
│   │
│   ├── # Núcleo Comercial
│   ├── cliente.py               # Clientes (CEASA, mercados)
│   ├── pedido.py                # Pedidos
│   ├── item_pedido.py           # Itens do pedido
│   ├── devolucao.py             # Devoluções
│   │
│   ├── # Núcleo Financeiro
│   ├── gasto_interno.py         # Gastos operacionais
│   │
│   └── # Núcleo IA/Futuro
│       ├── ocr_input.py          # OCR de pedidos
│       ├── rota.py               # Rotas de entrega
│       └── entrega_cliente.py    # Entregas
│
├── repositories/                 # Repositórios (16 arquivos)
│   ├── __init__.py
│   ├── base.py                  # BaseRepository (CRUD genérico)
│   ├── user.py
│   ├── auth_token.py
│   ├── carga.py
│   ├── camara.py
│   ├── cliente.py
│   ├── pedido.py
│   ├── pesagem.py
│   └── ... (todos os models têm repository)
│
├── schemas/                      # Schemas Pydantic (15 entidades)
│   ├── __init__.py
│   ├── user.py                   # UserBase, UserCreate, UserUpdate, UserRead
│   ├── carga.py                  # CargaBase, CargaCreate, CargaUpdate, CargaRead
│   ├── cliente.py
│   ├── pedido.py
│   └── ... (todos os models têm schemas)
│
└── services/                     # Serviços (4 principais)
    ├── __init__.py
    ├── carga.py                  # CargaService
    ├── cliente.py                # ClienteService
    ├── pedido.py                 # PedidoService
    └── pesagem.py                # PesagemService
```

### Principais Arquivos

#### `main.py`
- Ponto de entrada da aplicação FastAPI
- Configuração de CORS, middleware
- Registro de routers
- Lifespan events (startup/shutdown)

#### `app/core/config.py`
- Configurações centralizadas usando Pydantic Settings
- Suporte a variáveis de ambiente
- Validação de configurações

#### `app/db/session.py`
- Configuração do SQLAlchemy engine
- Factory de sessões
- Pool de conexões

#### `app/api/v1/api.py`
- Agregador de todos os routers
- Prefixo `/api/v1`
- Tags para documentação

---

## 🎨 Frontend - Next.js

### Estrutura Detalhada

```
frontend/
├── app/                          # App Router (Next.js 15)
│   ├── layout.tsx                 # Layout raiz
│   ├── page.tsx                   # Página inicial
│   ├── providers.tsx             # Providers (Query, etc)
│   ├── globals.css                # Estilos globais
│   │
│   ├── (auth)/                    # Grupo de rotas autenticadas
│   │   ├── layout.tsx             # Layout com autenticação
│   │   └── dashboard/
│   │       └── page.tsx           # Dashboard
│   │
│   └── (public)/                  # Grupo de rotas públicas
│       ├── layout.tsx
│       └── login/
│           └── page.tsx           # Login
│
├── components/                    # Componentes React
│   └── ui/                        # Componentes shadcn/ui
│       ├── button.tsx
│       ├── card.tsx
│       ├── input.tsx
│       ├── label.tsx
│       └── index.ts               # Exports
│
├── features/                      # Features/Módulos (futuro)
│
├── hooks/                         # Custom hooks
│   └── use-api.ts                # Hook para chamadas API
│
├── lib/                           # Utilitários
│   └── utils.ts                   # Funções utilitárias
│
├── services/                      # Serviços de API
│   ├── api.ts                    # Cliente HTTP base
│   └── auth.service.ts           # Serviço de autenticação
│
├── store/                         # Estado global (Zustand)
│   └── auth.store.ts             # Store de autenticação
│
├── types/                         # TypeScript types
│   └── index.ts                   # Tipos compartilhados
│
├── middleware.ts                  # Middleware Next.js (auth)
├── next.config.ts                 # Config Next.js
├── tailwind.config.ts             # Config TailwindCSS
├── tsconfig.json                  # Config TypeScript
└── package.json                   # Dependências
```

### Principais Arquivos

#### `app/layout.tsx`
- Layout raiz da aplicação
- Providers globais
- Metadata

#### `app/(auth)/layout.tsx`
- Layout para rotas autenticadas
- Verificação de autenticação
- Redirecionamento se não autenticado

#### `store/auth.store.ts`
- Estado global de autenticação (Zustand)
- Token, usuário, login, logout

#### `services/api.ts`
- Cliente HTTP base (fetch/axios)
- Interceptors
- Tratamento de erros

---

## 🗄️ Banco de Dados

### Estrutura

**SGBD:** PostgreSQL 14+

**ORM:** SQLAlchemy 2.x

**Migrations:** Alembic

### Entidades (15 Tabelas)

#### Núcleo Técnico
1. **users** - Usuários do sistema
2. **auth_tokens** - Tokens de autenticação JWT
3. **logs_operacionais** - Logs de auditoria

#### Núcleo Operacional
4. **cargas** - Entrada de frutas de fornecedores
5. **camaras** - Câmaras frias físicas
6. **movimentacoes_camara** - Entradas/saídas de câmaras
7. **pesagens** - Operações de pesagem/separar
8. **perdas** - Frutas estragadas/separadas

#### Núcleo Comercial
9. **clientes** - Clientes (CEASA, mercados, etc)
10. **pedidos** - Pedidos dos clientes
11. **itens_pedido** - Itens de cada pedido
12. **devolucoes** - Devoluções de caixas

#### Núcleo Financeiro
13. **gastos_internos** - Gastos operacionais internos

#### Núcleo IA/Futuro
14. **ocr_inputs** - Imagens e extração OCR
15. **rotas** - Rotas de entrega
16. **entregas_cliente** - Relação rota-cliente

### Índices de Performance

**Total:** 33 índices implementados

- **14 índices simples** em campos de data
- **13 índices compostos** para queries frequentes
- **4 índices de busca** em campos de texto
- **2 índices de filtro** em campos booleanos

Ver `INDICES_PERFORMANCE.md` para detalhes.

### Migrations

**Localização:** `alembic/versions/`

**Migrations principais:**
- `432576a07748` - Migration inicial (15 entidades)
- `e0f88042950c` - Índices de performance

---

## 📝 Convenções de Nomenclatura

### Backend (Python)

**Arquivos:**
- `snake_case.py` - Ex: `user_service.py`, `carga_repository.py`

**Classes:**
- `PascalCase` - Ex: `UserService`, `CargaRepository`, `CargaCreate`

**Funções/Variáveis:**
- `snake_case` - Ex: `get_user()`, `create_carga()`

**Constantes:**
- `UPPER_SNAKE_CASE` - Ex: `DATABASE_URL`, `SECRET_KEY`

### Frontend (TypeScript)

**Arquivos:**
- `kebab-case.tsx` ou `PascalCase.tsx` - Ex: `auth.store.ts`, `Button.tsx`

**Componentes:**
- `PascalCase` - Ex: `LoginPage`, `DashboardCard`

**Funções/Variáveis:**
- `camelCase` - Ex: `getUser()`, `handleSubmit()`

**Types/Interfaces:**
- `PascalCase` - Ex: `User`, `CargaCreate`, `ApiResponse`

### Banco de Dados

**Tabelas:**
- `snake_case` (plural) - Ex: `users`, `cargas`, `pedidos`

**Colunas:**
- `snake_case` - Ex: `created_at`, `cliente_id`, `tipo_banana`

**Índices:**
- `ix_<tabela>_<campo>` - Ex: `ix_pedidos_cliente_id`
- `ix_<tabela>_<campo1>_<campo2>` - Ex: `ix_pedidos_cliente_status`

---

## 🔄 Fluxo de Dados

### Exemplo: Criar uma Carga

```
1. Frontend (React)
   ↓ POST /api/v1/cargas
   { fornecedor: "...", tipo_banana: "nanica", ... }

2. Router (app/api/v1/routers/carga.py)
   ↓ Validação de autenticação
   ↓ Validação de entrada (Pydantic)

3. Service (app/services/carga.py)
   ↓ Regras de negócio
   ↓ Validações complexas

4. Repository (app/repositories/carga.py)
   ↓ Abstração de acesso a dados
   ↓ SQLAlchemy operations

5. Database (PostgreSQL)
   ↓ INSERT INTO cargas ...
   ↓ Retorna registro criado

6. Response
   ↓ JSON serializado
   ↓ Frontend recebe e atualiza UI
```

### Exemplo: Listar Pedidos de um Cliente

```
1. Frontend
   ↓ GET /api/v1/pedidos?cliente_id=xxx&status=aberto

2. Router
   ↓ Query parameters validation

3. Service
   ↓ Busca no repository com filtros

4. Repository
   ↓ Query otimizada com índices compostos
   ↓ SELECT * FROM pedidos WHERE cliente_id = ? AND status = ?

5. Database
   ↓ Usa índice ix_pedidos_cliente_status
   ↓ Retorna resultados

6. Response
   ↓ Lista de pedidos serializada
```

---

## 📦 Organização por Módulos

### Módulo: Gestão de Cargas

**Arquivos:**
- `app/models/carga.py` - Model
- `app/schemas/carga.py` - Schemas (Create, Update, Read)
- `app/repositories/carga.py` - Repository
- `app/services/carga.py` - Service
- `app/api/v1/routers/carga.py` - Router (futuro)

**Funcionalidades:**
- Criar carga
- Listar cargas
- Atualizar carga
- Buscar por fornecedor
- Filtrar por tipo de banana
- Filtrar por status

### Módulo: Gestão de Clientes

**Arquivos:**
- `app/models/cliente.py`
- `app/schemas/cliente.py`
- `app/repositories/cliente.py`
- `app/services/cliente.py`

**Funcionalidades:**
- CRUD completo de clientes
- Buscar por cidade/bairro
- Filtrar por tipo (CEASA, mercado, etc)
- Ativar/desativar cliente

### Módulo: Gestão de Pedidos

**Arquivos:**
- `app/models/pedido.py`
- `app/models/item_pedido.py`
- `app/schemas/pedido.py`
- `app/schemas/item_pedido.py`
- `app/repositories/pedido.py`
- `app/services/pedido.py`

**Funcionalidades:**
- Criar pedido com itens
- Atualizar status do pedido
- Listar pedidos por cliente
- Filtrar por status
- Calcular totais

### Módulo: Gestão de Pesagens

**Arquivos:**
- `app/models/pesagem.py`
- `app/schemas/pesagem.py`
- `app/repositories/pesagem.py`
- `app/services/pesagem.py`

**Funcionalidades:**
- Registrar pesagem
- Associar a carga e cliente
- Atualizar status (pendente → carregado → enviado)
- Listar pesagens por cliente/carga

---

## 🔍 Estrutura de Dependências

### Backend

```
main.py
  └── app.api.v1.api
      └── routers (auth, health, etc)
          └── services
              └── repositories
                  └── models (SQLAlchemy)
```

### Frontend

```
app/page.tsx
  └── components
  └── services/api.ts
      └── store/auth.store.ts
          └── hooks/use-api.ts
```

---

## 📚 Documentação Relacionada

- **`ARQUITETURA.md`** - Arquitetura detalhada do backend
- **`DATABASE_ENTITIES.md`** - Documentação das entidades
- **`ERD.md`** - Diagrama Entidade-Relacionamento
- **`INDICES_PERFORMANCE.md`** - Documentação dos índices
- **`DEPLOY.md`** - Guia de deploy
- **`DOCKER_GUIDE.md`** - Guia Docker

---

**Última atualização:** 2025-12-03  
**Versão do documento:** 1.0.0

