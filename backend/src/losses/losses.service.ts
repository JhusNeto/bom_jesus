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
import { CreateLossDto } from './dto/create-loss.dto';

@Injectable()
export class LossesService {
  constructor(private readonly prisma: PrismaService) {}

  async create(dto: CreateLossDto) {
    if (dto.boxes === undefined && dto.kg === undefined) {
      throw new BadRequestException('Informe caixas ou kg.');
    }
    if (!dto.locationId) {
      throw new BadRequestException('Informe locationId.');
    }
    if (!dto.lotId && !dto.productId) {
      throw new BadRequestException('Informe lotId ou productId.');
    }

    const duplicated = await this.prisma.rawEvent.findUnique({
      where: { idempotencyKey: dto.idempotencyKey },
    });
    if (duplicated) return { duplicated: true, rawEventId: duplicated.id };

    if (!dto.lotId) {
      const raw = await this.prisma.rawEvent.create({
        data: {
          eventType: RawEventType.LOSS_REGISTERED,
          source: 'pwa',
          payloadJson: dto as unknown as Prisma.InputJsonValue,
          userId: dto.userId,
          occurredAt: new Date(dto.happenedAt),
          validationStatus: ValidationStatus.NEEDS_REVIEW,
          processingStatus: ProcessingStatus.PENDING,
          syncStatus: EventSyncStatus.RECEIVED,
          idempotencyKey: dto.idempotencyKey,
        },
      });
      await this.prisma.validationIssue.create({
        data: {
          rawEventId: raw.id,
          issueCode: 'LOSS_WITHOUT_LOT',
          severity: 'warning',
          details:
            'Perda sem lotId foi registrada para revisao e nao afetou o ledger.',
        },
      });
      return { duplicated: false, acceptedForReview: true, rawEventId: raw.id };
    }

    const lotId = dto.lotId as string;
    const lot = await this.prisma.lot.findUnique({ where: { id: lotId } });
    if (!lot) throw new BadRequestException('Lote nao encontrado.');
    const resolvedProductId = dto.productId ?? lot.productId;

    const flagInconsistency =
      (dto.boxes !== undefined && dto.boxes > lot.boxes) ||
      (dto.kg !== undefined &&
        lot.kg !== null &&
        dto.kg > Number(lot.kg.toString()));

    const result = await this.prisma.$transaction(async (tx) => {
      const raw = await tx.rawEvent.create({
        data: {
          eventType: RawEventType.LOSS_REGISTERED,
          source: 'pwa',
          payloadJson: dto as unknown as Prisma.InputJsonValue,
          userId: dto.userId,
          occurredAt: new Date(dto.happenedAt),
          validationStatus: flagInconsistency
            ? ValidationStatus.NEEDS_REVIEW
            : ValidationStatus.VALID,
          processingStatus: ProcessingStatus.PROCESSED,
          processedAt: new Date(),
          syncStatus: EventSyncStatus.PROCESSED,
          idempotencyKey: dto.idempotencyKey,
        },
      });

      const loss = await tx.lossRecord.create({
        data: {
          lotId,
          productId: resolvedProductId,
          locationId: dto.locationId,
          reason: dto.reason,
          boxes: dto.boxes ?? 0,
          kg: dto.kg === undefined ? null : new Prisma.Decimal(dto.kg),
          happenedAt: new Date(dto.happenedAt),
          userId: dto.userId,
          sourceRawEventId: raw.id,
        },
      });

      await tx.stockMovement.create({
        data: {
          lotId,
          movementType: MovementType.LOSS,
          boxesDelta: (dto.boxes ?? 0) * -1,
          kgDelta: dto.kg === undefined ? null : new Prisma.Decimal(dto.kg * -1),
          happenedAt: new Date(dto.happenedAt),
          userId: dto.userId,
          sourceRawEventId: raw.id,
        },
      });

      await tx.lot.update({
        where: { id: lotId },
        data: {
          boxes: Math.max(0, (lot?.boxes ?? 0) - (dto.boxes ?? 0)),
          kg:
            dto.kg === undefined || lot?.kg === null
              ? lot?.kg
              : new Prisma.Decimal(
                  Math.max(0, Number((lot?.kg ?? 0).toString()) - dto.kg),
                ),
          inconsistent: flagInconsistency || (lot?.inconsistent ?? false),
        },
      });

      if (flagInconsistency) {
        await tx.validationIssue.create({
          data: {
            rawEventId: raw.id,
            issueCode: 'LOSS_OVER_STOCK',
            severity: 'warning',
            details: 'Perda registrada acima do saldo disponivel.',
          },
        });
      }

      return { lossId: loss.id, rawEventId: raw.id, flagged: flagInconsistency };
    });

    return { duplicated: false, ...result };
  }
}
