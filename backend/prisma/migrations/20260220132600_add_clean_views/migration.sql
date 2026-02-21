CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS auth;
CREATE SCHEMA IF NOT EXISTS clean;

CREATE OR REPLACE VIEW clean.estoque_atual AS
SELECT
  l."productId" AS product_id,
  COALESCE(sm."toLocationId", l."currentLocationId") AS location_id,
  l."maturityState" AS maturity_stage,
  SUM(sm."boxesDelta")::numeric AS saldo_boxes,
  SUM(COALESCE(sm."kgDelta", 0))::numeric AS saldo_kg
FROM "StockMovement" sm
LEFT JOIN "Lot" l ON l.id = sm."lotId"
GROUP BY l."productId", COALESCE(sm."toLocationId", l."currentLocationId"), l."maturityState";

CREATE OR REPLACE VIEW clean.maturacao_atual AS
SELECT
  l.id AS lot_id,
  l."productId" AS product_id,
  l."maturityState" AS current_maturity,
  l."updatedAt" AS maturity_updated_at,
  l.boxes,
  l.kg
FROM "Lot" l;

CREATE OR REPLACE VIEW clean.devolucoes_clientes AS
SELECT
  r."clientId" AS client_id,
  SUM(r.boxes)::numeric AS total_boxes,
  SUM(COALESCE(r.kg, 0))::numeric AS total_kg,
  date_trunc('day', r."happenedAt") AS dia
FROM "ReturnRecord" r
GROUP BY r."clientId", date_trunc('day', r."happenedAt");

CREATE OR REPLACE VIEW clean.perdas_mensal AS
SELECT
  date_trunc('month', lr."happenedAt") AS mes,
  lr."lotId" AS lot_id,
  l."productId" AS product_id,
  lr.reason,
  SUM(lr.boxes)::numeric AS total_boxes,
  SUM(COALESCE(lr.kg, 0))::numeric AS total_kg
FROM "LossRecord" lr
LEFT JOIN "Lot" l ON l.id = lr."lotId"
GROUP BY date_trunc('month', lr."happenedAt"), lr."lotId", l."productId", lr.reason;
