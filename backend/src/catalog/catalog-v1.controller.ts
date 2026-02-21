import {
  Body,
  Controller,
  Get,
  Post,
  Query,
  Req,
  UseGuards,
} from '@nestjs/common';
import { UserRole } from '@prisma/client';
import { AuthenticatedGuard } from '../auth/authenticated.guard';
import { Roles } from '../auth/roles.decorator';
import { RolesGuard } from '../auth/roles.guard';
import { CatalogService } from './catalog.service';
import { CreateClientDto } from './dto/create-client.dto';
import { CreateLocationDto } from './dto/create-location.dto';
import { CreateProductDto } from './dto/create-product.dto';
import { CreateStoreDto } from './dto/create-store.dto';

@Controller()
@UseGuards(AuthenticatedGuard, RolesGuard)
export class CatalogV1Controller {
  constructor(private readonly catalogService: CatalogService) {}

  @Get('products')
  listProducts() {
    return this.catalogService.listProducts();
  }

  @Post('products')
  @Roles(UserRole.ADMIN, UserRole.ADMINISTRATIVE, UserRole.MANAGER)
  createProduct(@Body() dto: CreateProductDto, @Req() req: { user: { id: string } }) {
    return this.catalogService.createProduct(dto, req.user.id);
  }

  @Get('locations')
  listLocations() {
    return this.catalogService.listLocations();
  }

  @Post('locations')
  @Roles(UserRole.ADMIN, UserRole.ADMINISTRATIVE, UserRole.MANAGER)
  createLocation(@Body() dto: CreateLocationDto, @Req() req: { user: { id: string } }) {
    return this.catalogService.createLocation(dto, req.user.id);
  }

  @Get('clients')
  listClients() {
    return this.catalogService.listClients();
  }

  @Post('clients')
  @Roles(UserRole.ADMIN, UserRole.ADMINISTRATIVE, UserRole.MANAGER)
  createClient(@Body() dto: CreateClientDto, @Req() req: { user: { id: string } }) {
    return this.catalogService.createClient(dto, req.user.id);
  }

  @Get('stores')
  listStores(@Query('clientId') clientId?: string) {
    return this.catalogService.listStores(clientId);
  }

  @Post('stores')
  @Roles(UserRole.ADMIN, UserRole.ADMINISTRATIVE, UserRole.MANAGER)
  createStore(@Body() dto: CreateStoreDto, @Req() req: { user: { id: string } }) {
    return this.catalogService.createStore(dto, req.user.id);
  }
}
