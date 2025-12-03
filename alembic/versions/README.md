# Migrations do Alembic

Este diretório contém os arquivos de migração do banco de dados.

## Como criar uma nova migration

```bash
# Auto-generate baseado nos models
alembic revision --autogenerate -m "descrição da migration"

# Ou criar migration vazia
alembic revision -m "descrição da migration"
```

## Como aplicar migrations

```bash
# Aplicar todas
alembic upgrade head

# Aplicar próxima
alembic upgrade +1
```

## Como reverter

```bash
# Reverter última
alembic downgrade -1

# Reverter todas
alembic downgrade base
```

## Migration Inicial

Para criar a migration inicial com as tabelas base (users e auth_tokens):

```bash
# 1. Certifique-se que o banco está rodando
docker compose up -d db

# 2. Crie a migration
alembic revision --autogenerate -m "Initial migration: users and auth_tokens"

# 3. Revise o arquivo gerado

# 4. Aplique
alembic upgrade head
```

