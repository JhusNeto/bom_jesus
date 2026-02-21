import { RawEventType, ValidationStatus } from '@prisma/client';
import { validateOperationalEvent } from './event-validation';

const rules = {
  qtyBoxesMax: 2000,
  qtyKgMax: 50000,
  eventFutureMinutesMax: 5,
  eventPastDaysMax: 7,
};

describe('validateOperationalEvent', () => {
  it('marca INVALID quando falta campo essencial', () => {
    const result = validateOperationalEvent({
      eventType: RawEventType.RETURN_REGISTERED,
      occurredAt: new Date(),
      data: { clientId: 'c1', boxes: 10 },
      rules,
    });

    expect(result.status).toBe(ValidationStatus.INVALID);
    expect(result.errors.some((item) => item.code === 'MISSING_STORE_ID')).toBe(true);
  });

  it('marca NEEDS_REVIEW para range fora da faixa', () => {
    const result = validateOperationalEvent({
      eventType: RawEventType.LOT_ENTRY_REGISTERED,
      occurredAt: new Date(),
      data: {
        productId: 'p1',
        locationId: 'l1',
        boxes: 2300,
      },
      rules,
    });

    expect(result.status).toBe(ValidationStatus.NEEDS_REVIEW);
    expect(result.errors.some((item) => item.code === 'QTY_BOXES_OUT_OF_RANGE')).toBe(
      true,
    );
  });

  it('marca VALID quando evento atende minimo viavel', () => {
    const result = validateOperationalEvent({
      eventType: RawEventType.LOT_MOVED,
      occurredAt: new Date(),
      data: {
        lotId: 'lot-1',
        fromLocationId: 'a',
        toLocationId: 'b',
        kg: 120,
      },
      rules,
    });

    expect(result.status).toBe(ValidationStatus.VALID);
    expect(result.errors).toHaveLength(0);
  });

  it('marca EVENT_TS_TOO_FUTURE para ocorreuAt no futuro', () => {
    const futuro = new Date(Date.now() + 10 * 60 * 1000); // +10 min
    const result = validateOperationalEvent({
      eventType: RawEventType.LOT_ENTRY_REGISTERED,
      occurredAt: futuro,
      data: { productId: 'p1', locationId: 'l1', boxes: 10 },
      rules,
    });
    expect(result.errors.some((e) => e.code === 'EVENT_TS_TOO_FUTURE')).toBe(true);
  });

  it('marca EVENT_TS_TOO_OLD para ocorreuAt muito antigo', () => {
    const antigo = new Date(Date.now() - 10 * 86400 * 1000); // -10 dias
    const result = validateOperationalEvent({
      eventType: RawEventType.LOT_ENTRY_REGISTERED,
      occurredAt: antigo,
      data: { productId: 'p1', locationId: 'l1', boxes: 10 },
      rules,
    });
    expect(result.errors.some((e) => e.code === 'EVENT_TS_TOO_OLD')).toBe(true);
  });

  it('LOSS_REGISTERED exige lotId ou productId, locationId, reason, quantidade', () => {
    const r = validateOperationalEvent({
      eventType: RawEventType.LOSS_REGISTERED,
      occurredAt: new Date(),
      data: { lotId: 'l1', locationId: 'loc1', reason: 'apodrecimento', boxes: 5 },
      rules,
    });
    expect(r.status).toBe(ValidationStatus.VALID);
  });
});
