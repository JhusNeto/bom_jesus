#!/bin/bash
# Script para preparar e iniciar o projeto completo

set -e

echo "🚀 Sistema Operacional Bom Jesus - Setup e Inicialização"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 1. Verificar projeto
echo "📋 Passo 1: Verificando projeto..."
./scripts/check-project.sh
echo ""

# 2. Parar containers existentes
echo "🛑 Passo 2: Parando containers existentes..."
docker compose down 2>/dev/null || true
echo -e "${GREEN}✅${NC} Containers parados"
echo ""

# 3. Criar diretório de logs se não existir
echo "📁 Passo 3: Criando diretórios necessários..."
mkdir -p logs
echo -e "${GREEN}✅${NC} Diretórios criados"
echo ""

# 4. Build das imagens
echo "🔨 Passo 4: Construindo imagens Docker..."
docker compose build
echo -e "${GREEN}✅${NC} Imagens construídas"
echo ""

# 5. Iniciar serviços
echo "▶️  Passo 5: Iniciando serviços..."
docker compose up -d
echo -e "${GREEN}✅${NC} Serviços iniciados"
echo ""

# 6. Aguardar serviços ficarem prontos
echo "⏳ Passo 6: Aguardando serviços ficarem prontos (60 segundos)..."
sleep 60
echo ""

# 7. Verificar status
echo "📊 Passo 7: Verificando status dos containers..."
docker compose ps
echo ""

# 8. Aplicar migrações
echo "🗄️  Passo 8: Aplicando migrações do banco de dados..."
if docker compose exec -T api-service alembic upgrade head 2>/dev/null; then
    echo -e "${GREEN}✅${NC} Migrações aplicadas"
else
    echo -e "${YELLOW}⚠️${NC} Erro ao aplicar migrações (pode ser que o banco ainda esteja iniciando)"
    echo "   Tente novamente em alguns segundos:"
    echo "   docker compose exec api-service alembic upgrade head"
fi
echo ""

# 9. Verificar saúde dos serviços
echo "🏥 Passo 9: Verificando saúde dos serviços..."
echo ""

# Backend
if curl -s http://localhost:8000/api/v1/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅${NC} Backend: OK"
else
    echo -e "${YELLOW}⚠️${NC} Backend: Ainda iniciando..."
fi

# Frontend
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo -e "${GREEN}✅${NC} Frontend: OK"
else
    echo -e "${YELLOW}⚠️${NC} Frontend: Ainda iniciando..."
fi

echo ""

# 10. Resumo final
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✅ Setup concluído!${NC}"
echo ""
echo "📍 URLs disponíveis:"
echo "   - Frontend:     http://localhost:3000"
echo "   - Backend:      http://localhost:8000"
echo "   - API Docs:     http://localhost:8000/docs"
echo "   - Health Check: http://localhost:8000/api/v1/health"
echo ""
echo "📋 Comandos úteis:"
echo "   - Ver logs:      docker compose logs -f"
echo "   - Parar:        docker compose down"
echo "   - Status:        docker compose ps"
echo "   - Migrações:    docker compose exec api-service alembic upgrade head"
echo ""
echo "📝 Próximos passos:"
echo "   1. Acesse http://localhost:3000 no navegador"
echo "   2. Faça login com suas credenciais"
echo "   3. Explore a aplicação!"
echo ""

