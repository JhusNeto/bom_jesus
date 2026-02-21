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
import { CreateReturnDto } from './dto/create-return.dto';

@Injectable()
export class ReturnsService {
  constructor(private readonly prisma: PrismaService) {}

  async create(dto: CreateReturnDto) {
    if (dto.boxes === undefined && dto.kg === undefined) {
      throw new BadRequestException('Informe caixas ou kg.');
    }

    const duplicated = await this.prisma.rawEvent.findUnique({
      where: { idempotencyKey: dto.idempotencyKey },
    });
    if (duplicated) return { duplicated: true, rawEventId: duplicated.id };

    const result = await this.prisma.$transaction(async (tx) => {
      const raw = await tx.rawEvent.create({
        data: {
          eventType: RawEventType.RETURN_REGISTERED,
          source: 'pwa',
          payloadJson: dto as unknown as Prisma.InputJsonValue,
          userId: dto.userId,
          occurredAt: new Date(dto.happenedAt),
          validationStatus: ValidationStatus.VALID,
          processingStatus: ProcessingStatus.PROCESSED,
          processedAt: new Date(),
          syncStatus: EventSyncStatus.PROCESSED,
          idempotencyKey: dto.idempotencyKey,
        },
      });

      const ret = await tx.returnRecord.create({
        data: {
          lotId: dto.lotId,
          clientId: dto.clientId,
          storeId: dto.storeId,
          productId: dto.productId,
          reason: dto.reason,
          boxes: dto.boxes ?? 0,
          kg: dto.kg === undefined ? null : new Prisma.Decimal(dto.kg),
          photoUrl: dto.photoUrl,
          happenedAt: new Date(dto.happenedAt),
          userId: dto.userId,
          sourceRawEventId: raw.id,
        },
      });

      if (dto.lotId) {
        await tx.stockMovement.create({
          data: {
            lotId: dto.lotId,
            movementType: MovementType.RETURN,
            boxesDelta: (dto.boxes ?? 0) * -1,
            kgDelta:
              dto.kg === undefined ? null : new Prisma.Decimal(dto.kg * -1),
            happenedAt: new Date(dto.happenedAt),
            userId: dto.userId,
            sourceRawEventId: raw.id,
          },
        });
      }

      return { returnId: ret.id, rawEventId: raw.id };
    });

    return { duplicated: false, ...result };
  }
}
