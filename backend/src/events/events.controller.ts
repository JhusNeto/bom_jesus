import {
  Body,
  Controller,
  Get,
  Param,
  Post,
  Query,
  Res,
  UseGuards,
} from '@nestjs/common';
import { ProcessingStatus, RawEventType, UserRole } from '@prisma/client';
import type { Response } from 'express';
import { AuthenticatedGuard } from '../auth/authenticated.guard';
import { Roles } from '../auth/roles.decorator';
import { RolesGuard } from '../auth/roles.guard';
import { IngestEventDto } from './dto/ingest-event.dto';
import { IngestV1EventDto } from './dto/ingest-v1-event.dto';
import { EventsService } from './events.service';

@Controller('events')
@UseGuards(AuthenticatedGuard, RolesGuard)
export class EventsController {
  constructor(private readonly eventsService: EventsService) {}

  private normalizePayload(payload: Record<string, unknown>) {
    const map: Record<string, string> = {
      lot_id: 'lotId',
      product_id: 'productId',
      location_id: 'locationId',
      from_location_id: 'fromLocationId',
      to_location_id: 'toLocationId',
      client_id: 'clientId',
      store_id: 'storeId',
      qty_boxes: 'boxes',
      qty_kg: 'kg',
      photo_url: 'photoUrl',
      event_ts: 'occurredAt',
      user_id: 'userId',
    };
    return Object.entries(payload).reduce(
      (acc, [key, value]) => {
        const mapped = map[key] ?? key;
        acc[mapped] = value;
        return acc;
      },
      {} as Record<string, unknown>,
    );
  }

  private parseProcessingStatus(status?: string): ProcessingStatus | undefined {
    if (!status) return undefined;
    if (
      status === ProcessingStatus.PENDING ||
      status === ProcessingStatus.PROCESSED ||
      status === ProcessingStatus.FAILED
    ) {
      return status;
    }
    return undefined;
  }

  private parseEventType(eventType?: string): RawEventType | undefined {
    if (!eventType) return undefined;
    if (Object.values(RawEventType).includes(eventType as RawEventType)) {
      return eventType as RawEventType;
    }
    return undefined;
  }

  private parseExternalEventType(eventType: string): RawEventType | undefined {
    const normalized = eventType.toLowerCase();
    if (normalized === 'lot_received') return RawEventType.LOT_ENTRY_REGISTERED;
    if (normalized === 'stock_moved') return RawEventType.LOT_MOVED;
    if (normalized === 'loss_recorded') return RawEventType.LOSS_REGISTERED;
    if (normalized === 'return_recorded') return RawEventType.RETURN_REGISTERED;
    return this.parseEventType(eventType);
  }

  @Post()
  @Roles(
    UserRole.ADMIN,
    UserRole.ADMINISTRATIVE,
    UserRole.MANAGER,
    UserRole.OPERATOR,
  )
  async ingestUnified(@Body() dto: IngestV1EventDto) {
    const parsedType = this.parseExternalEventType(dto.event_type);
    if (!parsedType) {
      return {
        raw_event_id: null,
        validation_status: 'invalid',
        processing_status: 'failed',
        message: 'event_type invalido',
      };
    }
    const result = await this.eventsService.ingest({
      eventType: parsedType,
      idempotencyKey: dto.idempotency_key,
      occurredAt: dto.event_ts,
      deviceId: dto.device_id,
      userId: dto.user_id,
      data: this.normalizePayload(dto.payload),
    });

    return {
      raw_event_id: result.rawEventId,
      validation_status: result.validationStatus?.toLowerCase() ?? 'valid',
      processing_status: result.processingStatus?.toLowerCase() ?? 'pending',
      duplicated: result.duplicated,
    };
  }

  @Post('ingest')
  @Roles(
    UserRole.ADMIN,
    UserRole.ADMINISTRATIVE,
    UserRole.MANAGER,
    UserRole.OPERATOR,
  )
  ingest(@Body() dto: IngestEventDto) {
    return this.eventsService.ingest(dto);
  }

