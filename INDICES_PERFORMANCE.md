# 📊 Índices de Performance - Sistema Operacional Bom Jesus

## Visão Geral

Este documento descreve os índices de performance implementados no banco de dados para otimizar queries comuns e melhorar a performance geral do sistema.

**Migration**: `e0f88042950c_add_performance_indexes`

---

## 🎯 Estratégia de Indexação

### 1. **Índices Simples em Campos de Data**
Otimizam ordenação e filtros temporais (WHERE, ORDER BY).

### 2. **Índices Compostos**
Otimizam queries que filtram por múltiplos campos simultaneamente (ex: cliente + status).

### 3. **Índices em Campos de Busca**
Otimizam buscas por texto (LIKE queries) em campos como fornecedor, cidade, bairro.

### 4. **Índices em Campos de Filtro**
Otimizam filtros booleanos e de status (is_active, devolucao).

---

## 📋 Índices Implementados

### **Índices Simples - Campos de Data**

| Tabela | Campo | Índice | Uso |
|--------|-------|--------|-----|
| `cargas` | `data_chegada` | `ix_cargas_data_chegada` | Buscar cargas por data de chegada |
| `cargas` | `created_at` | `ix_cargas_created_at` | Ordenação por data de criação |
| `pedidos` | `created_at` | `ix_pedidos_created_at` | Ordenação por data de criação |
| `pesagens` | `created_at` | `ix_pesagens_created_at` | Ordenação por data de criação |
| `movimentacoes_camara` | `created_at` | `ix_movimentacoes_camara_created_at` | Ordenação por data de criação |
| `perdas` | `created_at` | `ix_perdas_created_at` | Ordenação por data de criação |
| `devolucoes` | `created_at` | `ix_devolucoes_created_at` | Ordenação por data de criação |
| `gastos_internos` | `created_at` | `ix_gastos_internos_created_at` | Ordenação por data de criação |
| `logs_operacionais` | `created_at` | `ix_logs_operacionais_created_at` | Ordenação por data de criação |
| `ocr_inputs` | `created_at` | `ix_ocr_inputs_created_at` | Ordenação por data de criação |
| `rotas` | `created_at` | `ix_rotas_created_at` | Ordenação por data de criação |
| `entregas_cliente` | `created_at` | `ix_entregas_cliente_created_at` | Ordenação por data de criação |
| `users` | `created_at` | `ix_users_created_at` | Ordenação por data de criação |
| `auth_tokens` | `created_at` | `ix_auth_tokens_created_at` | Ordenação por data de criação |

**Total**: 14 índices simples de data

---

### **Índices Compostos - Queries Frequentes**

| Tabela | Campos | Índice | Query Otimizada |
|--------|--------|--------|-----------------|
| `pedidos` | `cliente_id, status` | `ix_pedidos_cliente_status` | Pedidos de um cliente por status |
| `pedidos` | `cliente_id, data` | `ix_pedidos_cliente_data` | Pedidos de um cliente por período |
| `pesagens` | `cliente_id, status` | `ix_pesagens_cliente_status` | Pesagens de um cliente por status |
| `pesagens` | `carga_id, status` | `ix_pesagens_carga_status` | Pesagens de uma carga por status |
| `movimentacoes_camara` | `camara_id, tipo_movimento, data` | `ix_movimentacoes_camara_camara_tipo_data` | Movimentações por câmara, tipo e data |
| `movimentacoes_camara` | `camara_id, data` | `ix_movimentacoes_camara_camara_data` | Movimentações por câmara e data |
| `perdas` | `carga_id, data` | `ix_perdas_carga_data` | Perdas de uma carga por data |
| `logs_operacionais` | `usuario_id, tipo, data` | `ix_logs_operacionais_usuario_tipo_data` | Logs por usuário, tipo e data |
| `logs_operacionais` | `tipo, data` | `ix_logs_operacionais_tipo_data` | Logs por tipo e data (auditoria) |
| `auth_tokens` | `user_id, is_active, expires_at` | `ix_auth_tokens_user_active_expires` | Tokens ativos de um usuário |
| `itens_pedido` | `pedido_id, tipo_banana` | `ix_itens_pedido_pedido_tipo` | Itens de um pedido por tipo |
| `entregas_cliente` | `rota_id, cliente_id` | `ix_entregas_cliente_rota_cliente` | Entregas por rota e cliente |
| `devolucoes` | `cliente_id, pedido_id` | `ix_devolucoes_cliente_pedido` | Devoluções por cliente e pedido |

**Total**: 13 índices compostos

---

### **Índices - Campos de Busca**

