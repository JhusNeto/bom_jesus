import { Module } from '@nestjs/common';
import { CatalogV1Controller } from './catalog-v1.controller';
import { CatalogController } from './catalog.controller';
import { CatalogService } from './catalog.service';

@Module({
  controllers: [CatalogController, CatalogV1Controller],
  providers: [CatalogService],
  exports: [CatalogService],
})
export class CatalogModule {}