  @Get('raw')
  @Roles(UserRole.ADMIN, UserRole.ADMINISTRATIVE, UserRole.MANAGER)
  listRaw(
    @Query('status') status?: string,
    @Query('eventType') eventType?: string,
    @Query('idempotencyKey') idempotencyKey?: string,
    @Query('from') from?: string,
    @Query('to') to?: string,
    @Query('limit') limit?: string,
  ) {
    const parsedLimit = Number(limit ?? 200);
    return this.eventsService.listRaw({
      status: this.parseProcessingStatus(status),
      eventType: this.parseEventType(eventType),
      idempotencyKey,
      from,
      to,
      limit: Number.isNaN(parsedLimit) ? 200 : parsedLimit,
    });
  }

  @Get()
  @Roles(UserRole.ADMIN, UserRole.ADMINISTRATIVE, UserRole.MANAGER)
  listUnified(
    @Query('status') status?: string,
    @Query('event_type') eventType?: string,
    @Query('idempotency_key') idempotencyKey?: string,
    @Query('from') from?: string,
    @Query('to') to?: string,
    @Query('limit') limit?: string,
  ) {
    const parsedLimit = Number(limit ?? 200);
    const parsedType = eventType ? this.parseExternalEventType(eventType) : undefined;
    return this.eventsService.listRaw({
      status: this.parseProcessingStatus(status),
      eventType: parsedType,
      idempotencyKey,
      from,
      to,
      limit: Number.isNaN(parsedLimit) ? 200 : parsedLimit,
    });
  }

  @Get('raw/export.csv')
  @Roles(UserRole.ADMIN, UserRole.ADMINISTRATIVE, UserRole.MANAGER)
  async exportRawCsv(
    @Query('status') status: string | undefined,
    @Query('eventType') eventType: string | undefined,
    @Query('idempotencyKey') idempotencyKey: string | undefined,
    @Query('from') from: string | undefined,
    @Query('to') to: string | undefined,
    @Query('limit') limit: string | undefined,
    @Res() res: Response,
  ) {
    const parsedLimit = Number(limit ?? 500);
    const csv = await this.eventsService.exportRawCsv({
      status: this.parseProcessingStatus(status),
      eventType: this.parseEventType(eventType),
      idempotencyKey,
      from,
      to,
      limit: Number.isNaN(parsedLimit) ? 500 : parsedLimit,
    });
    res.setHeader('Content-Type', 'text/csv; charset=utf-8');
    res.setHeader('Content-Disposition', 'attachment; filename="raw-events.csv"');
    res.send(csv);
  }

  @Post('process')
  @Roles(UserRole.ADMIN, UserRole.ADMINISTRATIVE, UserRole.MANAGER)
  processPending(@Query('limit') limit?: string) {
    const parsed = Number(limit ?? 100);
    return this.eventsService.processPending(Number.isNaN(parsed) ? 100 : parsed);
  }

  @Post('reprocess/:id')
  @Roles(UserRole.ADMIN, UserRole.ADMINISTRATIVE, UserRole.MANAGER)
  reprocess(@Param('id') id: string) {
    return this.eventsService.reprocess(id);
  }

  @Post('reprocess-failed')
  @Roles(UserRole.ADMIN, UserRole.ADMINISTRATIVE, UserRole.MANAGER)
  reprocessFailed(@Query('limit') limit?: string) {
    const parsed = Number(limit ?? 100);
    return this.eventsService.reprocessFailed(Number.isNaN(parsed) ? 100 : parsed);
  }

  @Get('metrics')
  @Roles(UserRole.ADMIN, UserRole.ADMINISTRATIVE, UserRole.MANAGER)
  metrics() {
    return this.eventsService.getPipelineMetrics();
  }
}
