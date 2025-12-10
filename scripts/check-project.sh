#!/bin/bash
# Script para verificar e preparar o projeto

set -e

echo "🔍 Verificando projeto Sistema Operacional Bom Jesus..."
echo ""

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Função para verificar comando
check_command() {
    if command -v $1 &> /dev/null; then
        echo -e "${GREEN}✅${NC} $1 encontrado"
        return 0
    else
        echo -e "${RED}❌${NC} $1 não encontrado"
        return 1
    fi
}

# Verificar comandos necessários
echo "📦 Verificando dependências..."
check_command docker || exit 1
check_command docker-compose || check_command "docker compose" || exit 1
check_command python3 || exit 1
echo ""

# Verificar arquivos essenciais
echo "📁 Verificando arquivos essenciais..."
files=(
    "docker-compose.yml"
    "Dockerfile.backend"
    "requirements.txt"
    "main.py"
    "app/core/config.py"
    "app/api/v1/api.py"
    "frontend/package.json"
    "frontend/next.config.ts"
)

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✅${NC} $file"
    else
        echo -e "${RED}❌${NC} $file não encontrado"
        exit 1
    fi
done
echo ""

# Verificar estrutura de diretórios
echo "📂 Verificando estrutura de diretórios..."
dirs=(
    "app"
    "app/api/v1/routers"
    "app/core"
    "app/models"
    "app/services"
    "app/repositories"
    "alembic/versions"
    "frontend"
    "logs"
)

for dir in "${dirs[@]}"; do
    if [ -d "$dir" ]; then
        echo -e "${GREEN}✅${NC} $dir/"
    else
        echo -e "${YELLOW}⚠️${NC} $dir/ não encontrado (criando...)"
        mkdir -p "$dir"
    fi
done
echo ""

# Verificar .env
echo "🔐 Verificando variáveis de ambiente..."
if [ -f ".env" ]; then
    echo -e "${GREEN}✅${NC} Arquivo .env encontrado"
else
    echo -e "${YELLOW}⚠️${NC} Arquivo .env não encontrado"
    if [ -f "env.example" ]; then
        echo "   Copiando env.example para .env..."
        cp env.example .env
        echo -e "${GREEN}✅${NC} Arquivo .env criado a partir de env.example"
        echo -e "${YELLOW}⚠️${NC} IMPORTANTE: Revise e ajuste o arquivo .env antes de continuar"
    else
        echo -e "${RED}❌${NC} env.example também não encontrado"
    fi
fi
echo ""

# Verificar sintaxe Python
echo "🐍 Verificando sintaxe Python..."
if python3 -m py_compile main.py 2>/dev/null; then
    echo -e "${GREEN}✅${NC} Sintaxe Python OK (main.py)"
else
    echo -e "${RED}❌${NC} Erro de sintaxe em main.py"
    exit 1
fi

# Verificar imports principais (opcional - pode falhar se dependências não estiverem instaladas localmente)
echo "📦 Verificando imports principais..."
python3 << EOF
import sys
try:
    from app.core.config import settings
    from app.api.v1.api import api_router
    print("✅ Imports principais OK")
except ImportError as e:
    print(f"⚠️  Imports não verificados (dependências não instaladas localmente)")
    print(f"   Isso é normal se você vai rodar apenas no Docker")
    sys.exit(0)  # Não falha, apenas avisa
EOF
echo ""

# Verificar docker-compose.yml
echo "🐳 Verificando docker-compose.yml..."
if docker compose config > /dev/null 2>&1; then
    echo -e "${GREEN}✅${NC} docker-compose.yml válido"
else
    echo -e "${RED}❌${NC} docker-compose.yml inválido"
    docker compose config
    exit 1
fi
echo ""

# Verificar migrações
echo "🗄️  Verificando migrações..."
if [ -d "alembic/versions" ] && [ "$(ls -A alembic/versions/*.py 2>/dev/null | grep -v __pycache__ | wc -l)" -gt 0 ]; then
    migration_count=$(ls -1 alembic/versions/*.py 2>/dev/null | grep -v __pycache__ | wc -l | tr -d ' ')
    echo -e "${GREEN}✅${NC} $migration_count migração(ões) encontrada(s)"
else
    echo -e "${YELLOW}⚠️${NC} Nenhuma migração encontrada"
fi
echo ""

# Resumo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✅ Verificação concluída!${NC}"
echo ""
echo "📋 Próximos passos:"
echo "   1. Revise o arquivo .env se necessário"
echo "   2. Execute: docker compose up -d"
echo "   3. Aplique migrações: docker compose exec api-service alembic upgrade head"
echo "   4. Acesse: http://localhost:8000/docs"
echo ""

