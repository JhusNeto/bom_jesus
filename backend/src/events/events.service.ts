import { Injectable } from '@nestjs/common';
import {
  MovementType,
  Prisma,
  ProcessingStatus,
  RawEventType,
  ValidationStatus,
} from '@prisma/client';
import { PrismaService } from '../prisma/prisma.service';
import { ValidationRulesService } from '../validation-rules/validation-rules.service';
import { IngestEventDto } from './dto/ingest-event.dto';
import { validateOperationalEvent } from './event-validation';

@Injectable()
export class EventsService {
  constructor(
    private readonly prisma: PrismaService,
    private readonly validationRulesService: ValidationRulesService,
  ) {}

  private buildRawWhere(params: {
    status?: ProcessingStatus;
    eventType?: RawEventType;
    idempotencyKey?: string;
    from?: string;
    to?: string;
  }): Prisma.RawEventWhereInput {
    const occurredAtFilter: Prisma.DateTimeFilter = {};
    if (params.from) {
      const fromDate = new Date(params.from);
      if (!Number.isNaN(fromDate.getTime())) {
        occurredAtFilter.gte = fromDate;
      }
    }
    if (params.to) {
      const toDate = new Date(params.to);
      if (!Number.isNaN(toDate.getTime())) {
        occurredAtFilter.lte = toDate;
      }
    }

    return {
      ...(params.status
        ? { processingState: { processingStatus: params.status } }
        : {}),
      ...(params.eventType ? { eventType: params.eventType } : {}),
      ...(params.idempotencyKey
        ? { idempotencyKey: { contains: params.idempotencyKey, mode: 'insensitive' } }
        : {}),
      ...(Object.keys(occurredAtFilter).length > 0
        ? { occurredAt: occurredAtFilter }
        : {}),
    };
  }

  async ingest(dto: IngestEventDto) {
    const existing = await this.prisma.rawEvent.findUnique({
      where: { idempotencyKey: dto.idempotencyKey },
    });

    if (existing) {
      return { duplicated: true, rawEventId: existing.id };
    }

    const rules = await this.validationRulesService.getRules();
    const validation = validateOperationalEvent({
      eventType: dto.eventType,
      occurredAt: new Date(dto.occurredAt),
      data: dto.data,
      rules: {
        qtyBoxesMax: rules.QTY_BOXES_MAX,
        qtyKgMax: rules.QTY_KG_MAX,
        eventFutureMinutesMax: rules.EVENT_FUTURE_MINUTES_MAX,
        eventPastDaysMax: rules.EVENT_PAST_DAYS_MAX,
      },
    });
    const raw = await this.prisma.rawEvent.create({
      data: {
        eventType: dto.eventType,
        idempotencyKey: dto.idempotencyKey,
        occurredAt: new Date(dto.occurredAt),
        source: 'pwa',
        payloadJson: dto.data as Prisma.InputJsonValue,
        deviceId: dto.deviceId,
        userId: dto.userId,
      },
    });
    await this.prisma.rawEventProcessingState.create({
      data: {
        rawEventId: raw.id,
        validationStatus: validation.status,
        ...(validation.errors.length > 0
          ? {
              validationErrors:
                validation.errors as unknown as Prisma.InputJsonValue,
            }
          : {}),
        processingStatus: ProcessingStatus.PENDING,
      },
    });

    return {
      duplicated: false,
      rawEventId: raw.id,
      validationStatus: validation.status,
      processingStatus: ProcessingStatus.PENDING,
    };
  }

