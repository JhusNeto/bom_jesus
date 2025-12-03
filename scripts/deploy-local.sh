#!/bin/bash

# Script para deploy local (teste do stack completo)
# Sistema Operacional Bom Jesus

set -e

echo "🚀 Deploy Local - Sistema Operacional Bom Jesus"
echo ""

# Verificar Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker não encontrado"
    exit 1
fi

echo "✅ Docker encontrado"
echo ""

# Parar containers existentes
echo "🛑 Parando containers existentes..."
docker compose down 2>/dev/null || true

# Build e start
echo "🔨 Fazendo build das imagens..."
docker compose build

echo "🚀 Iniciando serviços..."
docker compose up -d

echo "⏳ Aguardando serviços iniciarem..."
sleep 10

# Verificar status
echo ""
echo "📊 Status dos serviços:"
docker compose ps

echo ""
echo "✅ Deploy local concluído!"
echo ""
echo "📍 Endpoints:"
echo "   - Frontend: http://localhost:3000"
echo "   - Backend: http://localhost:8000"
echo "   - API Docs: http://localhost:8000/docs"
echo "   - Health: http://localhost:8000/api/v1/health"
echo "   - DB Health: http://localhost:8000/api/v1/db/health"
echo ""

