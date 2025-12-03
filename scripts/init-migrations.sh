#!/bin/bash

# Script para inicializar as migrations do Alembic
# Sistema Operacional Bom Jesus

set -e

echo "🔧 Inicializando migrations do Alembic"
echo ""

# Verificar se o banco está rodando
echo "Verificando conexão com o banco..."
if ! docker compose exec -T db pg_isready -U postgres > /dev/null 2>&1; then
    echo "❌ Banco de dados não está rodando!"
    echo "Execute: docker compose up -d db"
    exit 1
fi

echo "✅ Banco de dados está rodando"
echo ""

# Criar migration inicial
echo "📝 Criando migration inicial..."
alembic revision --autogenerate -m "Initial migration: users and auth_tokens"

echo ""
echo "✅ Migration criada!"
echo ""
echo "📋 Próximos passos:"
echo "1. Revise o arquivo de migration gerado em: alembic/versions/"
echo "2. Aplique a migration: alembic upgrade head"
echo ""