  private async processSingle(rawEventId: string) {
    const event = await this.prisma.rawEvent.findUnique({
      where: { id: rawEventId },
      include: { processingState: true },
    });
    if (!event) return { processed: false };

    if (event.processingState?.processingStatus === ProcessingStatus.PROCESSED) {
      return { processed: false, reason: 'already_processed' };
    }
    if (event.processingState?.validationStatus === ValidationStatus.INVALID) {
      await this.prisma.rawEventProcessingState.update({
        where: { rawEventId: event.id },
        data: {
          processingStatus: ProcessingStatus.FAILED,
          lastError: 'Evento invalido: campos essenciais ausentes.',
        },
      });
      return { processed: false, reason: 'invalid_payload' };
    }

    const payload = event.payloadJson as Record<string, unknown>;

    await this.prisma.$transaction(async (tx) => {
      const alreadyProjected =
        (event.eventType === RawEventType.LOT_ENTRY_REGISTERED &&
          (await tx.stockMovement.findFirst({
            where: { sourceRawEventId: event.id, movementType: MovementType.ENTRY },
            select: { id: true },
          }))) ||
        (event.eventType === RawEventType.LOT_MOVED &&
          (await tx.stockMovement.findFirst({
            where: { sourceRawEventId: event.id, movementType: MovementType.MOVE },
            select: { id: true },
          }))) ||
        (event.eventType === RawEventType.LOSS_REGISTERED &&
          (await tx.lossRecord.findFirst({
            where: { sourceRawEventId: event.id },
            select: { id: true },
          }))) ||
        (event.eventType === RawEventType.RETURN_REGISTERED &&
          (await tx.returnRecord.findFirst({
            where: { sourceRawEventId: event.id },
            select: { id: true },
          })));

      if (alreadyProjected) {
        await tx.rawEventProcessingState.update({
          where: { rawEventId: event.id },
          data: {
            processingStatus: ProcessingStatus.PROCESSED,
            processedAt: new Date(),
            lastError: null,
          },
        });
        return;
      }

      if (event.eventType === RawEventType.LOT_ENTRY_REGISTERED) {
        const lot = await tx.lot.create({
          data: {
            productId: String(payload.productId),
            currentLocationId:
              payload.locationId === undefined ? null : String(payload.locationId),
            boxes:
              payload.boxes === undefined
                ? 0
                : Number(payload.boxes),
            kg:
              payload.kg === undefined ? null : new Prisma.Decimal(Number(payload.kg)),
            entryDate: new Date(event.occurredAt),
          },
        });
        await tx.stockMovement.create({
          data: {
            lotId: lot.id,
            movementType: MovementType.ENTRY,
            boxesDelta: payload.boxes === undefined ? 0 : Number(payload.boxes),
            kgDelta:
              payload.kg === undefined ? null : new Prisma.Decimal(Number(payload.kg)),
            happenedAt: event.occurredAt,
            toLocationId:
              payload.locationId === undefined ? null : String(payload.locationId),
            userId: String(payload.userId ?? event.userId),
            sourceRawEventId: event.id,
          },
        });
      }

      if (event.eventType === RawEventType.LOT_MOVED && payload.lotId) {
        const lot = await tx.lot.findUnique({ where: { id: String(payload.lotId) } });
        if (lot) {
          await tx.stockMovement.create({
            data: {
              lotId: lot.id,
              movementType: MovementType.MOVE,
              boxesDelta:
                payload.boxes === undefined ? 0 : Number(payload.boxes) * -1,
              kgDelta:
                payload.kg === undefined
                  ? null
                  : new Prisma.Decimal(Number(payload.kg) * -1),
              happenedAt: event.occurredAt,
              fromLocationId:
                payload.fromLocationId === undefined
                  ? null
                  : String(payload.fromLocationId),
              toLocationId:
                payload.toLocationId === undefined
                  ? null
                  : String(payload.toLocationId),
              userId: String(payload.userId ?? event.userId),
              sourceRawEventId: event.id,
            },
          });
        }
      }

      if (event.eventType === RawEventType.LOSS_REGISTERED && payload.lotId) {
        const lot = await tx.lot.findUnique({ where: { id: String(payload.lotId) } });
        if (lot) {
          await tx.lossRecord.create({
            data: {
              lotId: lot.id,
              productId:
                payload.productId === undefined
                  ? lot.productId
                  : String(payload.productId),
              locationId:
                payload.locationId === undefined ? null : String(payload.locationId),
              reason: String(payload.reason ?? 'nao_informado'),
              boxes: payload.boxes === undefined ? 0 : Number(payload.boxes),
              kg:
                payload.kg === undefined ? null : new Prisma.Decimal(Number(payload.kg)),
              happenedAt: event.occurredAt,
              userId: String(payload.userId ?? event.userId),
              sourceRawEventId: event.id,
            },
          });
        }
      }

      if (event.eventType === RawEventType.RETURN_REGISTERED) {
        await tx.returnRecord.create({
          data: {
            lotId: payload.lotId === undefined ? null : String(payload.lotId),
            clientId: String(payload.clientId),
            storeId: String(payload.storeId),
            productId:
              payload.productId === undefined ? null : String(payload.productId),
            reason: String(payload.reason ?? 'nao_informado'),
            boxes: payload.boxes === undefined ? 0 : Number(payload.boxes),
            kg:
              payload.kg === undefined ? null : new Prisma.Decimal(Number(payload.kg)),
            photoUrl:
              payload.photoUrl === undefined ? null : String(payload.photoUrl),
            happenedAt: event.occurredAt,
            userId: String(payload.userId ?? event.userId),
            sourceRawEventId: event.id,
          },
        });
      }

      await tx.rawEventProcessingState.update({
        where: { rawEventId: event.id },
        data: {
          processingStatus: ProcessingStatus.PROCESSED,
          processedAt: new Date(),
          lastError: null,
        },
      });
    });

    return { processed: true, rawEventId: event.id };
  }

