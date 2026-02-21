import { RawEventType, ValidationStatus } from '@prisma/client';

export interface EventValidationRules {
  qtyBoxesMax: number;
  qtyKgMax: number;
  eventFutureMinutesMax: number;
  eventPastDaysMax: number;
}

export interface EventValidationResult {
  status: ValidationStatus;
  errors: Array<{ code: string; message: string }>;
}

function hasPositiveQuantity(payload: Record<string, unknown>) {
  const boxes =
    typeof payload.boxes === 'number' ? Number(payload.boxes) : undefined;
  const kg = typeof payload.kg === 'number' ? Number(payload.kg) : undefined;
  return (boxes !== undefined && boxes > 0) || (kg !== undefined && kg > 0);
}

export function validateOperationalEvent(params: {
  eventType: RawEventType;
  occurredAt: Date;
  data: Record<string, unknown>;
  rules: EventValidationRules;
}): EventValidationResult {
  const errors: Array<{ code: string; message: string }> = [];
  const payload = params.data;

  const now = new Date();
  const maxFuture = new Date(now.getTime() + params.rules.eventFutureMinutesMax * 60_000);
  const maxPast = new Date(now.getTime() - params.rules.eventPastDaysMax * 86_400_000);
  if (params.occurredAt > maxFuture) {
    errors.push({
      code: 'EVENT_TS_TOO_FUTURE',
      message: 'event_ts acima da tolerancia futura',
    });
  }
  if (params.occurredAt < maxPast) {
    errors.push({
      code: 'EVENT_TS_TOO_OLD',
      message: 'event_ts antigo acima da tolerancia',
    });
  }

  const boxes = typeof payload.boxes === 'number' ? Number(payload.boxes) : undefined;
  const kg = typeof payload.kg === 'number' ? Number(payload.kg) : undefined;
  if (boxes !== undefined && boxes > params.rules.qtyBoxesMax) {
    errors.push({ code: 'QTY_BOXES_OUT_OF_RANGE', message: 'qty_boxes acima da faixa' });
  }
  if (kg !== undefined && kg > params.rules.qtyKgMax) {
    errors.push({ code: 'QTY_KG_OUT_OF_RANGE', message: 'qty_kg acima da faixa' });
  }

  switch (params.eventType) {
    case RawEventType.LOT_ENTRY_REGISTERED: {
      if (!payload.productId) {
        errors.push({ code: 'MISSING_PRODUCT_ID', message: 'product_id obrigatorio' });
      }
      if (!payload.locationId) {
        errors.push({ code: 'MISSING_LOCATION_ID', message: 'location_id obrigatorio' });
      }
      if (!hasPositiveQuantity(payload)) {
        errors.push({
          code: 'MISSING_QUANTITY',
          message: 'qty_boxes ou qty_kg obrigatorio',
        });
      }
      break;
    }
    case RawEventType.LOT_MOVED: {
      if (!payload.lotId) errors.push({ code: 'MISSING_LOT_ID', message: 'lot_id obrigatorio' });
      if (!payload.fromLocationId) {
        errors.push({
          code: 'MISSING_FROM_LOCATION_ID',
          message: 'from_location_id obrigatorio',
        });
      }
      if (!payload.toLocationId) {
        errors.push({
          code: 'MISSING_TO_LOCATION_ID',
          message: 'to_location_id obrigatorio',
        });
      }
      if (!hasPositiveQuantity(payload)) {
        errors.push({
          code: 'MISSING_QUANTITY',
          message: 'qty_boxes ou qty_kg obrigatorio',
        });
      }
      break;
    }
    case RawEventType.LOSS_REGISTERED: {
      if (!payload.lotId && !payload.productId) {
        errors.push({
          code: 'MISSING_LOT_OR_PRODUCT',
          message: 'lot_id ou product_id obrigatorio',
        });
      }
      if (!payload.locationId) {
        errors.push({
          code: 'MISSING_LOCATION_ID',
          message: 'location_id obrigatorio',
        });
      }
      if (!payload.reason) {
        errors.push({ code: 'MISSING_REASON', message: 'reason obrigatorio' });
      }
      if (!hasPositiveQuantity(payload)) {
        errors.push({
          code: 'MISSING_QUANTITY',
          message: 'qty_boxes ou qty_kg obrigatorio',
        });
      }
      break;
    }
    case RawEventType.RETURN_REGISTERED: {
      if (!payload.clientId) {
        errors.push({ code: 'MISSING_CLIENT_ID', message: 'client_id obrigatorio' });
      }
      if (!payload.storeId) {
        errors.push({ code: 'MISSING_STORE_ID', message: 'store_id obrigatorio' });
      }
      if (!payload.productId) {
        errors.push({ code: 'MISSING_PRODUCT_ID', message: 'product_id obrigatorio' });
      }
      if (!payload.reason) {
        errors.push({ code: 'MISSING_REASON', message: 'reason obrigatorio' });
      }
      if (!hasPositiveQuantity(payload)) {
        errors.push({
          code: 'MISSING_QUANTITY',
          message: 'qty_boxes ou qty_kg obrigatorio',
        });
      }
      break;
    }
    default:
      break;
  }

  const hasHardBlock = errors.some((error) => error.code.startsWith('MISSING_'));
  const status = hasHardBlock
    ? ValidationStatus.INVALID
    : errors.length > 0
      ? ValidationStatus.NEEDS_REVIEW
      : ValidationStatus.VALID;

  return { status, errors };
}
