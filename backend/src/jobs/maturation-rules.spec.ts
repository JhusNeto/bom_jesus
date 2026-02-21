import { MaturityState } from '@prisma/client';
import { computeMaturityState } from './maturation-rules';

describe('computeMaturityState', () => {
  const base = new Date('2025-01-01T12:00:00Z');

  it('retorna VERDE para lote com 0-2 dias', () => {
    expect(computeMaturityState(base, new Date('2025-01-01T12:00:00Z'))).toBe(
      MaturityState.VERDE,
    );
    expect(computeMaturityState(base, new Date('2025-01-02T12:00:00Z'))).toBe(
      MaturityState.VERDE,
    );
    expect(computeMaturityState(base, new Date('2025-01-03T11:59:59Z'))).toBe(
      MaturityState.VERDE,
    );
  });

  it('retorna DE_VEZ para lote com 3-4 dias', () => {
    expect(computeMaturityState(base, new Date('2025-01-04T12:00:00Z'))).toBe(
      MaturityState.DE_VEZ,
    );
    expect(computeMaturityState(base, new Date('2025-01-05T11:59:59Z'))).toBe(
      MaturityState.DE_VEZ,
    );
  });

  it('retorna MADURA para lote com 5+ dias', () => {
    expect(computeMaturityState(base, new Date('2025-01-06T12:00:00Z'))).toBe(
      MaturityState.MADURA,
    );
    expect(computeMaturityState(base, new Date('2025-01-10T12:00:00Z'))).toBe(
      MaturityState.MADURA,
    );
  });
});
