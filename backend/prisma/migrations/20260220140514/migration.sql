-- AlterTable (safe: table created in 20260220142000)
DO $$
BEGIN
  IF EXISTS (
    SELECT 1 FROM information_schema.tables
    WHERE table_schema = 'public' AND table_name = 'RawEventProcessingState'
  ) THEN
    ALTER TABLE "RawEventProcessingState" ALTER COLUMN "updatedAt" DROP DEFAULT;
  END IF;
END $$;
