import { Injectable, Logger } from '@nestjs/common';
import { Cron } from '@nestjs/schedule';
import { ProcessingStatus } from '@prisma/client';
import { AlertsService } from '../alerts/alerts.service';
import { EventsService } from '../events/events.service';
import { computeMaturityState } from './maturation-rules';
import { PrismaService } from '../prisma/prisma.service';

@Injectable()
export class JobsService {
  private readonly logger = new Logger(JobsService.name);

  constructor(
    private readonly prisma: PrismaService,
    private readonly eventsService: EventsService,
    private readonly alertsService: AlertsService,
  ) {}

  @Cron('* * * * *')
  async processRawEvents() {
    const pendingCount = await this.prisma.rawEventProcessingState.count({
      where: { processingStatus: ProcessingStatus.PENDING },
    });

    if (pendingCount === 0) return;

    this.logger.log(`Eventos RAW pendentes: ${pendingCount}`);
    await this.eventsService.processPending(200);
  }

  @Cron('*/5 * * * *')
  async refreshMaterializedViews() {
    await this.prisma.$executeRawUnsafe(
      'REFRESH MATERIALIZED VIEW clean.estoque_atual',
    );
    await this.prisma.$executeRawUnsafe(
      'REFRESH MATERIALIZED VIEW clean.maturacao_atual',
    );
    await this.prisma.$executeRawUnsafe(
      'REFRESH MATERIALIZED VIEW clean.devolucoes_clientes',
    );
    await this.prisma.$executeRawUnsafe(
      'REFRESH MATERIALIZED VIEW clean.perdas_mensal',
    );
  }

  @Cron('*/10 * * * *')
  async runAlerts() {
    try {
      const { fired, skipped } = await this.alertsService.runAlerts();
      if (fired > 0 || skipped > 0) {
        this.logger.log(`Alertas: ${fired} disparados, ${skipped} em cooldown`);
      }
    } catch (err) {
      this.logger.error(`Erro ao executar alertas: ${err}`);
    }
  }

  @Cron('5 0 * * *')
  async updateMaturation() {
    const lots = await this.prisma.lot.findMany();
    const now = new Date();

    for (const lot of lots) {
      const state = computeMaturityState(lot.entryDate, now);

      await this.prisma.lot.update({
        where: { id: lot.id },
        data: { maturityState: state },
      });

      await this.prisma.maturationDailySnapshot.upsert({
        where: {
          lotId_snapshotDate: {
            lotId: lot.id,
            snapshotDate: new Date(now.getFullYear(), now.getMonth(), now.getDate()),
          },
        },
        update: {
          state,
          boxes: lot.boxes,
          kg: lot.kg,
        },
        create: {
          lotId: lot.id,
          snapshotDate: new Date(now.getFullYear(), now.getMonth(), now.getDate()),
          state,
          boxes: lot.boxes,
          kg: lot.kg,
        },
      });
    }
  }
}
