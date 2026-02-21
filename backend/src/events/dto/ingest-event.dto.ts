import { Type } from 'class-transformer';
import {
  IsEnum,
  IsDateString,
  IsNotEmpty,
  IsObject,
  IsOptional,
  IsString,
  ValidateNested,
} from 'class-validator';
import { RawEventType } from '@prisma/client';

class EventDataDto {
  [key: string]: unknown;
}

export class IngestEventDto {
  @IsEnum(RawEventType)
  eventType!: RawEventType;

  @IsString()
  @IsNotEmpty()
  idempotencyKey!: string;

  @IsDateString()
  occurredAt!: string;

  @IsOptional()
  @IsString()
  deviceId?: string;

  @IsOptional()
  @IsString()
  userId?: string;

  @IsObject()
  @ValidateNested()
  @Type(() => EventDataDto)
  data!: Record<string, unknown>;
}
