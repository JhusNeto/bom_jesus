import { MaturityState } from '@prisma/client';

/**
 * Regras de maturação por idade do lote (dias desde entrada).
 * VERDE: 0-2 dias; DE_VEZ: 3-4 dias; MADURA: 5+ dias.
 */
export function computeMaturityState(
  entryDate: Date,
  asOfDate: Date = new Date(),
): MaturityState {
  const ageInDays = Math.floor(
    (asOfDate.getTime() - entryDate.getTime()) / (1000 * 60 * 60 * 24),
  );
  if (ageInDays >= 5) return MaturityState.MADURA;
  if (ageInDays >= 3) return MaturityState.DE_VEZ;
  return MaturityState.VERDE;
}
