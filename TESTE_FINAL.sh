#!/bin/bash

echo "🧪 BATERIA COMPLETA DE TESTES"
echo "================================"
echo ""

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PASSED=0
FAILED=0

test_result() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ PASSOU${NC}"
        ((PASSED++))
    else
        echo -e "${RED}❌ FALHOU${NC}"
        ((FAILED++))
    fi
    echo ""
}

echo "1. Verificando serviços Docker..."
docker ps | grep -q bom_jesus_backend && docker ps | grep -q bom_jesus_db && docker ps | grep -q bom_jesus_redis
test_result

echo "2. Testando Health Check da Aplicação..."
curl -s http://localhost:8000/api/v1/health | grep -q "healthy"
test_result

echo "3. Testando Health Check do Banco..."
curl -s http://localhost:8000/api/v1/db/health | grep -q "ok"
test_result

echo "4. Testando Endpoint Raiz..."
curl -s http://localhost:8000/ | grep -q "Bem-vindo"
test_result

echo "5. Testando Swagger UI..."
curl -s http://localhost:8000/docs | grep -q "swagger"
test_result

echo "6. Verificando PostgreSQL..."
docker exec bom_jesus_db psql -U postgres -d bom_jesus_db -c "SELECT 1;" > /dev/null 2>&1
test_result

echo "7. Verificando Redis..."
docker exec bom_jesus_redis redis-cli ping | grep -q "PONG"
test_result

echo "8. Verificando Tabelas..."
docker exec bom_jesus_db psql -U postgres -d bom_jesus_db -c "\dt" | grep -q "users"
test_result

echo "================================"
echo -e "${GREEN}PASSARAM: $PASSED${NC}"
echo -e "${RED}FALHARAM: $FAILED${NC}"
echo "================================"

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 TODOS OS TESTES PASSARAM!${NC}"
    exit 0
else
    echo -e "${RED}⚠️  Alguns testes falharam${NC}"
    exit 1
fi
