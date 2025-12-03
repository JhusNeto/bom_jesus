#!/bin/bash

# Script para setup completo do banco de dados
# Sistema Operacional Bom Jesus

set -e

echo "🗄️  Setup do Banco de Dados - Sistema Operacional Bom Jesus"
echo ""

# Verificar se Docker está rodando
if ! command -v docker &> /dev/null; then
    echo "❌ Docker não encontrado"
    exit 1
fi

echo "✅ Docker encontrado"
echo ""

# Iniciar banco de dados
echo "🚀 Iniciando PostgreSQL..."
docker compose up -d db

echo "⏳ Aguardando banco ficar pronto..."
sleep 5

# Verificar se banco está saudável
for i in {1..30}; do
    if docker compose exec -T db pg_isready -U postgres > /dev/null 2>&1; then
        echo "✅ Banco de dados está pronto!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ Timeout: Banco não ficou pronto"
        exit 1
    fi
    sleep 1
done

echo ""
echo "📊 Status do banco:"
docker compose exec -T db psql -U postgres -d bom_jesus_db -c "SELECT version();" 2>/dev/null || echo "Banco criado, aguardando primeira conexão..."

echo ""
echo "✅ Setup do banco concluído!"
echo ""
echo "📋 Próximos passos:"
echo "1. Criar migration inicial: ./scripts/init-migrations.sh"
echo "2. Aplicar migrations: alembic upgrade head"
echo "3. Testar conexão: curl http://localhost:8000/api/v1/db/health"
echo ""

