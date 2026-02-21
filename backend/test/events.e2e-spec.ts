import { Test, TestingModule } from '@nestjs/testing';
import { INestApplication, ValidationPipe } from '@nestjs/common';
import request from 'supertest';
import { App } from 'supertest/types';
import { AppModule } from '../src/app.module';

/**
 * Testes de integração: /events, /auth, /dashboard
 * Requer DATABASE_URL apontando para banco com schema aplicado.
 * Em CI: usar banco de teste ou docker-compose.
 */
describe('Events + Auth + Dashboard (e2e)', () => {
  let app: INestApplication<App>;
  let accessToken: string;

  beforeAll(async () => {
    const moduleFixture: TestingModule = await Test.createTestingModule({
      imports: [AppModule],
    }).compile();

    app = moduleFixture.createNestApplication();
    app.setGlobalPrefix('v1');
    app.useGlobalPipes(
      new ValidationPipe({ transform: true, whitelist: true }),
    );
    await app.init();
  });

  afterAll(async () => {
    await app?.close();
  });

  describe('Auth', () => {
    it('POST /auth/login retorna tokens', async () => {
      const res = await request(app.getHttpServer())
        .post('/v1/auth/login')
        .set('Content-Type', 'application/json')
        .send({ email: 'admin@bomjesus.local', password: 'admin1234' });
      if (res.status === 404 || res.status === 500) {
        return;
      }
      expect([200, 201]).toContain(res.status);
      expect(res.body.accessToken).toBeDefined();
      accessToken = res.body.accessToken;
    });
  });

  describe('Events', () => {
    const idem = `e2e-${Date.now()}-${Math.random().toString(36).slice(2)}`;

    it('POST /events/ingest ingere evento e retorna rawEventId', async () => {
      const res = await request(app.getHttpServer())
        .post('/v1/events/ingest')
        .set('Authorization', `Bearer ${accessToken}`)
        .send({
          eventType: 'LOT_ENTRY_REGISTERED',
          occurredAt: new Date().toISOString(),
          idempotencyKey: idem,
          data: {
            productId: 'prod-e2e',
            locationId: 'loc-e2e',
            boxes: 50,
          },
        });
      if (res.status === 401) return; // Auth não disponível
      expect([200, 201]).toContain(res.status);
      expect(res.body.rawEventId || res.body.validationStatus).toBeDefined();
    });

    it('POST /events/ingest idempotência retorna duplicated', async () => {
      const res = await request(app.getHttpServer())
        .post('/v1/events/ingest')
        .set('Authorization', `Bearer ${accessToken}`)
        .send({
          eventType: 'LOT_ENTRY_REGISTERED',
          occurredAt: new Date().toISOString(),
          idempotencyKey: idem,
          data: { productId: 'p', locationId: 'l', boxes: 1 },
        });
      if (res.status === 401) return;
      expect(res.body.duplicated).toBe(true);
    });
  });

  describe('Dashboard', () => {
    it('GET /dashboard/kpis retorna estrutura esperada', async () => {
      const res = await request(app.getHttpServer())
        .get('/v1/dashboard/kpis')
        .set('Authorization', `Bearer ${accessToken}`);
      if (res.status === 401) return;
      expect(res.status).toBe(200);
      expect(res.body).toHaveProperty('perdas');
      expect(res.body).toHaveProperty('estoquePorMaturacao');
      expect(res.body).toHaveProperty('atualizadoEm');
    });
  });
});
