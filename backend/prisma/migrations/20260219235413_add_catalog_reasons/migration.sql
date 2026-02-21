-- CreateEnum
CREATE TYPE "ReasonType" AS ENUM ('LOSS', 'RETURN');

-- CreateTable
CREATE TABLE "Reason" (
    "id" TEXT NOT NULL,
    "type" "ReasonType" NOT NULL,
    "name" TEXT NOT NULL,
    "active" BOOLEAN NOT NULL DEFAULT true,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "Reason_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE INDEX "Reason_type_active_idx" ON "Reason"("type", "active");

-- CreateIndex
CREATE UNIQUE INDEX "Reason_type_name_key" ON "Reason"("type", "name");
