import { IsOptional, IsString } from 'class-validator';

export class ResolveIssueDto {
  @IsOptional()
  @IsString()
  notes?: string;
}
