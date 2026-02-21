import { randomUUID } from 'node:crypto';
import { PrismaClient, UserRole } from '@prisma/client';
import { DashboardService } from '../dashboard/dashboard.service';
import { PrismaService } from '../prisma/prisma.service';
import { ValidationRulesService } from '../validation-rules/validation-rules.service';

function chunk<T>(items: T[], size: number) {
  const batches: T[][] = [];
  for (let i = 0; i < items.length; i += size) {
    batches.push(items.slice(i, i + size));
  }
  return batches;
}

async function main() {
  const prisma = new PrismaClient();
  const prismaService = prisma as unknown as PrismaService;
  const validationRulesService = new ValidationRulesService(prismaService);
  const dashboardService = new DashboardService(prismaService, validationRulesService);

  const days = Number(process.env.DASHBOARD_PERF_DAYS ?? 30);
  const rowsPerDay = Number(process.env.DASHBOARD_PERF_ROWS_PER_DAY ?? 200);

  const user = await prisma.user.upsert({
    where: { email: 'perf@bomjesus.local' },
    update: {},
    create: {
      email: 'perf@bomjesus.local',
      name: 'Perf User',
      role: UserRole.ADMIN,
      password: 'perf',
    },
  });
  const product = await prisma.product.create({
    data: { name: `Perf Product ${Date.now()}` },
  });
  const location = await prisma.location.create({
    data: { name: `Perf Location ${Date.now()}`, type: 'CD' },
  });
  const client = await prisma.client.create({
    data: { name: `Perf Client ${Date.now()}` },
  });
  const store = await prisma.store.create({
    data: { clientId: client.id, name: `Perf Store ${Date.now()}` },
  });
  const lot = await prisma.lot.create({
    data: {
      productId: product.id,
      currentLocationId: location.id,
      boxes: 100000,
      entryDate: new Date(),
    },
  });

  const movements: Array<{
    id: string;
    lotId: string;
    movementType: 'EXIT';
    boxesDelta: number;
    happenedAt: Date;
    userId: string;
  }> = [];
  const losses: Array<{
    id: string;
    lotId: string;
    productId: string;
    locationId: string;
    reason: string;
    boxes: number;
    happenedAt: Date;
    userId: string;
  }> = [];
  const returns: Array<{
    id: string;
    lotId: string;
    clientId: string;
    storeId: string;
    productId: string;
    reason: string;
    boxes: number;
    happenedAt: Date;
    userId: string;
  }> = [];

  for (let d = 0; d < days; d += 1) {
    for (let i = 0; i < rowsPerDay; i += 1) {
      const happenedAt = new Date(Date.now() - d * 864e5 - i * 1_000);
      movements.push({
        id: randomUUID(),
        lotId: lot.id,
        movementType: 'EXIT',
        boxesDelta: -1 * (1 + (i % 4)),
        happenedAt,
        userId: user.id,
      });
      losses.push({
        id: randomUUID(),
        lotId: lot.id,
        productId: product.id,
        locationId: location.id,
        reason: 'perf_test',
        boxes: 1 + (i % 2),
        happenedAt,
        userId: user.id,
      });
      returns.push({
        id: randomUUID(),
        lotId: lot.id,
        clientId: client.id,
        storeId: store.id,
        productId: product.id,
        reason: 'perf_test',
        boxes: 1,
        happenedAt,
        userId: user.id,
      });
    }
  }

  for (const batch of chunk(movements, 1000)) {
    await prisma.stockMovement.createMany({ data: batch });
  }
  for (const batch of chunk(losses, 1000)) {
    await prisma.lossRecord.createMany({ data: batch });
  }
  for (const batch of chunk(returns, 1000)) {
    await prisma.returnRecord.createMany({ data: batch });
  }

  const t1 = Date.now();
  await dashboardService.getKpis();
  const t2 = Date.now();
  await dashboardService.getTrends(7, { clientId: client.id });
  const t3 = Date.now();

  // eslint-disable-next-line no-console
  console.log(
    JSON.stringify(
      {
        rowsInserted: {
          movements: movements.length,
          losses: losses.length,
          returns: returns.length,
        },
        timingsMs: {
          getKpis: t2 - t1,
          getTrends: t3 - t2,
        },
      },
      null,
      2,
    ),
  );

  await prisma.$disconnect();
}

void main();
