-- Permissive validation runtime rules and extended return/loss traceability.

CREATE TABLE IF NOT EXISTS "ValidationRuleConfig" (
  "id" TEXT NOT NULL,
  "key" TEXT NOT NULL,
  "valueNumber" DECIMAL(14,4),
  "valueText" TEXT,
  "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "updatedAt" TIMESTAMP(3) NOT NULL,
  CONSTRAINT "ValidationRuleConfig_pkey" PRIMARY KEY ("id")
);

CREATE UNIQUE INDEX IF NOT EXISTS "ValidationRuleConfig_key_key"
  ON "ValidationRuleConfig"("key");

ALTER TABLE "LossRecord"
  ADD COLUMN IF NOT EXISTS "productId" TEXT,
  ADD COLUMN IF NOT EXISTS "locationId" TEXT;

ALTER TABLE "ReturnRecord"
  ADD COLUMN IF NOT EXISTS "productId" TEXT;

CREATE INDEX IF NOT EXISTS "LossRecord_productId_idx" ON "LossRecord"("productId");
CREATE INDEX IF NOT EXISTS "LossRecord_locationId_idx" ON "LossRecord"("locationId");
CREATE INDEX IF NOT EXISTS "ReturnRecord_productId_idx" ON "ReturnRecord"("productId");

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'LossRecord_productId_fkey'
  ) THEN
    ALTER TABLE "LossRecord"
      ADD CONSTRAINT "LossRecord_productId_fkey"
      FOREIGN KEY ("productId") REFERENCES "Product"("id")
      ON DELETE SET NULL ON UPDATE CASCADE;
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'LossRecord_locationId_fkey'
  ) THEN
    ALTER TABLE "LossRecord"
      ADD CONSTRAINT "LossRecord_locationId_fkey"
      FOREIGN KEY ("locationId") REFERENCES "Location"("id")
      ON DELETE SET NULL ON UPDATE CASCADE;
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'ReturnRecord_productId_fkey'
  ) THEN
    ALTER TABLE "ReturnRecord"
      ADD CONSTRAINT "ReturnRecord_productId_fkey"
      FOREIGN KEY ("productId") REFERENCES "Product"("id")
      ON DELETE SET NULL ON UPDATE CASCADE;
  END IF;
END $$;

INSERT INTO "ValidationRuleConfig" ("id", "key", "valueNumber", "createdAt", "updatedAt")
VALUES
  ('rule_qty_boxes_max', 'QTY_BOXES_MAX', 2000, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
  ('rule_qty_kg_max', 'QTY_KG_MAX', 50000, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
  ('rule_event_future_minutes_max', 'EVENT_FUTURE_MINUTES_MAX', 5, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
  ('rule_event_past_days_max', 'EVENT_PAST_DAYS_MAX', 7, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
  ('rule_mature_stock_alert_boxes', 'MATURE_STOCK_ALERT_BOXES', 300, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
ON CONFLICT ("key") DO NOTHING;
