# 📊 Documentação do Banco de Dados - Sistema Operacional Bom Jesus

## Visão Geral

O sistema utiliza **PostgreSQL 14+** como banco de dados principal, gerenciado através do **SQLAlchemy ORM** e **Alembic** para migrações.

---

## 🗄️ Arquitetura do Banco

### Stack Tecnológica

- **SGBD**: PostgreSQL 14+
- **ORM**: SQLAlchemy 2.0+
- **Migrações**: Alembic
- **Hospedagem MVP**: Docker (PostgreSQL Alpine)
- **Hospedagem Futura**: RDS (AWS) ou Cloud SQL (GCP)

### Estrutura de Conexão

```
Backend FastAPI
    ↓
SQLAlchemy Engine
    ↓
Session Factory
    ↓
PostgreSQL Database
```

---

## 📋 Entidades do Banco

### 1. Users (usuarios)

Tabela principal de usuários do sistema.

**Campos**:
- `id` (UUID) - Primary Key
- `name` (String) - Nome do usuário
- `email` (String, Unique) - Email do usuário
- `hashed_password` (String) - Senha criptografada (bcrypt)
- `role` (Enum) - Role do usuário (admin, manager, operator, viewer)
- `is_active` (String) - Status ativo/inativo (Y/N)
- `created_at` (DateTime) - Data de criação
- `updated_at` (DateTime) - Data de atualização

**Roles Disponíveis**:
- `ADMIN` - Administrador completo
- `MANAGER` - Gerente
- `OPERATOR` - Operador
- `VIEWER` - Visualizador (somente leitura)

**Relacionamentos**:
- Um usuário pode ter múltiplos tokens de autenticação (1:N)

### 2. AuthTokens (auth_tokens)

Tabela de tokens de autenticação JWT.

**Campos**:
- `id` (UUID) - Primary Key
- `user_id` (UUID, FK) - Referência ao usuário
- `token` (String, Unique) - Token JWT
- `token_type` (String) - Tipo do token (bearer)
- `is_active` (Boolean) - Token ativo/inativo
- `expires_at` (DateTime) - Data de expiração
- `created_at` (DateTime) - Data de criação
- `last_used_at` (DateTime) - Último uso do token
- `user_agent` (Text) - User agent do navegador
- `ip_address` (String) - IP de origem

**Relacionamentos**:
- Pertence a um usuário (N:1)

---

## 🗺️ Diagrama de Entidades

```
┌─────────────────┐
│     Users       │
├─────────────────┤
│ id (UUID) PK    │
│ name            │
│ email (unique)  │
│ hashed_password │
│ role (enum)     │
│ is_active       │
│ created_at      │
│ updated_at      │
└────────┬────────┘
         │
         │ 1:N
         │
┌────────▼────────┐
│  AuthTokens     │
├─────────────────┤
│ id (UUID) PK    │
│ user_id (FK)    │
│ token (unique)  │
│ token_type      │
│ is_active       │
│ expires_at      │
│ created_at      │
│ last_used_at    │
│ user_agent      │
│ ip_address      │
└─────────────────┘
```

---

## 🐳 Configuração Docker

### Variáveis de Ambiente

Configuradas no `docker-compose.yml`:

```yaml
POSTGRES_USER: postgres
POSTGRES_PASSWORD: postgres
POSTGRES_DB: bom_jesus_db
POSTGRES_PORT: 5433
```

### Volume Persistente

Os dados são armazenados em volume Docker nomeado:
- `postgres_data` - Persiste dados entre restarts

### Health Check

O PostgreSQL possui health check configurado:
- Comando: `pg_isready -U postgres`
- Intervalo: 10 segundos
- Timeout: 5 segundos
- Retries: 5

---

## 🔧 Configuração e Conexão

### URL de Conexão

A URL de conexão é configurada via variável de ambiente:

```
DATABASE_URL=postgresql://postgres:postgres@db:5432/bom_jesus_db
```

**Formato**: `postgresql://usuario:senha@host:porta/nome_banco`

### Configuração Local vs Docker

**Local (fora do Docker)**:
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5433/bom_jesus_db
```

**Docker (dentro da rede)**:
```env
DATABASE_URL=postgresql://postgres:postgres@db:5432/bom_jesus_db
```

---

## 📦 Migrações (Alembic)

### Estrutura de Migrações

```
alembic/
├── env.py              # Configuração do Alembic
├── script.py.mako      # Template de migrations
└── versions/           # Arquivos de migração
    └── [migration files]
