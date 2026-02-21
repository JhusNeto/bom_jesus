import { IsDateString, IsInt, IsOptional, IsString, Min } from 'class-validator';

export class CreateReturnDto {
  @IsOptional()
  @IsString()
  lotId?: string;

  @IsString()
  clientId!: string;

  @IsString()
  storeId!: string;

  @IsString()
  productId!: string;

  @IsString()
  reason!: string;

  @IsOptional()
  @IsInt()
  @Min(0)
  boxes?: number;

  @IsOptional()
  @Min(0)
  kg?: number;

  @IsOptional()
  @IsString()
  photoUrl?: string;

  @IsDateString()
  happenedAt!: string;

  @IsString()
  userId!: string;

  @IsString()
  idempotencyKey!: string;
}
