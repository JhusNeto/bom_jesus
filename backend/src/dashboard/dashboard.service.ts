import { Injectable } from '@nestjs/common';
import { MaturityState, MovementType, Prisma } from '@prisma/client';
import { PrismaService } from '../prisma/prisma.service';
import { ValidationRulesService } from '../validation-rules/validation-rules.service';

interface DashboardFilters {
  from?: string;
  to?: string;
  clientId?: string;
}

@Injectable()
export class DashboardService {
  constructor(
    private readonly prisma: PrismaService,
    private readonly validationRulesService: ValidationRulesService,
  ) {}

  private normalizeRange(filters: DashboardFilters, fallbackDays = 7) {
    const now = new Date();
    const end = filters.to ? new Date(filters.to) : now;
    const start = filters.from
      ? new Date(filters.from)
      : new Date(end.getTime() - (fallbackDays - 1) * 864e5);
    start.setHours(0, 0, 0, 0);
    end.setHours(23, 59, 59, 999);
    return { start, end, now };
  }

  async getKpis(filters: DashboardFilters = {}) {
    const now = new Date();
    const dayStart = new Date(
      now.getFullYear(),
      now.getMonth(),
      now.getDate(),
      0,
      0,
      0,
      0,
    );
    const monthStart = new Date(now.getFullYear(), now.getMonth(), 1);

    const { start, end } = this.normalizeRange(filters, 7);

    const [dayBoxes, stockByMaturity, lossDay, lossMonth, returnsByClient] =
      await Promise.all([
        this.prisma.stockMovement.aggregate({
          _sum: { boxesDelta: true, kgDelta: true },
          where: {
            movementType: MovementType.EXIT,
            happenedAt: { gte: dayStart },
          },
        }),
        this.prisma.lot.groupBy({
          by: ['maturityState'],
          _sum: { boxes: true, kg: true },
        }),
        this.prisma.lossRecord.aggregate({
          _sum: { boxes: true, kg: true },
          where: { happenedAt: { gte: dayStart } },
        }),
        this.prisma.lossRecord.aggregate({
          _sum: { boxes: true, kg: true },
          where: { happenedAt: { gte: monthStart } },
        }),
        this.prisma.$queryRaw<
          Array<{
            clientId: string;
            cliente: string;
            devolucoes7dCaixas: bigint;
            qtdeRegistros: bigint;
          }>
        >(Prisma.sql`
          SELECT
            c.id AS "clientId",
            c.name AS "cliente",
            COALESCE(SUM(r."boxes"), 0)::bigint AS "devolucoes7dCaixas",
            COUNT(*)::bigint AS "qtdeRegistros"
          FROM "ReturnRecord" r
          JOIN "Client" c ON c.id = r."clientId"
          WHERE r."happenedAt" >= ${start}
            AND r."happenedAt" <= ${end}
            ${
              filters.clientId
                ? Prisma.sql`AND r."clientId" = ${filters.clientId}`
                : Prisma.empty
            }
          GROUP BY c.id, c.name
          ORDER BY "devolucoes7dCaixas" DESC
          LIMIT 10
        `),
      ]);

    const stockMap: Record<MaturityState, { boxes: number; kg: number }> = {
      VERDE: { boxes: 0, kg: 0 },
      DE_VEZ: { boxes: 0, kg: 0 },
      MADURA: { boxes: 0, kg: 0 },
    };

    for (const row of stockByMaturity) {
      stockMap[row.maturityState] = {
        boxes: row._sum.boxes ?? 0,
        kg: Number(row._sum.kg?.toString() ?? 0),
      };
    }

    const rules = await this.validationRulesService.getRules();
    const maduraBoxes = stockMap.MADURA.boxes;
    const maturityAlertThreshold = rules.MATURE_STOCK_ALERT_BOXES;

    return {
      caixasDoDia: Math.abs(dayBoxes._sum.boxesDelta ?? 0),
      kgDoDia: Math.abs(Number(dayBoxes._sum.kgDelta?.toString() ?? 0)),
      estoquePorMaturacao: stockMap,
      perdas: {
        hoje: {
          caixas: lossDay._sum.boxes ?? 0,
          kg: Number(lossDay._sum.kg?.toString() ?? 0),
        },
        mes: {
          caixas: lossMonth._sum.boxes ?? 0,
          kg: Number(lossMonth._sum.kg?.toString() ?? 0),
        },
      },
      devolucoesTopClientes: returnsByClient.map((row) => ({
        clientId: row.clientId,
        cliente: row.cliente,
        caixas: Number(row.devolucoes7dCaixas),
        registros: Number(row.qtdeRegistros),
      })),
      alertas: {
        maturacaoRisco:
          maduraBoxes > maturityAlertThreshold
            ? {
                enabled: true,
                thresholdBoxes: maturityAlertThreshold,
                currentBoxes: maduraBoxes,
              }
            : {
                enabled: false,
                thresholdBoxes: maturityAlertThreshold,
                currentBoxes: maduraBoxes,
              },
      },
      atualizadoEm: now.toISOString(),
    };
  }

