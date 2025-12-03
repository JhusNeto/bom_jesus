#!/bin/bash

# Script para rodar o projeto via Docker
# Sistema Operacional Bom Jesus - Backend

set -e

echo "🐳 Configurando e executando Sistema Operacional Bom Jesus via Docker"
echo ""

# Verificar se Docker está instalado
if ! command -v docker &> /dev/null; then
    echo "❌ Docker não encontrado. Por favor, instale o Docker."
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! command -v docker compose &> /dev/null; then
    echo "❌ Docker Compose não encontrado. Por favor, instale o Docker Compose."
    exit 1
fi

# Detectar comando do Docker Compose
DOCKER_COMPOSE_CMD="docker compose"
if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker-compose"
fi

echo "✅ Docker encontrado"

# Verificar se .env existe
if [ ! -f ".env" ]; then
    echo "📝 Criando arquivo .env a partir do env.example..."
    cp env.example .env
    echo "✅ Arquivo .env criado"
    echo "⚠️  IMPORTANTE: Edite o arquivo .env com suas configurações antes de continuar"
    echo ""
    read -p "Deseja editar o .env agora? (s/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        ${EDITOR:-nano} .env
    fi
else
    echo "✅ Arquivo .env já existe"
fi

# Verificar se há containers rodando
if [ "$(docker ps -q -f name=bom_jesus)" ]; then
    echo "⚠️  Containers já estão rodando"
    read -p "Deseja parar e recriar? (s/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        echo "🛑 Parando containers..."
        $DOCKER_COMPOSE_CMD down
    else
        echo "✅ Usando containers existentes"
        exit 0
    fi
fi

# Detectar comando do Docker Compose
DOCKER_COMPOSE_CMD="docker compose"
if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker-compose"
fi

# Build e start
echo "🔨 Construindo imagens..."
$DOCKER_COMPOSE_CMD build

echo "🚀 Iniciando containers..."
$DOCKER_COMPOSE_CMD up -d

echo ""
echo "⏳ Aguardando serviços iniciarem..."
sleep 5

# Verificar status
echo ""
echo "📊 Status dos containers:"
$DOCKER_COMPOSE_CMD ps

echo ""
echo "✅ Serviços iniciados!"
echo ""
echo "📍 Endpoints disponíveis:"
echo "   - API: http://localhost:8000"
echo "   - Swagger: http://localhost:8000/docs"
echo "   - ReDoc: http://localhost:8000/redoc"
echo "   - Health: http://localhost:8000/api/v1/health"
echo ""
echo "📝 Comandos úteis:"
echo "   - Ver logs: $DOCKER_COMPOSE_CMD logs -f backend"
echo "   - Parar: $DOCKER_COMPOSE_CMD down"
echo "   - Parar e limpar volumes: $DOCKER_COMPOSE_CMD down -v"
echo ""

