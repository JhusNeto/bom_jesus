CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS auth;
CREATE SCHEMA IF NOT EXISTS clean;

-- Processing metadata separated from immutable RAW event.
CREATE TABLE IF NOT EXISTS "RawEventProcessingState" (
  "id" TEXT NOT NULL,
  "rawEventId" TEXT NOT NULL,
  "validationStatus" "ValidationStatus" NOT NULL DEFAULT 'VALID',
  "validationErrors" JSONB,
  "processingStatus" "ProcessingStatus" NOT NULL DEFAULT 'PENDING',
  "ingestedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "processedAt" TIMESTAMP(3),
  "lastError" TEXT,
  "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "updatedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT "RawEventProcessingState_pkey" PRIMARY KEY ("id"),
  CONSTRAINT "RawEventProcessingState_rawEventId_fkey" FOREIGN KEY ("rawEventId") REFERENCES "RawEvent"("id") ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE UNIQUE INDEX IF NOT EXISTS "RawEventProcessingState_rawEventId_key"
  ON "RawEventProcessingState" ("rawEventId");
CREATE INDEX IF NOT EXISTS "RawEventProcessingState_processingStatus_ingestedAt_idx"
  ON "RawEventProcessingState" ("processingStatus", "ingestedAt");
CREATE INDEX IF NOT EXISTS "RawEventProcessingState_validationStatus_idx"
  ON "RawEventProcessingState" ("validationStatus");

-- Backfill processing state for existing events.
INSERT INTO "RawEventProcessingState" ("id", "rawEventId", "validationStatus", "validationErrors", "processingStatus", "ingestedAt", "processedAt", "createdAt", "updatedAt")
SELECT
  gen_random_uuid()::text,
  r."id",
  COALESCE(r."validationStatus", 'VALID'::"ValidationStatus"),
  r."validationErrors",
  COALESCE(r."processingStatus", 'PENDING'::"ProcessingStatus"),
  COALESCE(r."ingestedAt", r."receivedAt", r."createdAt"),
  r."processedAt",
  CURRENT_TIMESTAMP,
  CURRENT_TIMESTAMP
FROM "RawEvent" r
LEFT JOIN "RawEventProcessingState" s ON s."rawEventId" = r."id"
WHERE s."rawEventId" IS NULL;

-- Immutable RAW events at DB level: no UPDATE/DELETE from app.
CREATE OR REPLACE FUNCTION raw.prevent_raw_event_mutation()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
  RAISE EXCEPTION 'raw.events are immutable';
END;
$$;

DROP TRIGGER IF EXISTS trg_raw_event_no_update ON "RawEvent";
CREATE TRIGGER trg_raw_event_no_update
BEFORE UPDATE ON "RawEvent"
FOR EACH ROW
EXECUTE FUNCTION raw.prevent_raw_event_mutation();

DROP TRIGGER IF EXISTS trg_raw_event_no_delete ON "RawEvent";
CREATE TRIGGER trg_raw_event_no_delete
BEFORE DELETE ON "RawEvent"
FOR EACH ROW
EXECUTE FUNCTION raw.prevent_raw_event_mutation();

-- Logical schema exposure
CREATE OR REPLACE VIEW raw.events AS
SELECT
  r."id",
  r."eventType"::text AS event_type,
  r."occurredAt" AS event_ts,
  r."deviceId" AS device_id,
  r."userId" AS user_id,
  r."payloadJson" AS payload,
  s."validationStatus"::text AS validation_status,
  s."validationErrors" AS validation_errors,
  s."ingestedAt" AS ingested_at,
  s."processedAt" AS processed_at,
  s."processingStatus"::text AS processing_status,
  r."idempotencyKey" AS idempotency_key
FROM "RawEvent" r
JOIN "RawEventProcessingState" s ON s."rawEventId" = r."id";

CREATE OR REPLACE VIEW auth.users AS
SELECT
  u."id",
  u."name",
  u."email",
  u."password" AS password_hash,
  u."role"::text AS role,
  true AS active
FROM "User" u;

-- Replace regular views by materialized views for dashboard consumption.
DROP VIEW IF EXISTS clean.estoque_atual;
DROP VIEW IF EXISTS clean.maturacao_atual;
DROP VIEW IF EXISTS clean.devolucoes_clientes;
DROP VIEW IF EXISTS clean.perdas_mensal;

CREATE MATERIALIZED VIEW clean.estoque_atual AS
SELECT
  l."productId" AS product_id,
  COALESCE(sm."toLocationId", l."currentLocationId") AS location_id,
  l."maturityState"::text AS maturity_stage,
  SUM(sm."boxesDelta")::numeric AS saldo_boxes,
  SUM(COALESCE(sm."kgDelta", 0))::numeric AS saldo_kg
FROM "StockMovement" sm
LEFT JOIN "Lot" l ON l."id" = sm."lotId"
GROUP BY l."productId", COALESCE(sm."toLocationId", l."currentLocationId"), l."maturityState";

CREATE MATERIALIZED VIEW clean.maturacao_atual AS
SELECT
  l."id" AS lot_id,
  l."productId" AS product_id,
  l."maturityState"::text AS current_maturity,
  l."updatedAt" AS maturity_updated_at,
  l."boxes",
  l."kg"
FROM "Lot" l;

CREATE MATERIALIZED VIEW clean.devolucoes_clientes AS
SELECT
  r."clientId" AS client_id,
  SUM(r."boxes")::numeric AS total_boxes,
  SUM(COALESCE(r."kg", 0))::numeric AS total_kg,
  date_trunc('day', r."happenedAt") AS dia
FROM "ReturnRecord" r
GROUP BY r."clientId", date_trunc('day', r."happenedAt");

CREATE MATERIALIZED VIEW clean.perdas_mensal AS
SELECT
  date_trunc('month', lr."happenedAt") AS mes,
  lr."lotId" AS lot_id,
  l."productId" AS product_id,
  lr."reason",
  SUM(lr."boxes")::numeric AS total_boxes,
  SUM(COALESCE(lr."kg", 0))::numeric AS total_kg
FROM "LossRecord" lr
LEFT JOIN "Lot" l ON l."id" = lr."lotId"
GROUP BY date_trunc('month', lr."happenedAt"), lr."lotId", l."productId", lr."reason";
