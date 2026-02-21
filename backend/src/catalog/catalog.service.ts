import { Injectable } from '@nestjs/common';
import { ReasonType } from '@prisma/client';
import { AuditService } from '../audit/audit.service';
import { PrismaService } from '../prisma/prisma.service';
import { CreateClientDto } from './dto/create-client.dto';
import { CreateLocationDto } from './dto/create-location.dto';
import { CreateProductDto } from './dto/create-product.dto';
import { CreateReasonDto } from './dto/create-reason.dto';
import { CreateStoreDto } from './dto/create-store.dto';

@Injectable()
export class CatalogService {
  constructor(
    private readonly prisma: PrismaService,
    private readonly auditService: AuditService,
  ) {}

  listProducts() {
    return this.prisma.product.findMany({ orderBy: { name: 'asc' } });
  }

  async createProduct(dto: CreateProductDto, actorUserId: string) {
    const created = await this.prisma.product.create({
      data: { name: dto.name, active: dto.active ?? true },
    });
    await this.auditService.log({
      actorUserId,
      action: 'CATALOG_CREATE_PRODUCT',
      entityType: 'Product',
      entityId: created.id,
      payload: dto as never,
    });
    return created;
  }

  listLocations() {
    return this.prisma.location.findMany({ orderBy: { name: 'asc' } });
  }

  async createLocation(dto: CreateLocationDto, actorUserId: string) {
    const created = await this.prisma.location.create({
      data: { name: dto.name, type: dto.type, active: dto.active ?? true },
    });
    await this.auditService.log({
      actorUserId,
      action: 'CATALOG_CREATE_LOCATION',
      entityType: 'Location',
      entityId: created.id,
      payload: dto as never,
    });
    return created;
  }

  listClients() {
    return this.prisma.client.findMany({
      include: { stores: { orderBy: { name: 'asc' } } },
      orderBy: { name: 'asc' },
    });
  }

  async createClient(dto: CreateClientDto, actorUserId: string) {
    const created = await this.prisma.client.create({
      data: { name: dto.name, active: dto.active ?? true },
    });
    await this.auditService.log({
      actorUserId,
      action: 'CATALOG_CREATE_CLIENT',
      entityType: 'Client',
      entityId: created.id,
      payload: dto as never,
    });
    return created;
  }

  listStores(clientId?: string) {
    return this.prisma.store.findMany({
      where: clientId ? { clientId } : undefined,
      orderBy: [{ clientId: 'asc' }, { name: 'asc' }],
    });
  }

  async createStore(dto: CreateStoreDto, actorUserId: string) {
    const created = await this.prisma.store.create({
      data: {
        clientId: dto.clientId,
        name: dto.name,
        city: dto.city,
        active: dto.active ?? true,
      },
    });
    await this.auditService.log({
      actorUserId,
      action: 'CATALOG_CREATE_STORE',
      entityType: 'Store',
      entityId: created.id,
      payload: dto as never,
    });
    return created;
  }

  listReasons(type?: ReasonType) {
    return this.prisma.reason.findMany({
      where: type ? { type } : undefined,
      orderBy: [{ type: 'asc' }, { name: 'asc' }],
    });
  }

  async createReason(dto: CreateReasonDto, actorUserId: string) {
    const created = await this.prisma.reason.create({
      data: { type: dto.type, name: dto.name, active: dto.active ?? true },
    });
    await this.auditService.log({
      actorUserId,
      action: 'CATALOG_CREATE_REASON',
      entityType: 'Reason',
      entityId: created.id,
      payload: dto as never,
    });
    return created;
  }
}
