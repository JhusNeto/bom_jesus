/*
  Warnings:

  - Changed the type of `eventType` on the `RawEvent` table. No cast exists, the column would be dropped and recreated, which cannot be done if there is data, since the column is required.

*/
-- CreateEnum
CREATE TYPE "RawEventType" AS ENUM ('LOT_ENTRY_REGISTERED', 'LOT_MOVED', 'LOSS_REGISTERED', 'RETURN_REGISTERED', 'MATURITY_OVERRIDE', 'ORDER_PHOTO_CAPTURED');

-- CreateEnum
CREATE TYPE "ValidationStatus" AS ENUM ('VALID', 'NEEDS_REVIEW', 'INVALID');

-- CreateEnum
CREATE TYPE "ProcessingStatus" AS ENUM ('PENDING', 'PROCESSED', 'FAILED');

-- AlterTable
ALTER TABLE "LossRecord" ADD COLUMN     "sourceRawEventId" TEXT;

-- AlterTable
ALTER TABLE "RawEvent" ADD COLUMN     "ingestedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
ADD COLUMN     "processedAt" TIMESTAMP(3),
ADD COLUMN     "processingStatus" "ProcessingStatus" NOT NULL DEFAULT 'PENDING',
ADD COLUMN     "validationErrors" JSONB,
ADD COLUMN     "validationStatus" "ValidationStatus" NOT NULL DEFAULT 'VALID';

-- Convert eventType from text to enum without data loss
ALTER TABLE "RawEvent"
  ALTER COLUMN "eventType" TYPE "RawEventType"
  USING "eventType"::"RawEventType";

-- AlterTable
ALTER TABLE "ReturnRecord" ADD COLUMN     "sourceRawEventId" TEXT;

-- AlterTable
ALTER TABLE "StockMovement" ADD COLUMN     "sourceRawEventId" TEXT;

-- CreateIndex
CREATE INDEX "LossRecord_sourceRawEventId_idx" ON "LossRecord"("sourceRawEventId");

-- CreateIndex
DROP INDEX IF EXISTS "RawEvent_eventType_occurredAt_idx";
CREATE INDEX "RawEvent_eventType_occurredAt_idx" ON "RawEvent"("eventType", "occurredAt");

-- CreateIndex
CREATE INDEX "RawEvent_validationStatus_idx" ON "RawEvent"("validationStatus");

-- CreateIndex
CREATE INDEX "RawEvent_processingStatus_ingestedAt_idx" ON "RawEvent"("processingStatus", "ingestedAt");

-- CreateIndex
CREATE INDEX "ReturnRecord_sourceRawEventId_idx" ON "ReturnRecord"("sourceRawEventId");

-- CreateIndex
CREATE INDEX "StockMovement_sourceRawEventId_idx" ON "StockMovement"("sourceRawEventId");

-- AddForeignKey
ALTER TABLE "StockMovement" ADD CONSTRAINT "StockMovement_sourceRawEventId_fkey" FOREIGN KEY ("sourceRawEventId") REFERENCES "RawEvent"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "LossRecord" ADD CONSTRAINT "LossRecord_sourceRawEventId_fkey" FOREIGN KEY ("sourceRawEventId") REFERENCES "RawEvent"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "ReturnRecord" ADD CONSTRAINT "ReturnRecord_sourceRawEventId_fkey" FOREIGN KEY ("sourceRawEventId") REFERENCES "RawEvent"("id") ON DELETE SET NULL ON UPDATE CASCADE;
