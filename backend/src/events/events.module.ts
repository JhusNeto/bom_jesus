import { Module } from '@nestjs/common';
import { EventsController } from './events.controller';
import { EventsService } from './events.service';
import { ValidationRulesModule } from '../validation-rules/validation-rules.module';

@Module({
  imports: [ValidationRulesModule],
  controllers: [EventsController],
  providers: [EventsService],
  exports: [EventsService],
})
export class EventsModule {}
