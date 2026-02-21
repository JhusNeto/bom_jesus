import { Body, Controller, Param, Post, UseGuards } from '@nestjs/common';
import { UserRole } from '@prisma/client';
import { AuthenticatedGuard } from '../auth/authenticated.guard';
import { Roles } from '../auth/roles.decorator';
import { RolesGuard } from '../auth/roles.guard';
import { EntryLotDto } from './dto/entry-lot.dto';
import { MoveLotDto } from './dto/move-lot.dto';
import { LotsService } from './lots.service';

@Controller('lots')
@UseGuards(AuthenticatedGuard, RolesGuard)
export class LotsController {
  constructor(private readonly lotsService: LotsService) {}

  @Post('entry')
  @Roles(
    UserRole.ADMIN,
    UserRole.ADMINISTRATIVE,
    UserRole.MANAGER,
    UserRole.OPERATOR,
  )
  entry(@Body() dto: EntryLotDto) {
    return this.lotsService.entry(dto);
  }

  @Post(':id/move')
  @Roles(
    UserRole.ADMIN,
    UserRole.ADMINISTRATIVE,
    UserRole.MANAGER,
    UserRole.OPERATOR,
  )
  move(@Param('id') id: string, @Body() dto: MoveLotDto) {
    return this.lotsService.move(id, dto);
  }
}
