import { BadRequestException, Injectable } from '@nestjs/common';
import {
  EventSyncStatus,
  MovementType,
  Prisma,
  ProcessingStatus,
  RawEventType,
  ValidationStatus,
} from '@prisma/client';
import { PrismaService } from '../prisma/prisma.service';
import { EntryLotDto } from './dto/entry-lot.dto';
import { MoveLotDto } from './dto/move-lot.dto';

@Injectable()
export class LotsService {
  constructor(private readonly prisma: PrismaService) {}

  private ensureAmount(boxes?: number, kg?: number) {
    if (boxes === undefined && kg === undefined) {
      throw new BadRequestException('Informe caixas ou kg.');
    }
  }

  async entry(dto: EntryLotDto) {
    this.ensureAmount(dto.boxes, dto.kg);

    const duplicated = await this.prisma.rawEvent.findUnique({
      where: { idempotencyKey: dto.idempotencyKey },
    });
    if (duplicated) return { duplicated: true, rawEventId: duplicated.id };

    const result = await this.prisma.$transaction(async (tx) => {
      const raw = await tx.rawEvent.create({
        data: {
          eventType: RawEventType.LOT_ENTRY_REGISTERED,
          source: 'pwa',
          payloadJson: dto as unknown as Prisma.InputJsonValue,
          deviceId: null,
          userId: dto.userId,
          occurredAt: new Date(dto.happenedAt),
          validationStatus: ValidationStatus.VALID,
          processingStatus: ProcessingStatus.PROCESSED,
          processedAt: new Date(),
          syncStatus: EventSyncStatus.PROCESSED,
          idempotencyKey: dto.idempotencyKey,
        },
      });

      const lot = await tx.lot.create({
        data: {
          productId: dto.productId,
          currentLocationId: dto.locationId,
          boxes: dto.boxes ?? 0,
          kg: dto.kg === undefined ? null : new Prisma.Decimal(dto.kg),
          entryDate: new Date(dto.happenedAt),
        },
      });

      await tx.stockMovement.create({
        data: {
          lotId: lot.id,
          movementType: MovementType.ENTRY,
          boxesDelta: dto.boxes ?? 0,
          kgDelta: dto.kg === undefined ? null : new Prisma.Decimal(dto.kg),
          happenedAt: new Date(dto.happenedAt),
          toLocationId: dto.locationId,
          userId: dto.userId,
          sourceRawEventId: raw.id,
        },
      });

      return { lotId: lot.id, rawEventId: raw.id };
    });

    return { duplicated: false, ...result };
  }

  async move(lotId: string, dto: MoveLotDto) {
    this.ensureAmount(dto.boxes, dto.kg);

    const lot = await this.prisma.lot.findUnique({ where: { id: lotId } });
    if (!lot) throw new BadRequestException('Lote nao encontrado.');

    const duplicated = await this.prisma.rawEvent.findUnique({
      where: { idempotencyKey: dto.idempotencyKey },
    });
    if (duplicated) return { duplicated: true, rawEventId: duplicated.id };

    let shouldFlagIssue = false;
    if (dto.boxes !== undefined && dto.boxes > lot.boxes) {
      shouldFlagIssue = true;
    }
    if (
      dto.kg !== undefined &&
      lot.kg !== null &&
      Number(lot.kg.toString()) < Number(dto.kg)
    ) {
      shouldFlagIssue = true;
    }

    const result = await this.prisma.$transaction(async (tx) => {
      const raw = await tx.rawEvent.create({
        data: {
          eventType: RawEventType.LOT_MOVED,
          source: 'pwa',
          payloadJson: { lotId, ...dto } as unknown as Prisma.InputJsonValue,
          userId: dto.userId,
          occurredAt: new Date(dto.happenedAt),
          validationStatus: shouldFlagIssue
            ? ValidationStatus.NEEDS_REVIEW
            : ValidationStatus.VALID,
          processingStatus: ProcessingStatus.PROCESSED,
          processedAt: new Date(),
          syncStatus: EventSyncStatus.PROCESSED,
          idempotencyKey: dto.idempotencyKey,
        },
      });

      const updated = await tx.lot.update({
        where: { id: lotId },
        data: {
          boxes:
            dto.boxes === undefined
              ? lot.boxes
              : Math.max(0, lot.boxes - dto.boxes),
          kg:
            dto.kg === undefined || lot.kg === null
              ? lot.kg
              : new Prisma.Decimal(
                  Math.max(0, Number(lot.kg.toString()) - Number(dto.kg)),
                ),
          currentLocationId: dto.toLocationId ?? lot.currentLocationId,
          inconsistent: shouldFlagIssue || lot.inconsistent,
        },
      });

      await tx.stockMovement.create({
        data: {
          lotId,
          movementType: MovementType.MOVE,
          boxesDelta: (dto.boxes ?? 0) * -1,
          kgDelta: dto.kg === undefined ? null : new Prisma.Decimal(dto.kg * -1),
          happenedAt: new Date(dto.happenedAt),
          fromLocationId: dto.fromLocationId,
          toLocationId: dto.toLocationId,
          userId: dto.userId,
          sourceRawEventId: raw.id,
        },
      });

      if (shouldFlagIssue) {
        await tx.validationIssue.create({
          data: {
            rawEventId: raw.id,
            issueCode: 'MOVEMENT_OVER_STOCK',
            severity: 'warning',
            details: 'Movimentacao maior que saldo disponivel.',
          },
        });
      }

      return { lot: updated, rawEventId: raw.id, flagged: shouldFlagIssue };
    });

    return { duplicated: false, ...result };
  }
}