  async processPending(limit = 100) {
    const pending = await this.prisma.rawEventProcessingState.findMany({
      where: { processingStatus: ProcessingStatus.PENDING },
      orderBy: { ingestedAt: 'asc' },
      take: limit,
      select: { rawEventId: true },
    });

    let processedCount = 0;
    for (const event of pending) {
      try {
        await this.processSingle(event.rawEventId);
        processedCount += 1;
      } catch (error) {
        await this.prisma.rawEventProcessingState.update({
          where: { rawEventId: event.rawEventId },
          data: {
            processingStatus: ProcessingStatus.FAILED,
            lastError:
              error instanceof Error ? error.message.slice(0, 2000) : 'unknown_error',
          },
        });
      }
    }
    return { processedCount, totalPending: pending.length };
  }

  async reprocess(rawEventId: string) {
    await this.prisma.rawEventProcessingState.update({
      where: { rawEventId },
      data: {
        processingStatus: ProcessingStatus.PENDING,
        processedAt: null,
        lastError: null,
      },
    });
    return this.processSingle(rawEventId);
  }

  listRaw(params: {
    status?: ProcessingStatus;
    eventType?: RawEventType;
    idempotencyKey?: string;
    from?: string;
    to?: string;
    limit?: number;
  }) {
    return this.prisma.rawEvent.findMany({
      where: this.buildRawWhere(params),
      include: { processingState: true },
      orderBy: { occurredAt: 'desc' },
      take: params.limit ?? 200,
    });
  }

  async getPipelineMetrics() {
    const [pending, processed, failed, valid, needsReview] = await Promise.all([
      this.prisma.rawEventProcessingState.count({
        where: { processingStatus: ProcessingStatus.PENDING },
      }),
      this.prisma.rawEventProcessingState.count({
        where: { processingStatus: ProcessingStatus.PROCESSED },
      }),
      this.prisma.rawEventProcessingState.count({
        where: { processingStatus: ProcessingStatus.FAILED },
      }),
      this.prisma.rawEventProcessingState.count({
        where: { validationStatus: ValidationStatus.VALID },
      }),
      this.prisma.rawEventProcessingState.count({
        where: { validationStatus: ValidationStatus.NEEDS_REVIEW },
      }),
    ]);

    return {
      processing: { pending, processed, failed },
      validation: { valid, needsReview },
      generatedAt: new Date().toISOString(),
    };
  }

  async reprocessFailed(limit = 100) {
    const failedEvents = await this.prisma.rawEventProcessingState.findMany({
      where: { processingStatus: ProcessingStatus.FAILED },
      orderBy: { ingestedAt: 'asc' },
      take: limit,
      select: { rawEventId: true },
    });

    for (const event of failedEvents) {
      await this.prisma.rawEventProcessingState.update({
        where: { rawEventId: event.rawEventId },
        data: {
          processingStatus: ProcessingStatus.PENDING,
          processedAt: null,
          lastError: null,
        },
      });
    }

    return this.processPending(limit);
  }

  async exportRawCsv(params: {
    status?: ProcessingStatus;
    eventType?: RawEventType;
    idempotencyKey?: string;
    from?: string;
    to?: string;
    limit?: number;
  }) {
    const rows = await this.listRaw(params);
    const escape = (value: unknown) => {
      if (value === null || value === undefined) return '';
      const text = String(value).replace(/"/g, '""');
      return `"${text}"`;
    };

    const header =
      'id,event_type,validation_status,processing_status,occurred_at,ingested_at,processed_at,idempotency_key,last_error';
    const lines = rows.map((row) =>
      [
        escape(row.id),
        escape(row.eventType),
        escape(row.processingState?.validationStatus),
        escape(row.processingState?.processingStatus),
        escape(row.occurredAt.toISOString()),
        escape(row.processingState?.ingestedAt?.toISOString()),
        escape(row.processingState?.processedAt?.toISOString()),
        escape(row.idempotencyKey),
        escape(row.processingState?.lastError),
      ].join(','),
    );
    return [header, ...lines].join('\n');
  }
}
