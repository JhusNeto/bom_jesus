import { IsArray, IsBoolean, IsEnum, IsInt, IsOptional, IsString, Min } from 'class-validator';
import { AlertSeverity } from '@prisma/client';

export class UpdateAlertRuleDto {
  @IsOptional()
  @IsBoolean()
  active?: boolean;

  @IsOptional()
  @IsInt()
  @Min(0)
  cooldownMinutes?: number;

  @IsOptional()
  @IsEnum(AlertSeverity)
  severity?: AlertSeverity;

  @IsOptional()
  @IsArray()
  @IsString({ each: true })
  channels?: string[];
}
