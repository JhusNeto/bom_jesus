import { CatalogService } from './catalog.service';
import { ReasonType } from '@prisma/client';

describe('CatalogService', () => {
  const prismaMock = {
    product: { findMany: jest.fn(), create: jest.fn() },
    location: { findMany: jest.fn(), create: jest.fn() },
    client: { findMany: jest.fn(), create: jest.fn() },
    store: { findMany: jest.fn(), create: jest.fn() },
    reason: { findMany: jest.fn(), create: jest.fn() },
  };
  const auditServiceMock = { log: jest.fn() };

  const service = new CatalogService(prismaMock as never, auditServiceMock as never);

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('lista produtos ordenados por nome', async () => {
    prismaMock.product.findMany.mockResolvedValue([{ id: '1', name: 'Banana' }]);
    const result = await service.listProducts();
    expect(prismaMock.product.findMany).toHaveBeenCalledWith({
      orderBy: { name: 'asc' },
    });
    expect(result).toHaveLength(1);
  });

  it('cria motivo com ativo default true', async () => {
    prismaMock.reason.create.mockResolvedValue({ id: 'x' });
    await service.createReason({ type: ReasonType.LOSS, name: 'Teste' }, 'user-1');
    expect(prismaMock.reason.create).toHaveBeenCalledWith({
      data: { type: ReasonType.LOSS, name: 'Teste', active: true },
    });
    expect(auditServiceMock.log).toHaveBeenCalled();
  });
});
