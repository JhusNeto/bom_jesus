import { Module } from '@nestjs/common';
import { AlertsModule } from '../alerts/alerts.module';
import { EventsModule } from '../events/events.module';
import { JobsService } from './jobs.service';

@Module({
  imports: [AlertsModule, EventsModule],
  providers: [JobsService],
})
export class JobsModule {}
