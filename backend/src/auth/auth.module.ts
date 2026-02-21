import { Global, Module } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { JwtModule } from '@nestjs/jwt';
import { AuthController } from './auth.controller';
import { AuthService } from './auth.service';
import { AuthenticatedGuard } from './authenticated.guard';
import { RolesGuard } from './roles.guard';

@Global()
@Module({
  imports: [
    JwtModule.registerAsync({
      inject: [ConfigService],
      useFactory: (config: ConfigService) => ({
        secret: config.get<string>('JWT_SECRET') ?? 'bom-jesus-dev-secret',
      }),
    }),
  ],
  controllers: [AuthController],
  providers: [AuthService, AuthenticatedGuard, RolesGuard],
  exports: [JwtModule, AuthenticatedGuard, RolesGuard],
})
export class AuthModule {}
