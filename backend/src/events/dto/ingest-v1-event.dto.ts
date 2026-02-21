import { IsDateString, IsNotEmpty, IsObject, IsOptional, IsString } from 'class-validator';

export class IngestV1EventDto {
  @IsString()
  @IsNotEmpty()
  idempotency_key!: string;

  @IsString()
  @IsNotEmpty()
  event_type!: string;

  @IsDateString()
  event_ts!: string;

  @IsOptional()
  @IsString()
  device_id?: string;

  @IsOptional()
  @IsString()
  user_id?: string;

  @IsObject()
  payload!: Record<string, unknown>;
}
