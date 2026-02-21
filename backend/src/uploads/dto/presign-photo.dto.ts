import { IsNotEmpty, IsOptional, IsString } from 'class-validator';

export class PresignPhotoDto {
  @IsString()
  @IsNotEmpty()
  fileName!: string;

  @IsOptional()
  @IsString()
  contentType?: string;
}
