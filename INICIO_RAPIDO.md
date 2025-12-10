# 🚀 Início Rápido - Sistema Operacional Bom Jesus

## ✅ Projeto Pronto e Operacional

O projeto está completamente configurado e pronto para uso!

## 📋 Pré-requisitos

- Docker e Docker Compose instalados
- Portas 3000, 8000, 5433 e 6379 disponíveis

## 🚀 Iniciar o Projeto

### Opção 1: Script Automatizado (Recomendado)

```bash
./scripts/setup-and-start.sh
```

Este script irá:
1. ✅ Verificar o projeto
2. ✅ Parar containers existentes
3. ✅ Construir imagens
4. ✅ Iniciar todos os serviços
5. ✅ Aplicar migrações do banco
6. ✅ Verificar saúde dos serviços

### Opção 2: Manual

```bash
# 1. Verificar projeto
./scripts/check-project.sh

# 2. Iniciar serviços
docker compose up -d

# 3. Aguardar serviços iniciarem (60 segundos)
sleep 60

# 4. Aplicar migrações
docker compose exec api-service alembic upgrade head

# 5. Verificar status
docker compose ps
```

## 📍 URLs Disponíveis

Após iniciar, acesse:

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation (Swagger)**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/v1/health

## 🛠️ Comandos Úteis

### Ver Logs
```bash
# Todos os serviços
docker compose logs -f

# Apenas backend
docker compose logs -f api-service

# Apenas frontend
docker compose logs -f frontend-service

# Apenas banco de dados
docker compose logs -f db-service
```

### Parar Serviços
```bash
docker compose down
```

### Parar e Remover Volumes
```bash
docker compose down -v
```

### Reiniciar um Serviço
```bash
docker compose restart api-service
```

### Status dos Containers
```bash
docker compose ps
```

### Executar Comandos no Container
```bash
# Backend (Python)
docker compose exec api-service python -c "print('Hello')"

# Aplicar migrações
docker compose exec api-service alembic upgrade head

# Criar nova migração
docker compose exec api-service alembic revision --autogenerate -m "descrição"

# Frontend (Node)
docker compose exec frontend-service npm run build
```

## 🗄️ Banco de Dados

### Conectar ao PostgreSQL
```bash
docker compose exec db-service psql -U postgres -d bom_jesus_db
```

### Backup do Banco
```bash
docker compose exec db-service pg_dump -U postgres bom_jesus_db > backup.sql
```

### Restaurar Backup
```bash
docker compose exec -T db-service psql -U postgres bom_jesus_db < backup.sql
```

## 🔧 Configuração

### Variáveis de Ambiente

O arquivo `.env` contém todas as configurações. Principais variáveis:

- `POSTGRES_USER`: Usuário do PostgreSQL (padrão: postgres)
- `POSTGRES_PASSWORD`: Senha do PostgreSQL (padrão: postgres)
- `POSTGRES_DB`: Nome do banco (padrão: bom_jesus_db)
- `SECRET_KEY`: Chave secreta para JWT (altere em produção!)
- `NEXT_PUBLIC_API_URL`: URL da API para o frontend (padrão: http://localhost:8000)

### Logs

Os logs são salvos em:
- `./logs/app.log` - Logs gerais da aplicação
- `./logs/errors.log` - Logs de erros
- `./logs/access.log` - Logs de acesso HTTP

## 🐛 Troubleshooting

### Serviços não iniciam

1. Verifique se as portas estão disponíveis:
```bash
lsof -i :3000
lsof -i :8000
lsof -i :5433
```

2. Verifique os logs:
```bash
docker compose logs
```

3. Reconstrua as imagens:
```bash
docker compose build --no-cache
docker compose up -d
```

### Erro de migrações

Se as migrações falharem, tente:

```bash
# Verificar status do banco
docker compose exec db-service pg_isready -U postgres

# Aplicar migrações novamente
docker compose exec api-service alembic upgrade head
```

### Frontend não carrega

1. Verifique se o backend está rodando:
```bash
curl http://localhost:8000/api/v1/health
```

2. Verifique os logs do frontend:
```bash
docker compose logs frontend-service
```

3. Limpe o cache do Next.js:
```bash
docker compose exec frontend-service rm -rf .next
docker compose restart frontend-service
```

## 📚 Documentação Adicional

- **README.md**: Documentação completa do projeto
- **DATABASE.md**: Guia do banco de dados
- **API Documentation**: http://localhost:8000/docs

## ✅ Checklist de Verificação

Após iniciar, verifique:

- [ ] Backend responde em http://localhost:8000/api/v1/health
- [ ] Frontend carrega em http://localhost:3000
- [ ] Swagger UI funciona em http://localhost:8000/docs
- [ ] Banco de dados está acessível
- [ ] Logs estão sendo gerados em `./logs/`

## 🎉 Pronto!

Seu projeto está rodando! Acesse http://localhost:3000 e comece a usar.

