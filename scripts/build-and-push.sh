#!/bin/bash

# Script para build e push das imagens Docker
# Sistema Operacional Bom Jesus

set -e

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "🚀 Build e Push das Imagens Docker"
echo "===================================="
echo ""

# Variáveis
DOCKER_REGISTRY=${DOCKER_REGISTRY:-bomjesus}
IMAGE_TAG=${IMAGE_TAG:-latest}
BACKEND_IMAGE="${DOCKER_REGISTRY}/backend"
FRONTEND_IMAGE="${DOCKER_REGISTRY}/frontend"

# Verificar se está logado no Docker Hub
echo "🔐 Verificando login no Docker Hub..."
if ! docker info | grep -q Username; then
    echo -e "${YELLOW}⚠️  Não está logado no Docker Hub${NC}"
    echo "Fazendo login..."
    docker login
else
    echo -e "${GREEN}✅ Já está logado no Docker Hub${NC}"
fi

echo ""
echo "📦 Build e Push do Backend"
echo "------------------------------------"

# Build do backend
echo "🔨 Fazendo build do backend..."
docker build -f Dockerfile.backend -t ${BACKEND_IMAGE}:${IMAGE_TAG} .

# Tag adicional para latest (se não for already)
if [ "${IMAGE_TAG}" != "latest" ]; then
    docker tag ${BACKEND_IMAGE}:${IMAGE_TAG} ${BACKEND_IMAGE}:latest
fi

# Push do backend
echo "📤 Fazendo push do backend..."
docker push ${BACKEND_IMAGE}:${IMAGE_TAG}
if [ "${IMAGE_TAG}" != "latest" ]; then
    docker push ${BACKEND_IMAGE}:latest
fi

echo -e "${GREEN}✅ Backend buildado e publicado!${NC}"
echo ""

echo "📦 Build e Push do Frontend"
echo "------------------------------------"

# Build do frontend
echo "🔨 Fazendo build do frontend..."
cd frontend
docker build -f Dockerfile.frontend -t ${FRONTEND_IMAGE}:${IMAGE_TAG} .

# Tag adicional para latest (se não for already)
if [ "${IMAGE_TAG}" != "latest" ]; then
    docker tag ${FRONTEND_IMAGE}:${IMAGE_TAG} ${FRONTEND_IMAGE}:latest
fi

# Push do frontend
echo "📤 Fazendo push do frontend..."
docker push ${FRONTEND_IMAGE}:${IMAGE_TAG}
if [ "${IMAGE_TAG}" != "latest" ]; then
    docker push ${FRONTEND_IMAGE}:latest
fi

cd ..

echo -e "${GREEN}✅ Frontend buildado e publicado!${NC}"
echo ""

echo "===================================="
echo -e "${GREEN}✅ Build e Push concluídos com sucesso!${NC}"
echo ""
echo "📋 Imagens publicadas:"
echo "   - ${BACKEND_IMAGE}:${IMAGE_TAG}"
echo "   - ${FRONTEND_IMAGE}:${IMAGE_TAG}"
echo ""
echo "🔗 Verifique em: https://hub.docker.com/u/${DOCKER_REGISTRY}"