  async getTrends(days = 7, filters: DashboardFilters = {}) {
    const { start, end } = this.normalizeRange(filters, Math.max(1, days));
    const rows = await this.prisma.$queryRaw<
      Array<{
        date: Date;
        sold: bigint;
        losses: bigint;
        returns: bigint;
      }>
    >(Prisma.sql`
      WITH days AS (
        SELECT generate_series(${start}::date, ${end}::date, interval '1 day')::date AS d
      )
      SELECT
        days.d AS "date",
        COALESCE(v.caixas_vendidas, 0)::bigint AS "sold",
        COALESCE(p.caixas_perdas, 0)::bigint AS "losses",
        COALESCE(dv.caixas_devolucoes, 0)::bigint AS "returns"
      FROM days
      LEFT JOIN (
        SELECT "happenedAt"::date AS d, SUM(-"boxesDelta") AS caixas_vendidas
        FROM "StockMovement"
        WHERE "movementType" = 'EXIT'::"MovementType"
          AND "happenedAt" >= ${start}
          AND "happenedAt" <= ${end}
        GROUP BY 1
      ) v ON v.d = days.d
      LEFT JOIN (
        SELECT "happenedAt"::date AS d, SUM("boxes") AS caixas_perdas
        FROM "LossRecord"
        WHERE "happenedAt" >= ${start}
          AND "happenedAt" <= ${end}
        GROUP BY 1
      ) p ON p.d = days.d
      LEFT JOIN (
        SELECT "happenedAt"::date AS d, SUM("boxes") AS caixas_devolucoes
        FROM "ReturnRecord"
        WHERE "happenedAt" >= ${start}
          AND "happenedAt" <= ${end}
          ${
            filters.clientId
              ? Prisma.sql`AND "clientId" = ${filters.clientId}`
              : Prisma.empty
          }
        GROUP BY 1
      ) dv ON dv.d = days.d
      ORDER BY days.d
    `);

    const series = rows.map((row) => ({
      date: row.date.toISOString().slice(0, 10),
      movements: Number(row.sold),
      losses: Number(row.losses),
      returns: Number(row.returns),
    }));

    return { days: series.length, series };
  }

  async exportKpisCsv() {
    const data = await this.getKpis();
    const lines = [
      'caixas_do_dia,kg_do_dia,perdas_hoje_caixas,perdas_mes_caixas,atualizado_em',
      `${data.caixasDoDia},${data.kgDoDia},${data.perdas.hoje.caixas},${data.perdas.mes.caixas},${data.atualizadoEm}`,
    ];
    return lines.join('\n');
  }

  async exportTrendsCsv(days = 7) {
    const data = await this.getTrends(days);
    const rows = data.series.map(
      (day) => `${day.date},${day.movements},${day.losses},${day.returns}`,
    );
    return ['date,movements,losses,returns', ...rows].join('\n');
  }
}
