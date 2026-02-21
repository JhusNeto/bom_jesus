import { Module } from '@nestjs/common';
import { DashboardController } from './dashboard.controller';
import { DashboardService } from './dashboard.service';
import { ValidationRulesModule } from '../validation-rules/validation-rules.module';

@Module({
  imports: [ValidationRulesModule],
  controllers: [DashboardController],
  providers: [DashboardService],
})
export class DashboardModule {}
