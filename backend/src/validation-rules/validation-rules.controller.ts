import { Body, Controller, Get, Patch, UseGuards } from '@nestjs/common';
import { UserRole } from '@prisma/client';
import { AuthenticatedGuard } from '../auth/authenticated.guard';
import { Roles } from '../auth/roles.decorator';
import { RolesGuard } from '../auth/roles.guard';
import {
  ValidationRuleKey,
  ValidationRulesService,
} from './validation-rules.service';

@Controller('validation-rules')
@UseGuards(AuthenticatedGuard, RolesGuard)
export class ValidationRulesController {
  constructor(private readonly validationRulesService: ValidationRulesService) {}

  @Get()
  @Roles(UserRole.ADMIN, UserRole.ADMINISTRATIVE, UserRole.MANAGER)
  getRules() {
    return this.validationRulesService.getRules();
  }

  @Patch()
  @Roles(UserRole.ADMIN, UserRole.ADMINISTRATIVE, UserRole.MANAGER)
  setRule(@Body() body: { key: ValidationRuleKey; valueNumber: number }) {
    return this.validationRulesService.setRule(body.key, body.valueNumber);
  }
}
