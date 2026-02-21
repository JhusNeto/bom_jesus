-- CreateEnum
CREATE TYPE "UserRole" AS ENUM ('OPERATOR', 'ADMINISTRATIVE', 'MANAGER', 'ADMIN');

-- CreateEnum
CREATE TYPE "MaturityState" AS ENUM ('VERDE', 'DE_VEZ', 'MADURA');

-- CreateEnum
CREATE TYPE "MovementType" AS ENUM ('ENTRY', 'MOVE', 'LOSS', 'RETURN', 'EXIT');

-- CreateEnum
CREATE TYPE "EventSyncStatus" AS ENUM ('RECEIVED', 'PROCESSED', 'FAILED');

-- CreateTable
CREATE TABLE "User" (
    "id" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "email" TEXT NOT NULL,
    "password" TEXT NOT NULL,
    "role" "UserRole" NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "User_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Product" (
    "id" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "active" BOOLEAN NOT NULL DEFAULT true,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "Product_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Location" (
    "id" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "type" TEXT NOT NULL,
    "active" BOOLEAN NOT NULL DEFAULT true,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "Location_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Client" (
    "id" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "active" BOOLEAN NOT NULL DEFAULT true,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "Client_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Store" (
    "id" TEXT NOT NULL,
    "clientId" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "city" TEXT,
    "active" BOOLEAN NOT NULL DEFAULT true,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "Store_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Lot" (
    "id" TEXT NOT NULL,
    "productId" TEXT NOT NULL,
    "currentLocationId" TEXT,
    "maturityState" "MaturityState" NOT NULL DEFAULT 'VERDE',
    "boxes" INTEGER NOT NULL DEFAULT 0,
    "kg" DECIMAL(12,3),
    "entryDate" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "inconsistent" BOOLEAN NOT NULL DEFAULT false,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "Lot_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "StockMovement" (
    "id" TEXT NOT NULL,
    "lotId" TEXT NOT NULL,
    "fromLocationId" TEXT,
    "toLocationId" TEXT,
    "movementType" "MovementType" NOT NULL,
    "boxesDelta" INTEGER NOT NULL DEFAULT 0,
    "kgDelta" DECIMAL(12,3),
    "happenedAt" TIMESTAMP(3) NOT NULL,
    "userId" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "StockMovement_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "LossRecord" (
    "id" TEXT NOT NULL,
    "lotId" TEXT NOT NULL,
    "reason" TEXT NOT NULL,
    "boxes" INTEGER NOT NULL DEFAULT 0,
    "kg" DECIMAL(12,3),
    "happenedAt" TIMESTAMP(3) NOT NULL,
    "userId" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "LossRecord_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "ReturnRecord" (
    "id" TEXT NOT NULL,
    "lotId" TEXT,
    "clientId" TEXT NOT NULL,
    "storeId" TEXT NOT NULL,
    "reason" TEXT NOT NULL,
    "boxes" INTEGER NOT NULL DEFAULT 0,
    "kg" DECIMAL(12,3),
    "photoUrl" TEXT,
    "happenedAt" TIMESTAMP(3) NOT NULL,
    "userId" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "ReturnRecord_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "RawEvent" (
    "id" TEXT NOT NULL,
    "eventType" TEXT NOT NULL,
    "source" TEXT NOT NULL,
    "payloadJson" JSONB NOT NULL,
    "deviceId" TEXT,
    "userId" TEXT,
    "occurredAt" TIMESTAMP(3) NOT NULL,
    "receivedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "syncStatus" "EventSyncStatus" NOT NULL DEFAULT 'RECEIVED',
    "idempotencyKey" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "RawEvent_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "ValidationIssue" (
    "id" TEXT NOT NULL,
    "rawEventId" TEXT NOT NULL,
    "issueCode" TEXT NOT NULL,
    "severity" TEXT NOT NULL,
    "details" TEXT,
    "resolved" BOOLEAN NOT NULL DEFAULT false,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "ValidationIssue_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "MaturationDailySnapshot" (
    "id" TEXT NOT NULL,
    "lotId" TEXT NOT NULL,
    "snapshotDate" TIMESTAMP(3) NOT NULL,
    "state" "MaturityState" NOT NULL,
    "boxes" INTEGER NOT NULL DEFAULT 0,
    "kg" DECIMAL(12,3),
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "MaturationDailySnapshot_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "User_email_key" ON "User"("email");

-- CreateIndex
CREATE UNIQUE INDEX "Product_name_key" ON "Product"("name");

-- CreateIndex
CREATE UNIQUE INDEX "Location_name_key" ON "Location"("name");

-- CreateIndex
CREATE UNIQUE INDEX "Client_name_key" ON "Client"("name");

-- CreateIndex
CREATE INDEX "Store_clientId_idx" ON "Store"("clientId");

-- CreateIndex
CREATE UNIQUE INDEX "Store_clientId_name_key" ON "Store"("clientId", "name");

-- CreateIndex
CREATE INDEX "Lot_productId_idx" ON "Lot"("productId");

-- CreateIndex
CREATE INDEX "Lot_maturityState_idx" ON "Lot"("maturityState");

-- CreateIndex
CREATE INDEX "Lot_currentLocationId_idx" ON "Lot"("currentLocationId");

-- CreateIndex
CREATE INDEX "StockMovement_lotId_happenedAt_idx" ON "StockMovement"("lotId", "happenedAt");

-- CreateIndex
CREATE INDEX "StockMovement_movementType_happenedAt_idx" ON "StockMovement"("movementType", "happenedAt");

-- CreateIndex
CREATE INDEX "LossRecord_happenedAt_idx" ON "LossRecord"("happenedAt");

-- CreateIndex
CREATE INDEX "LossRecord_lotId_idx" ON "LossRecord"("lotId");

-- CreateIndex
CREATE INDEX "ReturnRecord_happenedAt_idx" ON "ReturnRecord"("happenedAt");

-- CreateIndex
CREATE INDEX "ReturnRecord_clientId_storeId_idx" ON "ReturnRecord"("clientId", "storeId");

-- CreateIndex
CREATE UNIQUE INDEX "RawEvent_idempotencyKey_key" ON "RawEvent"("idempotencyKey");

-- CreateIndex
CREATE INDEX "RawEvent_eventType_occurredAt_idx" ON "RawEvent"("eventType", "occurredAt");

-- CreateIndex
CREATE INDEX "RawEvent_syncStatus_idx" ON "RawEvent"("syncStatus");

-- CreateIndex
CREATE INDEX "ValidationIssue_rawEventId_idx" ON "ValidationIssue"("rawEventId");

-- CreateIndex
CREATE INDEX "ValidationIssue_resolved_severity_idx" ON "ValidationIssue"("resolved", "severity");

-- CreateIndex
CREATE INDEX "MaturationDailySnapshot_snapshotDate_state_idx" ON "MaturationDailySnapshot"("snapshotDate", "state");

-- CreateIndex
CREATE UNIQUE INDEX "MaturationDailySnapshot_lotId_snapshotDate_key" ON "MaturationDailySnapshot"("lotId", "snapshotDate");

-- AddForeignKey
ALTER TABLE "Store" ADD CONSTRAINT "Store_clientId_fkey" FOREIGN KEY ("clientId") REFERENCES "Client"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Lot" ADD CONSTRAINT "Lot_productId_fkey" FOREIGN KEY ("productId") REFERENCES "Product"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Lot" ADD CONSTRAINT "Lot_currentLocationId_fkey" FOREIGN KEY ("currentLocationId") REFERENCES "Location"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "StockMovement" ADD CONSTRAINT "StockMovement_lotId_fkey" FOREIGN KEY ("lotId") REFERENCES "Lot"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "StockMovement" ADD CONSTRAINT "StockMovement_fromLocationId_fkey" FOREIGN KEY ("fromLocationId") REFERENCES "Location"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "StockMovement" ADD CONSTRAINT "StockMovement_toLocationId_fkey" FOREIGN KEY ("toLocationId") REFERENCES "Location"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "StockMovement" ADD CONSTRAINT "StockMovement_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "LossRecord" ADD CONSTRAINT "LossRecord_lotId_fkey" FOREIGN KEY ("lotId") REFERENCES "Lot"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "LossRecord" ADD CONSTRAINT "LossRecord_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "ReturnRecord" ADD CONSTRAINT "ReturnRecord_lotId_fkey" FOREIGN KEY ("lotId") REFERENCES "Lot"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "ReturnRecord" ADD CONSTRAINT "ReturnRecord_clientId_fkey" FOREIGN KEY ("clientId") REFERENCES "Client"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "ReturnRecord" ADD CONSTRAINT "ReturnRecord_storeId_fkey" FOREIGN KEY ("storeId") REFERENCES "Store"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "ReturnRecord" ADD CONSTRAINT "ReturnRecord_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "RawEvent" ADD CONSTRAINT "RawEvent_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "ValidationIssue" ADD CONSTRAINT "ValidationIssue_rawEventId_fkey" FOREIGN KEY ("rawEventId") REFERENCES "RawEvent"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "MaturationDailySnapshot" ADD CONSTRAINT "MaturationDailySnapshot_lotId_fkey" FOREIGN KEY ("lotId") REFERENCES "Lot"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
