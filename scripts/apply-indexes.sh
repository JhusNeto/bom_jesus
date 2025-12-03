#!/bin/bash
# Script para aplicar índices de performance no banco de dados

set -e

echo "🔍 Verificando se o banco está rodando..."
if ! docker compose ps | grep -q "bom_jesus_db"; then
    echo "❌ Banco de dados não está rodando. Iniciando..."
    docker compose up -d db-service
    echo "⏳ Aguardando banco ficar pronto..."
    sleep 5
fi

echo "📊 Aplicando migration de índices de performance..."
docker compose exec -T api-service alembic upgrade head || \
    docker compose exec api-service alembic upgrade head

echo "✅ Migration aplicada com sucesso!"
echo ""
echo "📋 Para verificar os índices criados:"
echo "   docker compose exec db-service psql -U postgres -d bom_jesus_db -c \"\\di\""
