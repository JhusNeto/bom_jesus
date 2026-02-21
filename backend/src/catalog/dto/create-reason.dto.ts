import { ReasonType } from '@prisma/client';
import { IsBoolean, IsEnum, IsNotEmpty, IsOptional, IsString } from 'class-validator';

export class CreateReasonDto {
  @IsEnum(ReasonType)
  type!: ReasonType;

  @IsString()
  @IsNotEmpty()
  name!: string;

  @IsOptional()
  @IsBoolean()
  active?: boolean;
}
