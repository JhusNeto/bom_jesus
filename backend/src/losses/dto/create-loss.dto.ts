import { IsDateString, IsInt, IsOptional, IsString, Min } from 'class-validator';

export class CreateLossDto {
  @IsOptional()
  @IsString()
  lotId?: string;

  @IsOptional()
  @IsString()
  productId?: string;

  @IsString()
  locationId!: string;

  @IsString()
  reason!: string;

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
