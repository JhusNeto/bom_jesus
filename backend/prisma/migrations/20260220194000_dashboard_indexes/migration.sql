-- Indexes for dashboard filters and grouping.

CREATE INDEX IF NOT EXISTS "Lot_productId_maturityState_idx"
  ON "Lot"("productId", "maturityState");

CREATE INDEX IF NOT EXISTS "ReturnRecord_clientId_happenedAt_idx"
  ON "ReturnRecord"("clientId", "happenedAt");
