import { IsDateString, IsInt, IsOptional, IsString, Min } from 'class-validator';

export class EntryLotDto {
  @IsString()
  productId!: string;

  @IsOptional()
  @IsString()
  locationId?: string;

  @IsOptional()
  @IsInt()
  @Min(0)
  boxes?: number;

  @IsOptional()
  @Min(0)
  kg?: number;

  @IsDateString()
  happenedAt!: string;

  @IsString()
  userId!: string;

  @IsString()
  idempotencyKey!: string;
}
