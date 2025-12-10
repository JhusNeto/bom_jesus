#!/bin/bash
#
# Script Principal de Testes - Sistema Operacional Bom Jesus
# Orquestra todos os testes e gera relatório consolidado
#

set -euo pipefail

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configurações
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
REPORTS_DIR="$PROJECT_ROOT/tests/reports"
TIMESTAMP=$(date +"%Y%m%d-%H%M%S")
REPORT_FILE="$REPORTS_DIR/test-report-$TIMESTAMP"
QUIET=false
VERBOSE=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --quiet|-q)
            QUIET=true
            shift
            ;;
        --verbose|-v)
            VERBOSE=true
            shift
            ;;
        *)
            echo "Opção desconhecida: $1"
            echo "Uso: $0 [--quiet|--verbose]"
            exit 1
            ;;
    esac
done

# Funções auxiliares
log_info() {
    if [ "$QUIET" = false ]; then
        echo -e "${BLUE}ℹ${NC} $1"
    fi
}

log_success() {
    if [ "$QUIET" = false ]; then
        echo -e "${GREEN}✅${NC} $1"
    fi
}

log_error() {
    echo -e "${RED}❌${NC} $1" >&2
}

log_warning() {
    if [ "$QUIET" = false ]; then
        echo -e "${YELLOW}⚠️${NC} $1"
    fi
}

log_verbose() {
    if [ "$VERBOSE" = true ] && [ "$QUIET" = false ]; then
        echo -e "${BLUE}[VERBOSE]${NC} $1"
    fi
}

# Criar diretório de relatórios
mkdir -p "$REPORTS_DIR"

# Banner
if [ "$QUIET" = false ]; then
    echo ""
    echo "════════════════════════════════════════════════════════════"
    echo "  🧪 SUITE DE TESTES - Sistema Operacional Bom Jesus"
    echo "════════════════════════════════════════════════════════════"
    echo ""
    echo "Timestamp: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "Diretório de relatórios: $REPORTS_DIR"
    echo ""
fi

# Contadores
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Função para executar teste e registrar resultado
run_test() {
    local test_name="$1"
    local test_command="$2"
    local test_category="${3:-general}"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    log_info "Testando: $test_name"
    
    if eval "$test_command" > /tmp/test_output_$$.log 2>&1; then
        PASSED_TESTS=$((PASSED_TESTS + 1))
        log_success "$test_name"
        # Escrever resultado JSON (adicionar ao array)
        result_json="{\"name\": \"$test_name\", \"status\": \"PASSED\", \"category\": \"$test_category\", \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"}"
        # Remover último ] e adicionar vírgula se necessário
        if [ -s "$REPORT_FILE-infra.json" ] && [ "$(tail -c 2 "$REPORT_FILE-infra.json" | tr -d '\n')" != "[]" ]; then
            sed -i '' '$ s/]$/,/' "$REPORT_FILE-infra.json" 2>/dev/null || sed -i '$ s/]$/,/' "$REPORT_FILE-infra.json"
        fi
        echo "$result_json" >> "$REPORT_FILE-infra.json"
        echo "]" >> "$REPORT_FILE-infra.json"
        return 0
    else
        FAILED_TESTS=$((FAILED_TESTS + 1))
        log_error "$test_name"
        local error_output=$(cat /tmp/test_output_$$.log | head -c 500 | tr -d '\n' | sed 's/"/\\"/g')
        # Escrever resultado JSON (adicionar ao array)
        result_json="{\"name\": \"$test_name\", \"status\": \"FAILED\", \"category\": \"$test_category\", \"error\": \"$error_output\", \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"}"
        # Remover último ] e adicionar vírgula se necessário
        if [ -s "$REPORT_FILE-infra.json" ] && [ "$(tail -c 2 "$REPORT_FILE-infra.json" | tr -d '\n')" != "[]" ]; then
            sed -i '' '$ s/]$/,/' "$REPORT_FILE-infra.json" 2>/dev/null || sed -i '$ s/]$/,/' "$REPORT_FILE-infra.json"
        fi
        echo "$result_json" >> "$REPORT_FILE-infra.json"
        echo "]" >> "$REPORT_FILE-infra.json"
        if [ "$VERBOSE" = true ]; then
            log_verbose "Erro: $error_output"
        fi
        return 1
    fi
}

# Inicializar arquivo JSON de relatórios de infraestrutura
touch "$REPORT_FILE-infra.json"
echo "[]" > "$REPORT_FILE-infra.json"

# ============================================
# 1. TESTES DE INFRAESTRUTURA
# ============================================
if [ "$QUIET" = false ]; then
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  1. TESTES DE INFRAESTRUTURA"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
fi

# Verificar se Docker está rodando
run_test "Docker está rodando" "docker ps > /dev/null 2>&1" "infrastructure"

# Verificar containers
run_test "Container backend rodando" "docker ps --format '{{.Names}}' | grep -q 'bom_jesus_backend'" "infrastructure"
run_test "Container database rodando" "docker ps --format '{{.Names}}' | grep -q 'bom_jesus_db'" "infrastructure"
run_test "Container redis rodando" "docker ps --format '{{.Names}}' | grep -q 'bom_jesus_redis'" "infrastructure"

