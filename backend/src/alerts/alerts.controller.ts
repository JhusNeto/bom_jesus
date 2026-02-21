import {
  Body,
  Controller,
  Get,
  Param,
  Patch,
  Post,
  Req,
  UseGuards,
} from '@nestjs/common';
import { ApiBearerAuth, ApiTags } from '@nestjs/swagger';
import { UserRole } from '@prisma/client';
import { AuthenticatedGuard } from '../auth/authenticated.guard';
import { RolesGuard } from '../auth/roles.guard';
import { Roles } from '../auth/roles.decorator';
import { AlertsService } from './alerts.service';
import { PushSubscriptionDto } from './dto/push-subscription.dto';
import { UpdateAlertRuleDto } from './dto/update-alert-rule.dto';

@ApiTags('alerts')
@Controller('alerts')
@UseGuards(AuthenticatedGuard, RolesGuard)
export class AlertsController {
  constructor(private readonly alertsService: AlertsService) {}

  @Get('rules')
  @Roles(UserRole.ADMIN, UserRole.MANAGER)
  @ApiBearerAuth()
  getRules() {
    return this.alertsService.getRules();
  }

  @Patch('rules/:id')
  @Roles(UserRole.ADMIN)
  @ApiBearerAuth()
  updateRule(@Param('id') id: string, @Body() dto: UpdateAlertRuleDto) {
    return this.alertsService.updateRule(id, {
      active: dto.active,
      cooldownMinutes: dto.cooldownMinutes,
      severity: dto.severity,
      channels: dto.channels,
    });
  }

  @Get('events')
  @Roles(UserRole.ADMIN, UserRole.MANAGER)
  @ApiBearerAuth()
  getEvents() {
    return this.alertsService.getRecentEvents(undefined, 50);
  }

  @Post('push-subscription')
  @ApiBearerAuth()
  async savePushSubscription(
    @Body() dto: PushSubscriptionDto,
    @Req() req: { user: { id: string } },
  ) {
    return this.alertsService.savePushSubscription(req.user.id, dto);
  }

  @Get('vapid-public-key')
  @ApiBearerAuth()
  getVapidPublicKey() {
    const key = this.alertsService.getVapidPublicKey();
    return { publicKey: key };
  }
}
