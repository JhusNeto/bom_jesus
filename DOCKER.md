# 🐳 Guia Docker - Sistema Operacional Bom Jesus

## Início Rápido

### Opção 1: Script Automático (Recomendado)

```bash
./run-docker.sh
```

### Opção 2: Comandos Manuais

```bash
# 1. Criar arquivo .env (se não existir)
cp env.example .env

# 2. Build e iniciar containers
docker-compose up -d --build

# 3. Ver logs
docker-compose logs -f backend
```

## Comandos Úteis

### Gerenciamento de Containers

```bash
# Iniciar serviços
docker-compose up -d

# Parar serviços
docker-compose down

# Parar e remover volumes (limpar dados)
docker-compose down -v

# Rebuild da imagem
docker-compose build --no-cache

# Ver status dos containers
docker-compose ps

# Ver logs
docker-compose logs -f backend
docker-compose logs -f db
docker-compose logs -f redis
```

### Acessar Containers

```bash
# Acessar shell do backend
docker-compose exec backend bash

# Acessar PostgreSQL
docker-compose exec db psql -U postgres -d bom_jesus_db

# Acessar Redis CLI
docker-compose exec redis redis-cli
```

### Executar Comandos

```bash
# Executar comando no backend
docker-compose exec backend python -m alembic upgrade head

# Executar testes
docker-compose exec backend pytest

# Criar migração
docker-compose exec backend alembic revision --autogenerate -m "description"
```

## Serviços

### Backend (FastAPI)
- **Porta**: 8000
- **URL**: http://localhost:8000
- **Swagger**: http://localhost:8000/docs
- **Health**: http://localhost:8000/api/v1/health

### PostgreSQL
- **Porta**: 5432
- **Usuário**: postgres
- **Senha**: postgres
- **Database**: bom_jesus_db
- **Host (dentro do Docker)**: db

### Redis
- **Porta**: 6379
- **Host (dentro do Docker)**: redis

## Variáveis de Ambiente

O arquivo `.env` é carregado automaticamente. As principais variáveis:

- `DATABASE_URL`: URL de conexão (usar `db` como host dentro do Docker)
- `REDIS_URL`: URL do Redis (usar `redis` como host dentro do Docker)
- `DEBUG`: Modo debug (True/False)
- `SECRET_KEY`: Chave secreta para JWT

**Importante**: Dentro do Docker, use os nomes dos serviços como host:
- Database: `postgresql://postgres:postgres@db:5432/bom_jesus_db`
- Redis: `redis://redis:6379/0`

## Troubleshooting

### Porta já em uso

Se a porta 8000, 5432 ou 6379 estiverem em uso:

1. Pare os serviços locais que estão usando essas portas
2. Ou altere as portas no `docker-compose.yml`:
```yaml
ports:
  - "8001:8000"  # Mude 8000 para outra porta
```

### Erro de permissão

```bash
# Dar permissão ao script
chmod +x run-docker.sh
```

### Limpar tudo e recomeçar

```bash
# Parar e remover tudo
docker-compose down -v

# Remover imagens
docker-compose rm -f

# Rebuild completo
docker-compose build --no-cache
docker-compose up -d
```

### Ver logs de erro

```bash
# Logs do backend
docker-compose logs backend

# Logs de todos os serviços
docker-compose logs

# Últimas 100 linhas
docker-compose logs --tail=100 backend
```

### Container não inicia

```bash
# Verificar status
docker-compose ps

# Ver logs detalhados
docker-compose logs backend

# Verificar se o banco está saudável
docker-compose exec db pg_isready -U postgres
```

## Desenvolvimento

### Hot Reload

O backend está configurado com `--reload` para desenvolvimento. Alterações no código são refletidas automaticamente.

### Volumes

Os seguintes diretórios são montados como volumes:
- `./app` → `/app/app` (código da aplicação)
- `./logs` → `/app/logs` (logs)

## Produção

Para produção, ajuste:

1. **Remover `--reload`** do comando no `docker-compose.yml`
2. **Definir `DEBUG=False`** no `.env`
3. **Usar `SECRET_KEY` forte** no `.env`
4. **Configurar CORS** adequadamente
5. **Usar variáveis de ambiente** seguras

## Estrutura Docker

```
bom_jesus/
├── Dockerfile              # Imagem do backend
├── docker-compose.yml      # Orquestração dos serviços
├── .dockerignore           # Arquivos ignorados no build
└── run-docker.sh           # Script de execução
```

## Próximos Passos

Após iniciar os containers:

1. ✅ Verificar health: http://localhost:8000/api/v1/health
2. ✅ Acessar Swagger: http://localhost:8000/docs
3. ⏳ Configurar migrações Alembic
4. ⏳ Implementar endpoints do MVP