# Verificar health dos containers (tentar ambos os nomes possíveis)
run_test "Backend está healthy" "(docker inspect bom_jesus_backend_dev --format '{{.State.Health.Status}}' 2>/dev/null | grep -q 'healthy') || (docker inspect bom_jesus_backend_dev --format '{{.State.Status}}' 2>/dev/null | grep -q 'running') || (docker inspect bom_jesus_backend --format '{{.State.Status}}' 2>/dev/null | grep -q 'running')" "infrastructure"
run_test "Database está healthy" "(docker inspect bom_jesus_db_dev --format '{{.State.Health.Status}}' 2>/dev/null | grep -q 'healthy') || (docker inspect bom_jesus_db_dev --format '{{.State.Status}}' 2>/dev/null | grep -q 'running') || (docker inspect bom_jesus_db --format '{{.State.Status}}' 2>/dev/null | grep -q 'running')" "infrastructure"
run_test "Redis está healthy" "(docker inspect bom_jesus_redis_dev --format '{{.State.Health.Status}}' 2>/dev/null | grep -q 'healthy') || (docker inspect bom_jesus_redis_dev --format '{{.State.Status}}' 2>/dev/null | grep -q 'running') || (docker inspect bom_jesus_redis --format '{{.State.Status}}' 2>/dev/null | grep -q 'running')" "infrastructure"

# Verificar portas
run_test "Porta 8000 está aberta" "nc -z localhost 8000 || curl -s http://localhost:8000 > /dev/null" "infrastructure"
run_test "Porta 5433 está aberta" "nc -z localhost 5433" "infrastructure"
run_test "Porta 6379 está aberta" "nc -z localhost 6379" "infrastructure"

# ============================================
# 2. TESTES DE API (via Python)
# ============================================
if [ "$QUIET" = false ]; then
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  2. TESTES DE API"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
fi

if [ -f "$SCRIPT_DIR/test-api.py" ]; then
    log_info "Executando testes de API..."
    if python3 "$SCRIPT_DIR/test-api.py" --output "$REPORT_FILE-api.json"; then
        log_success "Testes de API concluídos"
        # Mesclar resultados JSON (se jq estiver disponível)
        if [ -f "$REPORT_FILE-api.json" ] && command -v jq &> /dev/null; then
            jq -s '.[0] + .[1]' "$REPORT_FILE.json" "$REPORT_FILE-api.json" > "$REPORT_FILE.json.tmp" && mv "$REPORT_FILE.json.tmp" "$REPORT_FILE.json" || true
        elif [ -f "$REPORT_FILE-api.json" ]; then
            # Sem jq, usar o arquivo de API como principal
            cp "$REPORT_FILE-api.json" "$REPORT_FILE.json"
        fi
    else
        log_error "Alguns testes de API falharam"
    fi
else
    log_warning "Script test-api.py não encontrado, pulando testes de API"
fi

# ============================================
# 3. TESTES DE BANCO DE DADOS
# ============================================
if [ "$QUIET" = false ]; then
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  3. TESTES DE BANCO DE DADOS"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
fi

if [ -f "$SCRIPT_DIR/test-database.py" ]; then
    log_info "Executando testes de banco de dados..."
    if python3 "$SCRIPT_DIR/test-database.py" --output "$REPORT_FILE-db.json"; then
        log_success "Testes de banco de dados concluídos"
        if [ -f "$REPORT_FILE-db.json" ] && command -v jq &> /dev/null; then
            jq -s '.[0] + .[1]' "$REPORT_FILE.json" "$REPORT_FILE-db.json" > "$REPORT_FILE.json.tmp" && mv "$REPORT_FILE.json.tmp" "$REPORT_FILE.json" || true
        fi
    else
        log_error "Alguns testes de banco de dados falharam"
    fi
else
    log_warning "Script test-database.py não encontrado, pulando testes de banco"
fi

# ============================================
# 4. TESTES DE REDIS
# ============================================
if [ "$QUIET" = false ]; then
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  4. TESTES DE REDIS"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
fi

    if [ -f "$SCRIPT_DIR/test-redis.py" ]; then
    log_info "Executando testes de Redis..."
    if python3 "$SCRIPT_DIR/test-redis.py" --output "$REPORT_FILE-redis.json"; then
        log_success "Testes de Redis concluídos"
        if [ -f "$REPORT_FILE-redis.json" ] && command -v jq &> /dev/null; then
            jq -s '.[0] + .[1]' "$REPORT_FILE.json" "$REPORT_FILE-redis.json" > "$REPORT_FILE.json.tmp" && mv "$REPORT_FILE.json.tmp" "$REPORT_FILE.json" || true
        fi
    else
        log_error "Alguns testes de Redis falharam"
    fi
else
    log_warning "Script test-redis.py não encontrado, pulando testes de Redis"
fi

