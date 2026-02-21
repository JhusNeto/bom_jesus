# MVP Sistema Operacional Bom Jesus

Implementacao inicial do MVP com:

- `frontend`: React + Vite + PWA + IndexedDB offline queue
- `backend`: NestJS + Prisma + PostgreSQL
- `docker-compose.yml`: stack local portavel

## Subir local (sem Docker)

1. Backend:
   - `cd backend`
   - `cp .env.example .env`
   - `npm install`
   - `npm run prisma:generate`
   - `npm run prisma:migrate`
   - `npm run start:dev`
2. Frontend:
   - `cd frontend`
   - `cp .env.example .env`
   - `npm install`
   - `npm run dev`

## Subir com Docker

- `docker compose up`

## Credencial default (seed no bootstrap)

- Email: `admin@bomjesus.local`
- Senha: `admin1234`

## Endpoints principais

- Prefixo global: `/v1`
- OpenAPI: `GET /v1/docs` (JSON em `/v1/docs-json`)
- `POST /v1/auth/login`
- `POST /v1/auth/refresh`
- `POST /v1/auth/logout`
- `GET /v1/auth/me`
- `GET/POST /v1/products`
- `GET/POST /v1/locations`
- `GET/POST /v1/clients`
- `GET/POST /v1/stores`
- `GET/POST /v1/catalog/reasons`
- `POST /v1/events` (ingestao RAW unificada)
- `GET /v1/events` (historico com filtros)
- `GET /v1/events/raw?status=PENDING|PROCESSED|FAILED`
- `GET /v1/events/raw/export.csv?status=&eventType=&idempotencyKey=&from=&to=&limit=`
- `POST /v1/events/process?limit=100`
- `POST /v1/events/reprocess/:id`
- `POST /v1/events/reprocess-failed?limit=100`
- `GET /v1/events/metrics`
- `POST /v1/lots/entry`
- `POST /v1/lots/:id/move`
- `POST /v1/losses`
- `POST /v1/returns`
- `POST /v1/uploads` (multipart)
- `POST /v1/uploads/photo/presign`
- `GET /v1/dashboard/summary`
- `GET /v1/dashboard/timeseries?days=7&from=&to=&clientId=`
- `GET /v1/dashboard/kpis?from=&to=&clientId=`
- `GET /v1/dashboard/trends?days=7&from=&to=&clientId=`
- `GET /v1/dashboard/export/kpis.csv`
- `GET /v1/dashboard/export/trends.csv?days=7`
- `GET /v1/review/needs-review?resolved=false`
- `PATCH /v1/review/needs-review/:id`
- `GET /v1/reviews/validation-issues?resolved=false`
- `PATCH /v1/reviews/validation-issues/:id/resolve`
- `GET /v1/validation-rules`
- `PATCH /v1/validation-rules`
- `GET /v1/alerts/rules` (ADMIN/MANAGER)
- `PATCH /v1/alerts/rules/:id` (ADMIN)
- `GET /v1/alerts/events` (ADMIN/MANAGER)
- `POST /v1/alerts/push-subscription` (auth)
- `GET /v1/alerts/vapid-public-key` (auth)

## Notas

- Validacao permissiva: bloqueia apenas campos essenciais.
- Regras minimas por evento:
  - `LOT_ENTRY_REGISTERED`: `productId`, `locationId`, e `boxes` ou `kg`.
  - `LOT_MOVED`: `lotId`, `fromLocationId`, `toLocationId`, e `boxes` ou `kg`.
  - `LOSS_REGISTERED`: `lotId` ou `productId`, `locationId`, `reason`, e `boxes` ou `kg`.
  - `RETURN_REGISTERED`: `clientId`, `storeId`, `productId`, `reason`, e `boxes` ou `kg`.
- Ranges/tempo configuraveis sem redeploy (persistidos em banco):
  - `QTY_BOXES_MAX` (default `2000`)
  - `QTY_KG_MAX` (default `50000`)
  - `EVENT_FUTURE_MINUTES_MAX` (default `5`)
  - `EVENT_PAST_DAYS_MAX` (default `7`)
  - `MATURE_STOCK_ALERT_BOXES` (default `300`)
- `GET /validation-rules` retorna os valores efetivos; `PATCH /validation-rules` atualiza em runtime.
- Divergencias de saldo geram `validation_issue`, sem bloquear operacao.
- Todo input operacional cria evento RAW idempotente.
- Upload de foto suporta URL pre-assinada S3-compatível quando variaveis S3 estao configuradas.
- RBAC por papel em rotas protegidas via bearer JWT.
- Autenticacao usa JWT de acesso + refresh token rotativo com expiracao.
- Login usa senha com hash (`bcrypt`) e migra senha legada em texto puro no primeiro login bem-sucedido.
- Criacao de cadastros criticos gera trilha em `AuditLog`.
- Pipeline CAPTURE->VALIDATE->RAW->CLEAN: eventos entram em `RawEvent` com `validationStatus/processingStatus` e jobs processam para tabelas CLEAN com `sourceRawEventId`.
- Classificacao de validacao no backend:
  - `VALID`: sem inconsistencias.
  - `NEEDS_REVIEW`: fora de faixa/tempo, mas sem faltar campo essencial.
  - `INVALID`: falta de campos essenciais.
- Reprocessamento idempotente: `POST /events/reprocess/:id` reprojeta o RAW sem duplicar registros CLEAN vinculados.
- Reprocessamento operacional em lote: `POST /events/reprocess-failed`.
- RAW imutavel no banco: trigger bloqueia `UPDATE/DELETE` em `"RawEvent"`.
- Estado do pipeline separado em `"RawEventProcessingState"` (validate/process metadata).
- Schemas logicos expostos: `raw.events`, `auth.users`, `clean.*`.
- Consumo CLEAN com materialized views: `clean.estoque_atual`, `clean.maturacao_atual`, `clean.devolucoes_clientes`, `clean.perdas_mensal`.
- Alertas: regras em `AlertRule`, eventos em `AlertEvent`. Job `runAlerts` a cada 10 min. Regras: estoque madura, perdas dia, devolucoes cliente, backlog RAW. Canais: PWA push + e-mail. Configure `SMTP_*` e `VAPID_*` no `.env`.
- Runbook de reprocessamento: `docs/pipeline-reprocess-runbook.md`.
- Segurança/auditoria: `docs/security-rbac-audit-checklist.md`.
- Backup/restore: `scripts/backup-postgres.sh`, `scripts/restore-postgres.sh`, `docs/backup-restore-runbook.md`.
- Teste backup+restore: `./scripts/test-backup-restore.sh --docker`.
- Testes: `cd backend && npm test` (unit), `npm run test:e2e` (integration), `cd frontend && npm run test:e2e` (Playwright).
- Rollout: `docs/rollout-plan.md`, `docs/uat-checklist.md`, `docs/go-live-checklist.md`.
- Runbook de ajuste de regras permissivas: `docs/validation-rules-runbook.md`.
- SQLs e benchmark do dashboard: `docs/dashboard-consume-queries.md`.
- API e integracoes v1 (curl/Postman/Insomnia): `docs/api-v1-integrations.md`.
