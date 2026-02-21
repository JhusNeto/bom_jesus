# Runbook de regras de validacao

Este documento explica como ajustar faixas de validacao sem redeploy.

## Objetivo

- Manter validacao permissiva no operacional.
- Evitar bloqueio de operador por regras nao essenciais.
- Ajustar thresholds em runtime via API.

## Chaves disponiveis

- `QTY_BOXES_MAX`
- `QTY_KG_MAX`
- `EVENT_FUTURE_MINUTES_MAX`
- `EVENT_PAST_DAYS_MAX`
- `MATURE_STOCK_ALERT_BOXES`

## Consultar regras vigentes

`GET /validation-rules`

Resposta exemplo:

```json
{
  "QTY_BOXES_MAX": 2000,
  "QTY_KG_MAX": 50000,
  "EVENT_FUTURE_MINUTES_MAX": 5,
  "EVENT_PAST_DAYS_MAX": 7,
  "MATURE_STOCK_ALERT_BOXES": 300
}
```

## Atualizar uma regra

`PATCH /validation-rules`

Payload exemplo:

```json
{
  "key": "QTY_BOXES_MAX",
  "valueNumber": 2500
}
```

## Efeito operacional

- Novos eventos passam a usar imediatamente o valor atualizado.
- Eventos ja processados nao sao alterados automaticamente.
- Se necessario, use reprocessamento RAW para reprojetar no CLEAN.