# ============================================
# 5. TESTES DE FRONTEND
# ============================================
if [ "$QUIET" = false ]; then
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  5. TESTES DE FRONTEND"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
fi
    
    if [ -f "$SCRIPT_DIR/test-frontend.sh" ]; then
    log_info "Executando testes de frontend..."
    if bash "$SCRIPT_DIR/test-frontend.sh" --output "$REPORT_FILE-frontend.json"; then
        log_success "Testes de frontend concluídos"
        if [ -f "$REPORT_FILE-frontend.json" ]; then
            jq -s '.[0] + .[1]' "$REPORT_FILE.json" "$REPORT_FILE-frontend.json" > "$REPORT_FILE.json.tmp" && mv "$REPORT_FILE.json.tmp" "$REPORT_FILE.json"
        fi
    else
        log_error "Alguns testes de frontend falharam"
    fi
else
    log_warning "Script test-frontend.sh não encontrado, pulando testes de frontend"
fi

# Consolidar todos os resultados JSON em um único arquivo
all_jsons=()
[ -f "$REPORT_FILE-infra.json" ] && all_jsons+=("$REPORT_FILE-infra.json")
[ -f "$REPORT_FILE-api.json" ] && all_jsons+=("$REPORT_FILE-api.json")
[ -f "$REPORT_FILE-db.json" ] && all_jsons+=("$REPORT_FILE-db.json")
[ -f "$REPORT_FILE-redis.json" ] && all_jsons+=("$REPORT_FILE-redis.json")
[ -f "$REPORT_FILE-frontend.json" ] && all_jsons+=("$REPORT_FILE-frontend.json")

if [ ${#all_jsons[@]} -gt 0 ]; then
    if command -v jq &> /dev/null; then
        # Usar jq para mesclar
        jq -s 'add' "${all_jsons[@]}" > "$REPORT_FILE.json" 2>/dev/null || {
            # Fallback: concatenar manualmente
            echo "[" > "$REPORT_FILE.json"
            first=true
            for json_file in "${all_jsons[@]}"; do
                if [ -f "$json_file" ] && [ -s "$json_file" ]; then
                    if [ "$first" = false ]; then
                        echo "," >> "$REPORT_FILE.json"
                    fi
                    # Remover [ ] externos e adicionar conteúdo
                    sed '1d;$d' "$json_file" >> "$REPORT_FILE.json"
                    first=false
                fi
            done
            echo "]" >> "$REPORT_FILE.json"
        }
    else
        # Sem jq: concatenar manualmente
        echo "[" > "$REPORT_FILE.json"
        first=true
        for json_file in "${all_jsons[@]}"; do
            if [ -f "$json_file" ] && [ -s "$json_file" ]; then
                if [ "$first" = false ]; then
                    echo "," >> "$REPORT_FILE.json"
                fi
                # Remover [ ] externos e adicionar conteúdo
                sed '1d;$d' "$json_file" >> "$REPORT_FILE.json" 2>/dev/null || cat "$json_file" >> "$REPORT_FILE.json"
                first=false
            fi
        done
        echo "]" >> "$REPORT_FILE.json"
    fi
fi

# ============================================
# 6. GERAR RELATÓRIO CONSOLIDADO
# ============================================
if [ "$QUIET" = false ]; then
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  6. GERANDO RELATÓRIO CONSOLIDADO"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
fi

    if [ -f "$SCRIPT_DIR/generate-report.py" ]; then
    log_info "Gerando relatório Markdown..."
    if [ -f "$REPORT_FILE.json" ]; then
        if python3 "$SCRIPT_DIR/generate-report.py" --input "$REPORT_FILE.json" --output "$REPORT_FILE.md"; then
            log_success "Relatório gerado: $REPORT_FILE.md"
        else
            log_error "Erro ao gerar relatório"
        fi
    else
        log_warning "Arquivo JSON consolidado não encontrado, pulando geração de relatório"
    fi
else
    log_warning "Script generate-report.py não encontrado, pulando geração de relatório"
fi

# ============================================
# RESUMO FINAL
# ============================================
if [ "$QUIET" = false ]; then
    echo ""
    echo "════════════════════════════════════════════════════════════"
    echo "  📊 RESUMO DOS TESTES"
    echo "════════════════════════════════════════════════════════════"
    echo ""
    echo "Total de testes: $TOTAL_TESTS"
    echo -e "${GREEN}Passaram: $PASSED_TESTS${NC}"
    echo -e "${RED}Falharam: $FAILED_TESTS${NC}"
    echo ""
    
    if [ $FAILED_TESTS -eq 0 ]; then
        echo -e "${GREEN}🎉 TODOS OS TESTES PASSARAM!${NC}"
        echo ""
        exit 0
    else
        echo -e "${RED}⚠️  Alguns testes falharam. Verifique o relatório:${NC}"
        echo "   $REPORT_FILE.md"
        echo "   $REPORT_FILE.json"
        echo ""
        exit 1
    fi
else
    # Modo quiet: apenas código de saída
    if [ $FAILED_TESTS -eq 0 ]; then
                exit 0
    else
                exit 1
    fi
fi
