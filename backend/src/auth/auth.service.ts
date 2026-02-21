import { Injectable, UnauthorizedException } from '@nestjs/common';
import { JwtService } from '@nestjs/jwt';
import { ReasonType, UserRole } from '@prisma/client';
import { createHash } from 'node:crypto';
import { ConfigService } from '@nestjs/config';
import { compare, hash } from 'bcryptjs';
import { PrismaService } from '../prisma/prisma.service';
import { LoginDto } from './dto/login.dto';

@Injectable()
export class AuthService {
  constructor(
    private readonly prisma: PrismaService,
    private readonly jwtService: JwtService,
    private readonly configService: ConfigService,
  ) {}

  private hashToken(token: string) {
    return createHash('sha256').update(token).digest('hex');
  }

  private toSeconds(duration: string, fallback: number) {
    const match = duration.match(/^(\d+)([smhd])$/);
    if (!match) return fallback;
    const value = Number(match[1]);
    const unit = match[2];
    if (unit === 's') return value;
    if (unit === 'm') return value * 60;
    if (unit === 'h') return value * 3600;
    return value * 86400;
  }

  private async issueTokens(user: {
    id: string;
    name: string;
    email: string;
    role: UserRole;
  }) {
    const accessTokenDuration =
      this.configService.get<string>('JWT_ACCESS_EXPIRES_IN') ?? '1h';
    const refreshTokenDuration =
      this.configService.get<string>('JWT_REFRESH_EXPIRES_IN') ?? '7d';
    const accessTokenExpiresIn = this.toSeconds(accessTokenDuration, 3600);
    const refreshTokenExpiresIn = this.toSeconds(refreshTokenDuration, 7 * 86400);

    const accessToken = await this.jwtService.signAsync(
      { sub: user.id, role: user.role, email: user.email },
      { expiresIn: accessTokenExpiresIn },
    );
    const refreshToken = await this.jwtService.signAsync(
      { sub: user.id, tokenType: 'refresh' },
      { expiresIn: refreshTokenExpiresIn },
    );

    const refreshTokenHash = this.hashToken(refreshToken);
    const expiresAt = new Date();
    expiresAt.setSeconds(expiresAt.getSeconds() + refreshTokenExpiresIn);
    await this.prisma.refreshToken.create({
      data: {
        userId: user.id,
        tokenHash: refreshTokenHash,
        expiresAt,
      },
    });

    return { accessToken, refreshToken };
  }

  async login(dto: LoginDto) {
    const user = await this.prisma.user.findUnique({ where: { email: dto.email } });
    if (!user) {
      throw new UnauthorizedException('Credenciais invalidas');
    }
    const isHashedPassword = user.password.startsWith('$2');
    let isValidPassword = false;

    if (isHashedPassword) {
      isValidPassword = await compare(dto.password, user.password);
    } else if (user.password === dto.password) {
      isValidPassword = true;
      const hashedPassword = await hash(dto.password, 10);
      await this.prisma.user.update({
        where: { id: user.id },
        data: { password: hashedPassword },
      });
    }

    if (!isValidPassword) throw new UnauthorizedException('Credenciais invalidas');

    const tokens = await this.issueTokens(user);

    return {
      accessToken: tokens.accessToken,
      refreshToken: tokens.refreshToken,
      user: {
        id: user.id,
        name: user.name,
        email: user.email,
        role: user.role,
      },
    };
  }

  async refresh(refreshToken: string) {
    let payload: { sub: string; tokenType?: string };
    try {
      payload = await this.jwtService.verifyAsync(refreshToken);
    } catch {
      throw new UnauthorizedException('Refresh token invalido');
    }

    if (payload.tokenType !== 'refresh') {
      throw new UnauthorizedException('Token informado nao e refresh token');
    }

    const tokenHash = this.hashToken(refreshToken);
    const tokenInDb = await this.prisma.refreshToken.findUnique({
      where: { tokenHash },
      include: { user: true },
    });
    if (!tokenInDb || tokenInDb.revokedAt || tokenInDb.expiresAt < new Date()) {
      throw new UnauthorizedException('Refresh token expirado ou revogado');
    }

    await this.prisma.refreshToken.update({
      where: { id: tokenInDb.id },
      data: { revokedAt: new Date() },
    });

    const tokens = await this.issueTokens(tokenInDb.user);
    return { accessToken: tokens.accessToken, refreshToken: tokens.refreshToken };
  }

  async logout(refreshToken: string) {
    const tokenHash = this.hashToken(refreshToken);
    await this.prisma.refreshToken.updateMany({
      where: { tokenHash, revokedAt: null },
      data: { revokedAt: new Date() },
    });
    return { success: true };
  }

  async seedAdmin() {
    const hasAdmin = await this.prisma.user.findUnique({
      where: { email: 'admin@bomjesus.local' },
    });
    if (hasAdmin) return;

    await this.prisma.user.create({
      data: {
        name: 'Admin Bom Jesus',
        email: 'admin@bomjesus.local',
        password: await hash('admin1234', 10),
        role: UserRole.ADMIN,
      },
    });

    const client = await this.prisma.client.upsert({
      where: { name: 'Cliente Piloto' },
      update: {},
      create: { name: 'Cliente Piloto', active: true },
    });

    await Promise.all([
      this.prisma.product.upsert({
        where: { name: 'Banana Prata' },
        update: {},
        create: { name: 'Banana Prata', active: true },
      }),
      this.prisma.location.upsert({
        where: { name: 'Camara A' },
        update: {},
        create: { name: 'Camara A', type: 'CAMARA', active: true },
      }),
      this.prisma.store.upsert({
        where: { clientId_name: { clientId: client.id, name: 'Loja Central' } },
        update: {},
        create: {
          clientId: client.id,
          name: 'Loja Central',
          city: 'Bom Jesus',
          active: true,
        },
      }),
      this.prisma.reason.upsert({
        where: { type_name: { type: ReasonType.LOSS, name: 'Amassada' } },
        update: {},
        create: { type: ReasonType.LOSS, name: 'Amassada', active: true },
      }),
      this.prisma.reason.upsert({
        where: { type_name: { type: ReasonType.RETURN, name: 'Madura demais' } },
        update: {},
        create: { type: ReasonType.RETURN, name: 'Madura demais', active: true },
      }),
    ]);
  }
}