```

### Comandos Principais

#### Criar Migration

```bash
# Auto-generate migration baseado nos models
alembic revision --autogenerate -m "descrição da migration"

# Criar migration vazia
alembic revision -m "descrição da migration"
```

#### Aplicar Migrations

```bash
# Aplicar todas as migrations pendentes
alembic upgrade head

# Aplicar próxima migration
alembic upgrade +1

# Ver histórico
alembic history
```

#### Reverter Migrations

```bash
# Reverter última migration
alembic downgrade -1

# Reverter todas
alembic downgrade base
```

### Criar Migration Inicial

Para criar a migration inicial com as tabelas base:

```bash
# 1. Certifique-se de que o banco está rodando
docker compose up -d db

# 2. Crie a migration inicial
alembic revision --autogenerate -m "Initial migration: users and auth_tokens"

# 3. Revise o arquivo gerado em alembic/versions/

# 4. Aplique a migration
alembic upgrade head
```

---

## 🚀 Como Rodar e Conectar

### 1. Iniciar Banco com Docker

```bash
# Iniciar apenas o banco
docker compose up -d db

# Ver logs
docker compose logs -f db

# Verificar status
docker compose ps db
```

### 2. Conectar Localmente

```bash
# Via Docker
docker compose exec db psql -U postgres -d bom_jesus_db

# Via cliente local (se tiver instalado)
psql -h localhost -p 5433 -U postgres -d bom_jesus_db
```

### 3. Verificar Conexão

```bash
# Health check do backend
curl http://localhost:8000/api/v1/db/health

# Deve retornar:
# {
#   "status": "ok",
#   "database": "connected",
#   "version": "PostgreSQL 14.x"
# }
```

---

## 📝 Models (SQLAlchemy)

### Localização

Models estão em `app/models/`:

- `app/models/user.py` - Model User
- `app/models/auth_token.py` - Model AuthToken

### Exemplo de Uso

```python
from app.models import User, UserRole
from app.db.session import get_db
from sqlalchemy.orm import Session

# Em um endpoint FastAPI
def get_user(user_id: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    return user
```

---

## 🔐 Segurança

### Credenciais

- **Desenvolvimento**: Credenciais padrão (postgres/postgres)
- **Produção**: **ALTERAR CREDENCIAIS!**

### Recomendações

1. ✅ Sempre use variáveis de ambiente para credenciais
2. ✅ Não commitar `.env` no Git
3. ✅ Usar senhas fortes em produção
4. ✅ Habilitar SSL em produção
5. ✅ Backup regular dos dados

---

## 🧪 Testes

### Health Check Endpoint

Teste a conexão do banco via endpoint:

```bash
GET /api/v1/db/health
```

**Resposta de sucesso**:
```json
{
  "status": "ok",
  "database": "connected",
  "version": "PostgreSQL 14.x on ..."
}
```

**Resposta de erro**:
```json
{
  "detail": "Database connection failed: [erro]"
}
```

---

## 📊 Scripts Úteis

### Backup do Banco

```bash
# Backup
docker compose exec db pg_dump -U postgres bom_jesus_db > backup.sql

# Restore
docker compose exec -T db psql -U postgres bom_jesus_db < backup.sql
```

### Limpar Banco

```bash
# Parar containers
docker compose down

# Remover volume (CUIDADO: apaga todos os dados!)
docker compose down -v

# Reiniciar do zero
docker compose up -d
```

---

## 🔄 Migração para Produção

### RDS (AWS)

1. Criar instância RDS PostgreSQL 14+
2. Configurar security groups
3. Atualizar `DATABASE_URL`:
   ```
   postgresql://user:pass@rds-endpoint.region.rds.amazonaws.com:5432/dbname
   ```
4. Aplicar migrations:
   ```bash
   alembic upgrade head
   ```

### Cloud SQL (GCP)

1. Criar instância Cloud SQL PostgreSQL
2. Configurar authorized networks
3. Atualizar `DATABASE_URL`
4. Aplicar migrations

---

## 📚 Referências

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)

---

## 🆘 Troubleshooting

### Erro: "connection refused"

- Verifique se o PostgreSQL está rodando
- Verifique a porta (5433 externa, 5432 interna)
- Verifique credenciais no `.env`

### Erro: "database does not exist"

- Verifique se o banco foi criado
- Verifique `POSTGRES_DB` no docker-compose

### Erro: "relation does not exist"

- Aplique as migrations: `alembic upgrade head`
- Verifique se os models estão corretos

---

**Última atualização**: 2024  
**Versão do PostgreSQL**: 14+

