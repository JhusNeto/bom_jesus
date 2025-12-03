#!/bin/bash

# Script para fazer deploy local (simulando produção)
# Sistema Operacional Bom Jesus

set -e

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "🚀 Deploy Local (Simulação de Produção)"
echo "========================================"
echo ""

# Verificar se .env.prod existe
if [ ! -f .env.prod ]; then
    echo -e "${YELLOW}⚠️  Arquivo .env.prod não encontrado${NC}"
    echo "Copiando de env.prod.example..."
    cp env.prod.example .env.prod
    echo -e "${YELLOW}⚠️  Configure o .env.prod antes de continuar!${NC}"
    echo "Editando .env.prod..."
    ${EDITOR:-nano} .env.prod
fi

# Build das imagens locais
echo "🔨 Fazendo build das imagens locais..."
echo ""

echo "📦 Build do Backend..."
docker build -f Dockerfile.backend -t bomjesus/backend:latest .

echo ""
echo "📦 Build do Frontend..."
cd frontend
docker build -f Dockerfile.frontend -t bomjesus/frontend:latest .
cd ..

echo ""
echo "🛑 Parando containers existentes..."
docker compose -f docker-compose.prod.yml down 2>/dev/null || true

echo ""
echo "🚀 Iniciando serviços de produção..."
docker compose -f docker-compose.prod.yml up -d

echo ""
echo "⏳ Aguardando serviços iniciarem..."
sleep 10

echo ""
echo "📊 Status dos serviços:"
docker compose -f docker-compose.prod.yml ps

echo ""
echo "🧪 Testando endpoints..."
echo ""

# Testar health check
if curl -f -s http://localhost:8000/api/v1/health > /dev/null; then
    echo -e "${GREEN}✅ Health check: OK${NC}"
else
    echo -e "${RED}❌ Health check: FALHOU${NC}"
fi

# Testar DB health check
if curl -f -s http://localhost:8000/api/v1/db/health > /dev/null; then
    echo -e "${GREEN}✅ DB health check: OK${NC}"
else
    echo -e "${RED}❌ DB health check: FALHOU${NC}"
fi

echo ""
echo "========================================"
echo -e "${GREEN}✅ Deploy local concluído!${NC}"
echo ""
echo "📍 Endpoints:"
echo "   - Backend: http://localhost:8000"
echo "   - API Docs: http://localhost:8000/docs"
echo "   - Health: http://localhost:8000/api/v1/health"
echo ""
echo "📋 Ver logs:"
echo "   docker compose -f docker-compose.prod.yml logs -f"
echo ""
echo "🛑 Parar serviços:"
echo "   docker compose -f docker-compose.prod.yml down"

