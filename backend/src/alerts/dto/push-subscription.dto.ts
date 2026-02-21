import { IsObject, IsOptional, IsString, ValidateNested } from 'class-validator';
import { Type } from 'class-transformer';

class SubscriptionKeysDto {
  @IsString()
  p256dh!: string;

  @IsString()
  auth!: string;
}

export class PushSubscriptionDto {
  @IsString()
  endpoint!: string;

  @IsOptional()
  @IsString()
  p256dh?: string;

  @IsOptional()
  @IsString()
  auth?: string;

  @IsOptional()
  @IsObject()
  @ValidateNested()
  @Type(() => SubscriptionKeysDto)
  keys?: SubscriptionKeysDto;
}
