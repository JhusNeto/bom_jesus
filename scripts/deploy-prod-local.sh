#!/bin/bash
# Script para deploy local (ambiente unificado)

set -e

echo "🚀 Iniciando deploy local..."
echo ""

# Carregar variáveis de ambiente
if [ -f .env ]; then
    echo "📋 Carregando variáveis de .env..."
    export $(grep -v '^#' .env | grep -v '^$' | xargs)
else
    echo "⚠️  Arquivo .env não encontrado, usando valores padrão..."
fi

# Build das imagens
echo ""
echo "🔨 Construindo imagens..."
docker compose build --no-cache

# Parar containers antigos
echo ""
echo "🛑 Parando containers antigos..."
docker compose down 2>/dev/null || true

# Iniciar serviços
echo ""
echo "▶️  Iniciando serviços..."
docker compose up -d

# Aguardar serviços iniciarem
echo ""
echo "⏳ Aguardando serviços iniciarem (60 segundos)..."
sleep 60

# Verificar status
echo ""
echo "📊 Status dos containers:"
docker compose ps

# Verificar health
echo ""
echo "🏥 Verificando saúde dos serviços..."
echo ""

# Backend
if curl -s http://localhost:8000/api/v1/health > /dev/null; then
    echo "✅ Backend: OK"
else
    echo "❌ Backend: FALHOU"
    docker logs bom_jesus_backend_dev --tail 20
fi

# Frontend
if curl -s http://localhost:3000 > /dev/null; then
    echo "✅ Frontend: OK"
else
    echo "❌ Frontend: FALHOU"
    docker logs bom_jesus_frontend_dev --tail 20
fi

echo ""
echo "✅ Deploy concluído!"
echo ""
echo "📝 URLs:"
echo "  - Backend: http://localhost:8000"
echo "  - Frontend: http://localhost:3000"
echo "  - API Health: http://localhost:8000/api/v1/health"
echo ""
echo "📋 Comandos úteis:"
echo "  - Ver logs: docker compose logs -f"
echo "  - Parar: docker compose down"
echo "  - Status: docker compose ps"