| Tabela | Campo | Índice | Uso |
|--------|-------|--------|-----|
| `clientes` | `cidade` | `ix_clientes_cidade` | Buscar clientes por cidade |
| `clientes` | `bairro` | `ix_clientes_bairro` | Buscar clientes por bairro |
| `cargas` | `fornecedor` | `ix_cargas_fornecedor` | Buscar cargas por fornecedor |
| `cargas` | `fazenda` | `ix_cargas_fazenda` | Buscar cargas por fazenda |

**Total**: 4 índices de busca

---

### **Índices - Campos de Filtro**

| Tabela | Campo | Índice | Uso |
|--------|-------|--------|-----|
| `users` | `is_active` | `ix_users_is_active` | Filtrar usuários ativos/inativos |
| `entregas_cliente` | `devolucao` | `ix_entregas_cliente_devolucao` | Filtrar entregas com devolução |

**Total**: 2 índices de filtro

---

## 📊 Resumo Total

| Categoria | Quantidade |
|-----------|------------|
| Índices Simples (Data) | 14 |
| Índices Compostos | 13 |
| Índices de Busca | 4 |
| Índices de Filtro | 2 |
| **TOTAL** | **33 índices** |

---

## 🚀 Aplicar Migration

### Via Docker Compose

```bash
# 1. Iniciar os serviços
docker compose up -d

# 2. Aplicar a migration
docker compose exec api-service alembic upgrade head

# Ou executar localmente (se o banco estiver acessível)
alembic upgrade head
```

### Verificar Índices Criados

```sql
-- Listar todos os índices de uma tabela
SELECT 
    indexname, 
    indexdef 
FROM pg_indexes 
WHERE tablename = 'pedidos'
ORDER BY indexname;

-- Ver estatísticas de uso dos índices
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan as index_scans,
    idx_tup_read as tuples_read,
    idx_tup_fetch as tuples_fetched
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan DESC;
```

---

## 🎯 Queries Otimizadas

### Exemplo 1: Buscar Pedidos de um Cliente por Status
```sql
-- ANTES: Full table scan
SELECT * FROM pedidos WHERE cliente_id = ? AND status = ?;

-- DEPOIS: Usa índice ix_pedidos_cliente_status
-- Performance: O(1) lookup em vez de O(n) scan
```

### Exemplo 2: Relatório de Movimentações por Câmara
```sql
-- ANTES: Full table scan + sort
SELECT * FROM movimentacoes_camara 
WHERE camara_id = ? AND data BETWEEN ? AND ?
ORDER BY data;

-- DEPOIS: Usa índice ix_movimentacoes_camara_camara_data
-- Performance: Index scan direto, sem sort necessário
```

### Exemplo 3: Buscar Clientes por Cidade
```sql
-- ANTES: Full table scan com LIKE
SELECT * FROM clientes WHERE cidade LIKE '%São Paulo%';

-- DEPOIS: Usa índice ix_clientes_cidade
-- Performance: Index scan em vez de full scan
```

---

## ⚠️ Considerações Importantes

### 1. **Manutenção de Índices**
- Índices aumentam o espaço em disco
- Índices compostos podem ser grandes
- Atualizações (INSERT/UPDATE/DELETE) são mais lentas com muitos índices
- **Recomendação**: Monitorar uso dos índices e remover os não utilizados

### 2. **Monitoramento**
Execute periodicamente:
```sql
-- Ver índices não utilizados
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan
FROM pg_stat_user_indexes
WHERE schemaname = 'public' 
  AND idx_scan = 0
ORDER BY tablename, indexname;
```

### 3. **Análise de Queries**
Use `EXPLAIN ANALYZE` para verificar se os índices estão sendo utilizados:
```sql
EXPLAIN ANALYZE 
SELECT * FROM pedidos 
WHERE cliente_id = '...' AND status = 'aberto';
```

---

## 📝 Notas de Implementação

- Todos os índices são **NON-UNIQUE** (permitem duplicatas)
- Índices compostos seguem a ordem de campos mais seletivos primeiro
- Campos de data usam ordenação padrão (ASC)
- Índices em campos de texto (String) suportam buscas LIKE, mas para buscas de prefixo são mais eficientes

---

## 🔄 Rollback

Para reverter a migration:

```bash
alembic downgrade -1
```

Ou manualmente:
```sql
-- Remover índices específicos
DROP INDEX IF EXISTS ix_pedidos_cliente_status;
-- ... (ver função downgrade() na migration)
```

---

**Última atualização**: 2025-12-03  
**Migration**: `e0f88042950c_add_performance_indexes`

