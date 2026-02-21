# Dashboard CONSUME - SQL final e performance

## SQLs de referencia (PostgreSQL)

As consultas abaixo representam as versoes finais usadas como base para os endpoints do dashboard.

### 1) Caixas vendidas hoje

```sql
SELECT
  COALESCE(SUM(-"boxesDelta"), 0) AS caixas_vendidas_hoje
FROM "StockMovement"
WHERE "movementType" = 'EXIT'::"MovementType"
  AND "happenedAt"::date = CURRENT_DATE;
```

### 2) Estoque atual por maturacao

```sql
SELECT
  "productId" AS product_id,
  "maturityState" AS maturity_stage,
  SUM("boxes") AS caixas_em_estoque
FROM "Lot"
GROUP BY 1, 2
HAVING SUM("boxes") <> 0
ORDER BY product_id, maturity_stage;
```

### 3) Perdas do dia e do mes

```sql
SELECT
  COALESCE(SUM("boxes") FILTER (WHERE "happenedAt"::date = CURRENT_DATE), 0) AS perdas_hoje_caixas,
  COALESCE(
    SUM("boxes") FILTER (
      WHERE date_trunc('month', "happenedAt") = date_trunc('month', CURRENT_DATE)
    ),
    0
  ) AS perdas_mes_caixas
FROM "LossRecord";
```

### 4) Devolucoes por cliente (janela configuravel)

```sql
SELECT
  c.id AS client_id,
  c.name AS cliente,
  COALESCE(SUM(r."boxes"), 0) AS devolucoes_caixas,
  COUNT(*) AS qtde_registros
FROM "ReturnRecord" r
JOIN "Client" c ON c.id = r."clientId"
WHERE r."happenedAt" >= $1
  AND r."happenedAt" <= $2
  -- opcional:
  -- AND r."clientId" = $3
GROUP BY c.id, c.name
ORDER BY devolucoes_caixas DESC
LIMIT 10;
```

### 5) Serie dos ultimos 7 dias (vendas/perdas/devolucoes)

```sql
WITH days AS (
  SELECT generate_series($1::date, $2::date, interval '1 day')::date AS d
)
SELECT
  days.d,
  COALESCE(v.caixas_vendidas, 0) AS caixas_vendidas,
  COALESCE(p.caixas_perdas, 0) AS caixas_perdas,
  COALESCE(dv.caixas_devolucoes, 0) AS caixas_devolucoes
FROM days
LEFT JOIN (
  SELECT "happenedAt"::date AS d, SUM(-"boxesDelta") AS caixas_vendidas
  FROM "StockMovement"
  WHERE "movementType" = 'EXIT'::"MovementType"
    AND "happenedAt" >= $1
    AND "happenedAt" <= $2
  GROUP BY 1
) v ON v.d = days.d
LEFT JOIN (
  SELECT "happenedAt"::date AS d, SUM("boxes") AS caixas_perdas
  FROM "LossRecord"
  WHERE "happenedAt" >= $1
    AND "happenedAt" <= $2
  GROUP BY 1
) p ON p.d = days.d
LEFT JOIN (
  SELECT "happenedAt"::date AS d, SUM("boxes") AS caixas_devolucoes
  FROM "ReturnRecord"
  WHERE "happenedAt" >= $1
    AND "happenedAt" <= $2
    -- opcional:
    -- AND "clientId" = $3
  GROUP BY 1
) dv ON dv.d = days.d
ORDER BY days.d;
```

## Indices sugeridos/aplicados

- `Lot(productId, maturityState)`
- `ReturnRecord(clientId, happenedAt)`
- Ja existentes e relevantes:
  - `StockMovement(movementType, happenedAt)`
  - `LossRecord(happenedAt)`
  - `ReturnRecord(happenedAt)`

## Teste de performance com dataset sintetico

### Comando

```bash
cd backend
DASHBOARD_PERF_DAYS=30 DASHBOARD_PERF_ROWS_PER_DAY=200 npm run dashboard:perf
```

### O que o script faz

- Gera massa sintetica para `StockMovement`, `LossRecord`, `ReturnRecord`
- Mede latencia de:
  - `getKpis()`
  - `getTrends(7, { clientId })`
- Imprime JSON com volume inserido e tempos em ms
