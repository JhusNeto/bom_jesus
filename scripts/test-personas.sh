#!/bin/bash
#
# Script de Teste de Personas - Sistema Operacional Bom Jesus
# Testa login e permissões com diferentes roles
#

set -euo pipefail

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configurações
BASE_URL="http://localhost:8000"
API_BASE="${BASE_URL}/api/v1"

# Credenciais de teste (usando arrays separados para compatibilidade)
ROLES=("admin" "manager" "operator" "viewer")
ADMIN_EMAIL="admin@bomjesus.com"
ADMIN_PASS="admin123"
MANAGER_EMAIL="gerente@bomjesus.com"
MANAGER_PASS="gerente123"
OPERATOR_EMAIL="operador@bomjesus.com"
OPERATOR_PASS="operador123"
VIEWER_EMAIL="viewer@bomjesus.com"
VIEWER_PASS="viewer123"

get_user_credentials() {
    local role=$1
    case $role in
        admin) echo "${ADMIN_EMAIL}:${ADMIN_PASS}" ;;
        manager) echo "${MANAGER_EMAIL}:${MANAGER_PASS}" ;;
        operator) echo "${OPERATOR_EMAIL}:${OPERATOR_PASS}" ;;
        viewer) echo "${VIEWER_EMAIL}:${VIEWER_PASS}" ;;
    esac
}

log_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

log_success() {
    echo -e "${GREEN}✅${NC} $1"
}

log_error() {
    echo -e "${RED}❌${NC} $1"
}

log_test() {
    echo -e "${YELLOW}🧪${NC} $1"
}

# Função para fazer login e obter token
login_user() {
    local email=$1
    local password=$2
    
    response=$(curl -s -X POST "${API_BASE}/auth/login" \
        -H "Content-Type: application/json" \
        -d "{\"email\": \"${email}\", \"password\": \"${password}\"}")
    
    if echo "$response" | grep -q "access_token"; then
        echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null
        return 0
    else
        echo ""
        return 1
    fi
}

# Função para testar endpoint com token
test_endpoint() {
    local token=$1
    local endpoint=$2
    local expected_status=$3
    local role_name=$4
    
    response=$(curl -s -w "\n%{http_code}" "${API_BASE}${endpoint}" \
        -H "Authorization: Bearer ${token}")
    
    http_code=$(echo "$response" | tail -1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" = "$expected_status" ]; then
        log_success "${role_name}: ${endpoint} → ${http_code}"
        return 0
    else
        log_error "${role_name}: ${endpoint} → Esperado ${expected_status}, recebido ${http_code}"
        if [ "$http_code" != "200" ]; then
            echo "   Resposta: $body" | head -3
        fi
        return 1
    fi
}

echo "=" | tr '=' '='
echo "  TESTE DE PERSONAS - Sistema Operacional Bom Jesus"
echo "=" | tr '=' '='
echo ""

total_tests=0
passed_tests=0
failed_tests=0

# Testar cada persona
for role in "${ROLES[@]}"; do
    IFS=':' read -r email password <<< "$(get_user_credentials "$role")"
    
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    role_upper=$(echo "$role" | tr '[:lower:]' '[:upper:]')
    echo "  Testando: $role_upper"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Email: $email"
    echo ""
    
    # 1. Testar Login
    log_test "1. Login"
    token=$(login_user "$email" "$password")
    
    if [ -z "$token" ]; then
        log_error "Login falhou para ${role}"
        failed_tests=$((failed_tests + 1))
        continue
    else
        log_success "Login OK - Token obtido"
        passed_tests=$((passed_tests + 1))
    fi
    total_tests=$((total_tests + 1))
    
    # 2. Testar /auth/me
    log_test "2. GET /auth/me"
    if test_endpoint "$token" "/auth/me" "200" "$role"; then
        passed_tests=$((passed_tests + 1))
    else
        failed_tests=$((failed_tests + 1))
    fi
    total_tests=$((total_tests + 1))
    
    # 3. Testar endpoints baseado em role
    log_test "3. Testando permissões por role"
    
    case $role in
        admin)
            # Admin pode acessar tudo
            if test_endpoint "$token" "/auth/admin-only" "200" "$role"; then
                passed_tests=$((passed_tests + 1))
            else
                failed_tests=$((failed_tests + 1))
            fi
            total_tests=$((total_tests + 1))
            
            if test_endpoint "$token" "/auth/manager-or-admin" "200" "$role"; then
                passed_tests=$((passed_tests + 1))
            else
                failed_tests=$((failed_tests + 1))
            fi
            total_tests=$((total_tests + 1))
            ;;
        manager)
            # Manager NÃO pode acessar admin-only
            if test_endpoint "$token" "/auth/admin-only" "403" "$role"; then
                passed_tests=$((passed_tests + 1))
            else
                failed_tests=$((failed_tests + 1))
            fi
            total_tests=$((total_tests + 1))
            
            # Manager PODE acessar manager-or-admin
            if test_endpoint "$token" "/auth/manager-or-admin" "200" "$role"; then
                passed_tests=$((passed_tests + 1))
            else
                failed_tests=$((failed_tests + 1))
            fi
            total_tests=$((total_tests + 1))
            ;;
        operator|viewer)
            # Operator e Viewer NÃO podem acessar admin-only
            if test_endpoint "$token" "/auth/admin-only" "403" "$role"; then
                passed_tests=$((passed_tests + 1))
            else
                failed_tests=$((failed_tests + 1))
            fi
            total_tests=$((total_tests + 1))
            
            # Operator e Viewer NÃO podem acessar manager-or-admin
            if test_endpoint "$token" "/auth/manager-or-admin" "403" "$role"; then
                passed_tests=$((passed_tests + 1))
            else
                failed_tests=$((failed_tests + 1))
            fi
            total_tests=$((total_tests + 1))
            ;;
    esac
    
    # 4. Testar Refresh Token
    log_test "4. POST /auth/refresh"
    # Primeiro faz login para obter refresh token
    login_response=$(curl -s -X POST "${API_BASE}/auth/login" \
        -H "Content-Type: application/json" \
        -d "{\"email\": \"${email}\", \"password\": \"${password}\"}")
    
    refresh_token=$(echo "$login_response" | python3 -c "import sys, json; print(json.load(sys.stdin)['refresh_token'])" 2>/dev/null)
    
    if [ -z "$refresh_token" ]; then
        log_error "${role}: Não foi possível obter refresh token"
        failed_tests=$((failed_tests + 1))
    else
        # Testa refresh
        refresh_response=$(curl -s -X POST "${API_BASE}/auth/refresh" \
            -H "Content-Type: application/json" \
            -d "{\"refresh_token\": \"${refresh_token}\"}")
        
        if echo "$refresh_response" | grep -q "access_token"; then
            log_success "${role}: Refresh token funcionando"
            passed_tests=$((passed_tests + 1))
        else
            log_error "${role}: Refresh token falhou"
            failed_tests=$((failed_tests + 1))
        fi
    fi
    total_tests=$((total_tests + 1))
done

# Resumo
echo ""
echo "=" | tr '=' '='
echo "  RESUMO"
echo "=" | tr '=' '='
echo "Total de testes: $total_tests"
echo -e "${GREEN}✅ Passaram: $passed_tests${NC}"
echo -e "${RED}❌ Falharam: $failed_tests${NC}"
echo ""

if [ $failed_tests -eq 0 ]; then
    echo -e "${GREEN}🎉 TODOS OS TESTES PASSARAM!${NC}"
    exit 0
else
    echo -e "${RED}⚠️  Alguns testes falharam${NC}"
    exit 1
fi

