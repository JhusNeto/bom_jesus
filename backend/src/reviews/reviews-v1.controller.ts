import {
  Body,
  Controller,
  Get,
  Param,
  Patch,
  Query,
  Req,
  UseGuards,
} from '@nestjs/common';
import { UserRole } from '@prisma/client';
import { AuthenticatedGuard } from '../auth/authenticated.guard';
import { Roles } from '../auth/roles.decorator';
import { RolesGuard } from '../auth/roles.guard';
import { ResolveIssueDto } from './dto/resolve-issue.dto';
import { ReviewsService } from './reviews.service';

@Controller('review')
@UseGuards(AuthenticatedGuard, RolesGuard)
export class ReviewsV1Controller {
  constructor(private readonly reviewsService: ReviewsService) {}

  @Get('needs-review')
  @Roles(UserRole.ADMIN, UserRole.ADMINISTRATIVE, UserRole.MANAGER)
  list(
    @Query('resolved') resolved?: string,
    @Query('severity') severity?: string,
    @Query('issueCode') issueCode?: string,
    @Query('page') page?: string,
    @Query('pageSize') pageSize?: string,
  ) {
    const parsedPage = Number(page ?? 1);
    const parsedPageSize = Number(pageSize ?? 20);
    return this.reviewsService.listValidationIssues({
      resolved: resolved === undefined ? false : resolved === 'true',
      severity,
      issueCode,
      page: Number.isNaN(parsedPage) ? 1 : Math.max(1, parsedPage),
      pageSize: Number.isNaN(parsedPageSize)
        ? 20
        : Math.min(100, Math.max(1, parsedPageSize)),
    });
  }

  @Patch('needs-review/:id')
  @Roles(UserRole.ADMIN, UserRole.ADMINISTRATIVE, UserRole.MANAGER)
  resolve(
    @Param('id') id: string,
    @Body() dto: ResolveIssueDto,
    @Req() req: { user: { id: string } },
  ) {
    return this.reviewsService.resolveValidationIssue({
      id,
      actorUserId: req.user.id,
      notes: dto.notes,
    });
  }
}
