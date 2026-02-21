/**
 * Seed de dados para testes/EAT.
 * Uso: npx ts-node -r tsconfig-paths/register scripts/seed-for-test.ts
 * Requer: DATABASE_URL no .env
 */

import { PrismaClient, UserRole } from '@prisma/client';
import * as bcrypt from 'bcryptjs';

const prisma = new PrismaClient();

async function main() {
  const admin = await prisma.user.upsert({
    where: { email: 'admin@bomjesus.local' },
    update: {},
    create: {
      name: 'Admin Bom Jesus',
      email: 'admin@bomjesus.local',
      password: await bcrypt.hash('admin1234', 10),
      role: UserRole.ADMIN,
    },
  });

  const operator = await prisma.user.upsert({
    where: { email: 'operador@bomjesus.local' },
    update: {},
    create: {
      name: 'Operador Teste',
      email: 'operador@bomjesus.local',
      password: await bcrypt.hash('oper1234', 10),
      role: UserRole.OPERATOR,
    },
  });

  const product = await prisma.product.upsert({
    where: { name: 'Banana Prata' },
    update: {},
    create: { name: 'Banana Prata', active: true },
  });

  const location = await prisma.location.upsert({
    where: { name: 'Camara A' },
    update: {},
    create: { name: 'Camara A', type: 'CAMARA', active: true },
  });

  const client = await prisma.client.upsert({
    where: { name: 'Cliente Piloto' },
    update: {},
    create: { name: 'Cliente Piloto', active: true },
  });

  const store = await prisma.store.upsert({
    where: { clientId_name: { clientId: client.id, name: 'Loja Central' } },
    update: {},
    create: {
      clientId: client.id,
      name: 'Loja Central',
      city: 'Bom Jesus',
      active: true,
    },
  });

  console.log('Seed concluído:', {
    admin: admin.email,
    operator: operator.email,
    product: product.name,
    location: location.name,
    client: client.name,
    store: store.name,
  });
}

main()
  .then(() => prisma.$disconnect())
  .catch((e) => {
    console.error(e);
    prisma.$disconnect();
    process.exit(1);
  });
