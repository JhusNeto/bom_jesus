import { Body, Controller, Post, UseGuards } from '@nestjs/common';
import { UserRole } from '@prisma/client';
import { AuthenticatedGuard } from '../auth/authenticated.guard';
import { Roles } from '../auth/roles.decorator';
import { RolesGuard } from '../auth/roles.guard';
import { CreateLossDto } from './dto/create-loss.dto';
import { LossesService } from './losses.service';

@Controller('losses')
@UseGuards(AuthenticatedGuard, RolesGuard)
export class LossesController {
  constructor(private readonly lossesService: LossesService) {}

  @Post()
  @Roles(
    UserRole.ADMIN,
    UserRole.ADMINISTRATIVE,
    UserRole.MANAGER,
    UserRole.OPERATOR,
  )
  create(@Body() dto: CreateLossDto) {
    return this.lossesService.create(dto);
  }
}
