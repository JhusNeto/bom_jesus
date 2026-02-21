import {
  Controller,
  Get,
  Query,
  Res,
  UseGuards,
} from '@nestjs/common';
import { UserRole } from '@prisma/client';
import type { Response } from 'express';
import { AuthenticatedGuard } from '../auth/authenticated.guard';
import { Roles } from '../auth/roles.decorator';
import { RolesGuard } from '../auth/roles.guard';
import { DashboardService } from './dashboard.service';

@Controller('dashboard')
@UseGuards(AuthenticatedGuard, RolesGuard)
export class DashboardController {
  constructor(private readonly dashboardService: DashboardService) {}

  @Get('kpis')
  @Roles(
    UserRole.ADMIN,
    UserRole.ADMINISTRATIVE,
    UserRole.MANAGER,
    UserRole.OPERATOR,
  )
  getKpis(
    @Query('from') from?: string,
    @Query('to') to?: string,
    @Query('clientId') clientId?: string,
  ) {
    return this.dashboardService.getKpis({ from, to, clientId });
  }

  @Get('summary')
  @Roles(
    UserRole.ADMIN,
    UserRole.ADMINISTRATIVE,
    UserRole.MANAGER,
    UserRole.OPERATOR,
  )
  getSummary(
    @Query('from') from?: string,
    @Query('to') to?: string,
    @Query('clientId') clientId?: string,
  ) {
    return this.dashboardService.getKpis({ from, to, clientId });
  }

  @Get('trends')
  @Roles(
    UserRole.ADMIN,
    UserRole.ADMINISTRATIVE,
    UserRole.MANAGER,
    UserRole.OPERATOR,
  )
  getTrends(
    @Query('days') days?: string,
    @Query('from') from?: string,
    @Query('to') to?: string,
    @Query('clientId') clientId?: string,
  ) {
    const parsedDays = Number(days ?? 7);
    return this.dashboardService.getTrends(
      Number.isNaN(parsedDays) ? 7 : parsedDays,
      { from, to, clientId },
    );
  }

  @Get('timeseries')
  @Roles(
    UserRole.ADMIN,
    UserRole.ADMINISTRATIVE,
    UserRole.MANAGER,
    UserRole.OPERATOR,
  )
  getTimeSeries(
    @Query('days') days?: string,
    @Query('from') from?: string,
    @Query('to') to?: string,
    @Query('clientId') clientId?: string,
  ) {
    const parsedDays = Number(days ?? 7);
    return this.dashboardService.getTrends(
      Number.isNaN(parsedDays) ? 7 : parsedDays,
      { from, to, clientId },
    );
  }

  @Get('export/kpis.csv')
  @Roles(UserRole.ADMIN, UserRole.ADMINISTRATIVE, UserRole.MANAGER)
  async exportKpis(@Res() res: Response) {
    const csv = await this.dashboardService.exportKpisCsv();
    res.setHeader('Content-Type', 'text/csv; charset=utf-8');
    res.setHeader('Content-Disposition', 'attachment; filename="kpis.csv"');
    res.send(csv);
  }

  @Get('export/trends.csv')
  @Roles(UserRole.ADMIN, UserRole.ADMINISTRATIVE, UserRole.MANAGER)
  async exportTrends(@Query('days') days: string | undefined, @Res() res: Response) {
    const parsedDays = Number(days ?? 7);
    const csv = await this.dashboardService.exportTrendsCsv(
      Number.isNaN(parsedDays) ? 7 : parsedDays,
    );
    res.setHeader('Content-Type', 'text/csv; charset=utf-8');
    res.setHeader('Content-Disposition', 'attachment; filename="trends.csv"');
    res.send(csv);
  }
}
