# Runbook de Reprocessamento RAW

## Objetivo

Garantir reprocessamento seguro e idempotente do pipeline CAPTURE -> VALIDATE -> RAW -> CLEAN -> PROCESS -> CONSUME.

## Conceitos

- RAW imutavel: tabela `"RawEvent"` nao recebe update/delete pela aplicacao.
- Estado operacional: `"RawEventProcessingState"` concentra `validationStatus`, `processingStatus`, `lastError`, `ingestedAt`, `processedAt`.
- Projecoes CLEAN usam `sourceRawEventId` para impedir duplicidade em reprocessamento.

## Endpoints operacionais

- `GET /events/metrics`
- `GET /events/raw?status=PENDING|PROCESSED|FAILED&limit=30`
- `POST /events/process?limit=100`
- `POST /events/reprocess/:id`
- `POST /events/reprocess-failed?limit=100`

## Procedimento recomendado

1. Verificar backlog:
   - chamar `GET /events/metrics`
2. Tratar fila pendente:
   - chamar `POST /events/process?limit=100`
3. Tratar falhas:
   - chamar `GET /events/raw?status=FAILED`
   - revisar `processingState.lastError`
   - chamar `POST /events/reprocess-failed?limit=100`
4. Reprocessar evento especifico (incidente pontual):
   - `POST /events/reprocess/:id`
5. Confirmar resultado:
   - `GET /events/metrics`
   - conferir reducao de `failed` e `pending`

## Materialized views

As views de consumo sao atualizadas por job agendado a cada 5 minutos:

- `clean.estoque_atual`
- `clean.maturacao_atual`
- `clean.devolucoes_clientes`
- `clean.perdas_mensal`

Em incidentes de consistencia, executar refresh manual no banco:

```sql
REFRESH MATERIALIZED VIEW clean.estoque_atual;
REFRESH MATERIALIZED VIEW clean.maturacao_atual;
REFRESH MATERIALIZED VIEW clean.devolucoes_clientes;
REFRESH MATERIALIZED VIEW clean.perdas_mensal;
```

## Critérios de sucesso

- `processing.pending` estabilizado em baixo volume.
- `processing.failed` proximo de zero no dia.
- eventos com erro recorrente possuem correção de payload/regra antes de novo reprocessamento.
