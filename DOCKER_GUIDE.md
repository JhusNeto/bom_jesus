# 🐳 Guia Docker - Sistema Operacional Bom Jesus

## Visão Geral

Este guia explica toda a estrutura Docker do projeto, incluindo Dockerfiles, docker-compose e boas práticas.

---

## 📋 Índice

- [Dockerfiles](#dockerfiles)
- [Docker Compose](#docker-compose)
- [Estrutura de Serviços](#estrutura-de-serviços)
- [Boas Práticas](#boas-práticas)
- [Comandos Úteis](#comandos-úteis)

---

## 🏗️ Dockerfiles

### Dockerfile.backend

**Localização**: `/Dockerfile.backend`

**Características**:
- ✅ Multi-stage build (otimizado)
- ✅ Usuário não-root para segurança
- ✅ Health check configurado
- ✅ Workers para produção (4 workers)
- ✅ Logs otimizados

**Build**:
```bash
docker build -f Dockerfile.backend -t bomjesus/backend:latest .
```

### Dockerfile.frontend

**Localização**: `/frontend/Dockerfile.frontend`

**Características**:
- ✅ Multi-stage build (deps → builder → runner)
- ✅ Standalone output (Next.js)
- ✅ Usuário não-root
- ✅ Health check configurado
- ✅ Imagem minimalista (Alpine)

**Build**:
```bash
cd frontend
docker build -f Dockerfile.frontend -t bomjesus/frontend:latest .
```

---

## 🔧 Docker Compose

### Desenvolvimento: `docker-compose.yml`

**Serviços**:
- `api-service` - Backend FastAPI (hot reload)
- `frontend-service` - Frontend Next.js (hot reload)
- `db-service` - PostgreSQL 14
- `redis-service` - Redis 7
- `pgadmin` - PGAdmin (opcional, profile tools)

**Rede**: `bomjesus-net` (bridge)

**Volumes**:
- `postgres_data` - Dados do PostgreSQL
- `redis_data` - Dados do Redis
- Volumes de código (hot reload)

**Uso**:
```bash
# Iniciar todos os serviços
docker compose up -d

# Iniciar com PGAdmin
docker compose --profile tools up -d

# Ver logs
docker compose logs -f

# Parar
docker compose down
```

### Produção: `docker-compose.prod.yml`

**Serviços**:
- `api-service` - Backend (imagem Docker Hub)
- `frontend-service` - Frontend (imagem Docker Hub)
- `db-service` - PostgreSQL 14
- `redis-service` - Redis 7 (com senha)

**Diferenças**:
- ✅ Sem hot reload
- ✅ Imagens do registry (não build local)
- ✅ Restart policies mais rígidas
- ✅ Logs estruturados (JSON)
- ✅ Health checks mais rigorosos
- ✅ Sem exposição de portas desnecessárias

**Uso**:
```bash
# Iniciar produção
docker compose -f docker-compose.prod.yml up -d

# Ver status
docker compose -f docker-compose.prod.yml ps

# Ver logs
docker compose -f docker-compose.prod.yml logs -f
```

---

## 🏛️ Estrutura de Serviços

### Nomenclatura (Kubernetes-ready)

Todos os serviços seguem padrão para futura migração para Kubernetes:

- `api-service` → `api-service` (K8s Service)
- `frontend-service` → `frontend-service` (K8s Service)
- `db-service` → `db-service` (K8s StatefulSet)
- `redis-service` → `redis-service` (K8s StatefulSet)

### Dependências e Health Checks

```
db-service (PostgreSQL)
    ↓ (healthcheck)
api-service (Backend)
    ↓ (healthcheck)
frontend-service (Frontend)
    ↓
nginx (Reverse Proxy)
```

**Health Checks Configurados**:
- ✅ PostgreSQL: `pg_isready`
- ✅ Redis: `redis-cli ping`
- ✅ Backend: `/api/v1/health`
- ✅ Frontend: `wget http://localhost:3000`

---

## 🎯 Boas Práticas Implementadas

### Segurança

- ✅ Usuários não-root em todos os containers
- ✅ Secrets via variáveis de ambiente
- ✅ Firewall da VPS protegendo banco
- ✅ SSL/HTTPS em produção
- ✅ Health checks para detectar problemas

### Performance

- ✅ Multi-stage builds (imagens menores)
- ✅ Cache de layers Docker
- ✅ Connection pooling no backend
- ✅ Workers para produção (4 workers Uvicorn)

### Observabilidade

- ✅ Logs estruturados (JSON)
- ✅ Health checks em todos os serviços
- ✅ Rotação de logs (10MB, 3 arquivos)
- ✅ Health check endpoint público

### Manutenibilidade

- ✅ Dockerfiles separados (backend/frontend)
- ✅ docker-compose separados (dev/prod)
- ✅ Variáveis de ambiente documentadas
- ✅ Scripts auxiliares

---

## 📝 Comandos Úteis

### Desenvolvimento

```bash
# Iniciar tudo
docker compose up -d

# Rebuild e iniciar
docker compose up -d --build

# Ver logs
docker compose logs -f api-service
docker compose logs -f frontend-service

# Executar comando no container
docker compose exec api-service bash
docker compose exec db-service psql -U postgres -d bom_jesus_db

# Parar tudo
docker compose down

# Limpar volumes (CUIDADO: apaga dados!)
docker compose down -v
```

### Produção

```bash
# Pull imagens atualizadas
docker compose -f docker-compose.prod.yml pull

# Iniciar/atualizar
docker compose -f docker-compose.prod.yml up -d

# Ver status
docker compose -f docker-compose.prod.yml ps

# Restart específico
docker compose -f docker-compose.prod.yml restart api-service

# Ver logs
docker compose -f docker-compose.prod.yml logs -f --tail=100

# Limpar imagens antigas
docker system prune -a
```

### Debugging

```bash
# Inspecionar container
docker inspect bom_jesus_backend_prod

# Ver processos
docker compose -f docker-compose.prod.yml top

# Ver uso de recursos
docker stats

# Entrar no container
docker compose -f docker-compose.prod.yml exec api-service sh
```

---

## 🔍 Variáveis de Ambiente

### Desenvolvimento (.env)

```env
# Database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=bom_jesus_db
POSTGRES_PORT=5433

# App
PORT=8000
FRONTEND_PORT=3000
DEBUG=True
ENVIRONMENT=development
SECRET_KEY=dev-secret-key

# Redis
REDIS_URL=redis://redis-service:6379/0
```

### Produção (.env.prod)

```env
# Database (FORTES!)
POSTGRES_USER=bomjesus
POSTGRES_PASSWORD=<senha-forte-aleatória>
POSTGRES_DB=bom_jesus_db

# Redis (FORTE!)
REDIS_PASSWORD=<senha-forte-aleatória>

# App
SECRET_KEY=<chave-secreta-forte-aleatória>
NEXT_PUBLIC_API_URL=https://seu-dominio.com
ENVIRONMENT=production

# Docker
DOCKER_REGISTRY=bomjesus
IMAGE_TAG=latest
```

---

## 📦 Imagens Docker

### Build Local

```bash
# Backend
docker build -f Dockerfile.backend -t bomjesus/backend:local .

# Frontend
cd frontend
docker build -f Dockerfile.frontend -t bomjesus/frontend:local .
```

### Push para Registry

```bash
# Login
docker login

# Tag
docker tag bomjesus/backend:local bomjesus/backend:latest
docker tag bomjesus/frontend:local bomjesus/frontend:latest

# Push
docker push bomjesus/backend:latest
docker push bomjesus/frontend:latest
```

---

## 🔄 Fluxo de Deploy

### Desenvolvimento

```
1. Código alterado
   ↓
2. Hot reload detecta mudança
   ↓
3. Serviço reinicia automaticamente
   ↓
4. Código atualizado em execução
```

### Produção (Automático)

```
1. Push para main
   ↓
2. GitHub Actions trigger
   ↓
3. Build imagens
   ↓
4. Push para Docker Hub
   ↓
5. SSH na VPS
   ↓
6. Pull imagens
   ↓
7. Restart serviços
   ↓
8. Health check
```

---

## 🚨 Troubleshooting

### Container não inicia

```bash
# Ver logs detalhados
docker compose logs <service-name>

# Verificar dependências
docker compose ps

# Verificar recursos
docker stats
```

### Health check falhando

```bash
# Testar manualmente
docker compose exec <service> <health-command>

# Aumentar start_period
# Editar docker-compose.yml
```

### Imagens não atualizam

```bash
# Forçar pull
docker compose -f docker-compose.prod.yml pull --ignore-pull-failures

# Rebuild local
docker compose build --no-cache
```

---

## 📚 Recursos

- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Multi-stage Builds](https://docs.docker.com/build/building/multi-stage/)

---

**Versão**: 1.0.0  
**Última atualização**: 2024

