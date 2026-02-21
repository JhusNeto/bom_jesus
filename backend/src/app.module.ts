import { Module } from '@nestjs/common';
import { ConfigModule } from '@nestjs/config';
import { ScheduleModule } from '@nestjs/schedule';
import { AppController } from './app.controller';
import { AppService } from './app.service';
import { AlertsModule } from './alerts/alerts.module';
import { AuditModule } from './audit/audit.module';
import { AuthModule } from './auth/auth.module';
import { CatalogModule } from './catalog/catalog.module';
import { DashboardModule } from './dashboard/dashboard.module';
import { EventsModule } from './events/events.module';
import { JobsModule } from './jobs/jobs.module';
import { LotsModule } from './lots/lots.module';
import { LossesModule } from './losses/losses.module';
import { PrismaModule } from './prisma/prisma.module';
import { ReturnsModule } from './returns/returns.module';
import { ReviewsModule } from './reviews/reviews.module';
import { UploadsModule } from './uploads/uploads.module';
import { ValidationRulesModule } from './validation-rules/validation-rules.module';

@Module({
  imports: [
    ConfigModule.forRoot({ isGlobal: true }),
    ScheduleModule.forRoot(),
    AlertsModule,
    AuditModule,
    PrismaModule,
    AuthModule,
    CatalogModule,
    EventsModule,
    LotsModule,
    LossesModule,
    ReturnsModule,
    ReviewsModule,
    UploadsModule,
    ValidationRulesModule,
    DashboardModule,
    JobsModule,
  ],
  controllers: [AppController],
  providers: [AppService],
})
export class AppModule {}
