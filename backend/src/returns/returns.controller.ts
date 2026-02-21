import { Body, Controller, Post, UseGuards } from '@nestjs/common';
import { UserRole } from '@prisma/client';
import { AuthenticatedGuard } from '../auth/authenticated.guard';
import { Roles } from '../auth/roles.decorator';
import { RolesGuard } from '../auth/roles.guard';
import { CreateReturnDto } from './dto/create-return.dto';
import { ReturnsService } from './returns.service';

@Controller('returns')
@UseGuards(AuthenticatedGuard, RolesGuard)
export class ReturnsController {
  constructor(private readonly returnsService: ReturnsService) {}

  @Post()
  @Roles(
    UserRole.ADMIN,
    UserRole.ADMINISTRATIVE,
    UserRole.MANAGER,
    UserRole.OPERATOR,
  )
  create(@Body() dto: CreateReturnDto) {
    return this.returnsService.create(dto);
  }
}
