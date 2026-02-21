import {
  Body,
  Controller,
  Get,
  OnModuleInit,
  Post,
  Req,
  UseGuards,
} from '@nestjs/common';
import { AuthService } from './auth.service';
import { AuthenticatedGuard } from './authenticated.guard';
import { LoginDto } from './dto/login.dto';
import { LogoutDto } from './dto/logout.dto';
import { RefreshDto } from './dto/refresh.dto';

@Controller('auth')
export class AuthController implements OnModuleInit {
  constructor(private readonly authService: AuthService) {}

  async onModuleInit() {
    await this.authService.seedAdmin();
  }

  @Post('login')
  login(@Body() dto: LoginDto) {
    return this.authService.login(dto);
  }

  @Post('refresh')
  refresh(@Body() dto: RefreshDto) {
    return this.authService.refresh(dto.refreshToken);
  }

  @Post('logout')
  logout(@Body() dto: LogoutDto) {
    return this.authService.logout(dto.refreshToken);
  }

  @UseGuards(AuthenticatedGuard)
  @Get('me')
  me(
    @Req()
    req: { user: { id: string; name: string; email: string; role: string } },
  ) {
    return req.user;
  }
}
