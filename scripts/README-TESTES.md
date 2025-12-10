# 🧪 Suite de Testes - Sistema Operacional Bom Jesus

## Visão Geral

Suite completa de testes automatizados para validar todos os componentes do sistema em ambiente dev.

## Como Usar

### Executar Todos os Testes

```bash
./scripts/test-suite.sh
```

### Modos de Execução

**Modo Interativo (padrão):**
```bash
./scripts/test-suite.sh
```

**Modo Silencioso (apenas códigos de saída):**
```bash
./scripts/test-suite.sh --quiet
```

**Modo Verbose (mais detalhes):**
```bash
./scripts/test-suite.sh --verbose
```

## Scripts Individuais

### Testes de API
```bash
python3 scripts/test-api.py --output test-api-results.json
```

### Testes de Banco de Dados
```bash
python3 scripts/test-database.py --output test-db-results.json
```

### Testes de Redis
```bash
python3 scripts/test-redis.py --output test-redis-results.json
```

### Testes de Frontend
```bash
./scripts/test-frontend.sh --output test-frontend-results.json
```

## Relatórios

Os relatórios são gerados automaticamente em `tests/reports/`:

- **Markdown**: `test-report-YYYYMMDD-HHMMSS.md` - Relatório legível
- **JSON**: `test-report-YYYYMMDD-HHMMSS.json` - Dados estruturados

## Pré-requisitos

### Python
```bash
pip install -r requirements.txt
```

Dependências necessárias:
- `requests` - Para testes HTTP
- `psycopg2-binary` - Para testes de banco
- `redis` - Para testes de Redis

### Sistema
- Docker e Docker Compose rodando
- `curl` - Para testes básicos
- `jq` - Para parsing JSON (opcional, mas recomendado)

## Estrutura dos Testes

### 1. Infraestrutura
- Status dos containers Docker
- Health checks
- Portas expostas

### 2. API
- Endpoints básicos
- Health checks
- Documentação (Swagger, ReDoc)

### 3. Autenticação
- Login
- Refresh token
- Logout
- Proteção de rotas

### 4. Banco de Dados
- Conexão PostgreSQL
- Estrutura de tabelas
- Migrations
- Consultas básicas

### 5. Redis
- Conexão
- Operações de refresh tokens
- TTL e revogação

### 6. Frontend
- Acessibilidade
- Redirecionamentos
- Proteção de rotas

## Interpretando Resultados

### Status dos Testes
- ✅ **PASSED**: Teste passou
- ❌ **FAILED**: Teste falhou
- ⏭️ **SKIPPED**: Teste pulado (dependência não disponível)

### Criticidade de Problemas
- **CRÍTICO**: Sistema não funciona
- **ALTO**: Funcionalidade importante quebrada
- **MÉDIO**: Funcionalidade secundária com problema
- **BAIXO**: Melhorias ou warnings

## Troubleshooting

### Erro: "psycopg2 não instalado"
```bash
pip install psycopg2-binary
```

### Erro: "redis não instalado"
```bash
pip install redis
```

### Erro: "requests não instalado"
```bash
pip install requests
```

### Erro: "Container não encontrado"
Certifique-se de que os containers estão rodando:
```bash
docker compose ps
```

### Erro: "Usuário de teste não encontrado"
Crie o usuário de teste:
```bash
python3 scripts/create-test-user.py
```

## Exemplo de Saída

```
════════════════════════════════════════════════════════════
  🧪 SUITE DE TESTES - Sistema Operacional Bom Jesus
════════════════════════════════════════════════════════════

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  1. TESTES DE INFRAESTRUTURA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Docker está rodando
✅ Container backend rodando
✅ Container database rodando
...

════════════════════════════════════════════════════════════
  📊 RESUMO DOS TESTES
════════════════════════════════════════════════════════════

Total de testes: 50
Passaram: 48
Falharam: 2

🎉 TODOS OS TESTES PASSARAM!
```

## Próximos Passos

Após executar os testes:

1. Analisar relatório Markdown gerado
2. Verificar problemas encontrados
3. Corrigir problemas críticos primeiro
4. Re-executar testes para validação
5. Documentar problemas conhecidos (se houver)

