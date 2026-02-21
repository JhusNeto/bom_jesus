import {
  CanActivate,
  ExecutionContext,
  Injectable,
  UnauthorizedException,
} from '@nestjs/common';
import { JwtService } from '@nestjs/jwt';
import { PrismaService } from '../prisma/prisma.service';

@Injectable()
export class AuthenticatedGuard implements CanActivate {
  constructor(
    private readonly prisma: PrismaService,
    private readonly jwtService: JwtService,
  ) {}

  async canActivate(context: ExecutionContext): Promise<boolean> {
    const request = context.switchToHttp().getRequest<{
      headers: Record<string, string | undefined>;
      user?: unknown;
    }>();
    const authHeader = request.headers.authorization;
    if (!authHeader?.startsWith('Bearer ')) {
      throw new UnauthorizedException('Token ausente');
    }

    const token = authHeader.slice('Bearer '.length);
    let payload: { sub: string; role: string };
    try {
      payload = await this.jwtService.verifyAsync<{ sub: string; role: string }>(token);
    } catch {
      throw new UnauthorizedException('Token invalido');
    }
    const user = await this.prisma.user.findUnique({
      where: { id: payload.sub },
      select: { id: true, name: true, email: true, role: true },
    });
    if (!user) throw new UnauthorizedException('Usuario nao encontrado');

    request.user = user;
    return true;
  }
}
