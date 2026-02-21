export interface FrontValidationResult {
  blockingErrors: string[];
  warnings: string[];
}

const RULES = {
  qtyBoxesMax: 2000,
  qtyKgMax: 50000,
  eventFutureMinutesMax: 5,
  eventPastDaysMax: 7,
};

function validateCommonQuantities(boxes?: number, kg?: number, result?: FrontValidationResult) {
  const output = result ?? { blockingErrors: [], warnings: [] };

  if ((boxes === undefined || boxes <= 0) && (kg === undefined || kg <= 0)) {
    output.blockingErrors.push('Informe caixas ou kg.');
  }

  if (boxes !== undefined && boxes > RULES.qtyBoxesMax) {
    output.warnings.push(
      `Quantidade de caixas acima da faixa (${RULES.qtyBoxesMax}).`,
    );
  }
  if (kg !== undefined && kg > RULES.qtyKgMax) {
    output.warnings.push(`Quantidade em kg acima da faixa (${RULES.qtyKgMax}).`);
  }

  return output;
}

function validateEventTimestamp(eventTsIso: string, result?: FrontValidationResult) {
  const output = result ?? { blockingErrors: [], warnings: [] };
  const eventTs = new Date(eventTsIso);
  const now = new Date();
  const maxFuture = new Date(now.getTime() + RULES.eventFutureMinutesMax * 60_000);
  const maxPast = new Date(now.getTime() - RULES.eventPastDaysMax * 86_400_000);

  if (eventTs > maxFuture) {
    output.warnings.push('Evento com horario futuro acima da tolerancia.');
  }
  if (eventTs < maxPast) {
    output.warnings.push('Evento antigo acima da tolerancia operacional.');
  }

  return output;
}

export function validateLotEntry(input: {
  productId?: string;
  locationId?: string;
  boxes?: number;
  kg?: number;
  eventTsIso: string;
}): FrontValidationResult {
  const result: FrontValidationResult = { blockingErrors: [], warnings: [] };
  if (!input.productId) result.blockingErrors.push('Produto obrigatorio.');
  if (!input.locationId) result.blockingErrors.push('Localizacao obrigatoria.');
  validateCommonQuantities(input.boxes, input.kg, result);
  validateEventTimestamp(input.eventTsIso, result);
  return result;
}

export function validateLotMove(input: {
  lotId?: string;
  fromLocationId?: string;
  toLocationId?: string;
  boxes?: number;
  kg?: number;
  eventTsIso: string;
}): FrontValidationResult {
  const result: FrontValidationResult = { blockingErrors: [], warnings: [] };
  if (!input.lotId) result.blockingErrors.push('Lote obrigatorio.');
  if (!input.fromLocationId) result.blockingErrors.push('Origem obrigatoria.');
  if (!input.toLocationId) result.blockingErrors.push('Destino obrigatorio.');
  validateCommonQuantities(input.boxes, input.kg, result);
  validateEventTimestamp(input.eventTsIso, result);
  return result;
}

export function validateLoss(input: {
  lotId?: string;
  productId?: string;
  locationId?: string;
  reason?: string;
  boxes?: number;
  kg?: number;
  eventTsIso: string;
}): FrontValidationResult {
  const result: FrontValidationResult = { blockingErrors: [], warnings: [] };
  if (!input.lotId && !input.productId) {
    result.blockingErrors.push('Informe lote ou produto.');
  }
  if (!input.locationId) result.blockingErrors.push('Localizacao obrigatoria.');
  if (!input.reason) result.blockingErrors.push('Motivo obrigatorio.');
  validateCommonQuantities(input.boxes, input.kg, result);
  validateEventTimestamp(input.eventTsIso, result);
  return result;
}

export function validateReturn(input: {
  clientId?: string;
  storeId?: string;
  productId?: string;
  reason?: string;
  boxes?: number;
  kg?: number;
  eventTsIso: string;
}): FrontValidationResult {
  const result: FrontValidationResult = { blockingErrors: [], warnings: [] };
  if (!input.clientId) result.blockingErrors.push('Cliente obrigatorio.');
  if (!input.storeId) result.blockingErrors.push('Loja obrigatoria.');
  if (!input.productId) result.blockingErrors.push('Produto obrigatorio.');
  if (!input.reason) result.blockingErrors.push('Motivo obrigatorio.');
  validateCommonQuantities(input.boxes, input.kg, result);
  validateEventTimestamp(input.eventTsIso, result);
  return result;
}
