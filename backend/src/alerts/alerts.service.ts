import { Injectable, Logger, OnModuleInit } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import {
  AlertChannel,
  AlertDeliveryStatus,
  AlertRule,
  AlertSeverity,
  MaturityState,
  ProcessingStatus,
} from '@prisma/client';
import { Prisma } from '@prisma/client';
import * as nodemailer from 'nodemailer';
import * as webPush from 'web-push';
import { PrismaService } from '../prisma/prisma.service';

type ThresholdConfig = Record<string, number>;

interface AlertPayload {
  ruleKey: string;
  message: string;
  data?: Record<string, unknown>;
}

const DEFAULT_RULES: Array<{
  ruleKey: string;
  name: string;
  description: string;
  thresholdConfig: ThresholdConfig;
  cooldownMinutes: number;
  severity: AlertSeverity;
  channels: string[];
}> = [
  {
    ruleKey: 'estoque_madura',
    name: 'Estoque maduro em risco',
    description:
      'Caixas maduras acima do limite (20 amarelo, 50 vermelho) por produto',
    thresholdConfig: { warningBoxes: 20, criticalBoxes: 50 },
    cooldownMinutes: 120,
    severity: AlertSeverity.WARNING,
    channels: ['PUSH', 'EMAIL'],
  },
  {
    ruleKey: 'perdas_dia',
    name: 'Perdas acima da média',
    description: 'Perdas do dia > média 7d + 2σ',
    thresholdConfig: { sigmaMultiplier: 2, lookbackDays: 7 },
    cooldownMinutes: 120,
    severity: AlertSeverity.WARNING,
    channels: ['PUSH', 'EMAIL'],
  },
  {
    ruleKey: 'devolucoes_cliente_7d',
    name: 'Devoluções cliente elevadas',
    description: 'Devoluções 7d de cliente > 1,5× média 4 semanas',
    thresholdConfig: { multiplier: 1.5, weeksBaseline: 4 },
    cooldownMinutes: 120,
    severity: AlertSeverity.WARNING,
    channels: ['PUSH', 'EMAIL'],
  },
  {
    ruleKey: 'raw_pending_backlog',
    name: 'Backlog RAW pendente',
    description: 'RAW pendentes > 50 ou > 30 min sem processar',
    thresholdConfig: { maxPending: 50, maxMinutesStale: 30 },
    cooldownMinutes: 60,
    severity: AlertSeverity.CRITICAL,
    channels: ['PUSH', 'EMAIL'],
  },
];

@Injectable()
export class AlertsService implements OnModuleInit {
  private readonly logger = new Logger(AlertsService.name);
  private transporter: nodemailer.Transporter | null = null;
  private vapidConfigured = false;

  constructor(
    private readonly prisma: PrismaService,
    private readonly configService: ConfigService,
  ) {}

  async onModuleInit() {
    await this.ensureDefaultRules();
    this.initEmail();
    this.initWebPush();
  }

  private async ensureDefaultRules() {
    for (const rule of DEFAULT_RULES) {
      await this.prisma.alertRule.upsert({
        where: { ruleKey: rule.ruleKey },
        update: {
          name: rule.name,
          description: rule.description,
          thresholdConfig: rule.thresholdConfig as unknown as Prisma.JsonObject,
          cooldownMinutes: rule.cooldownMinutes,
          severity: rule.severity,
          channels: rule.channels,
        },
        create: {
          ruleKey: rule.ruleKey,
          name: rule.name,
          description: rule.description,
          thresholdConfig: rule.thresholdConfig as unknown as Prisma.JsonObject,
          cooldownMinutes: rule.cooldownMinutes,
          severity: rule.severity,
          channels: rule.channels,
          active: true,
        },
      });
    }
  }

  private initEmail() {
    const host = this.configService.get<string>('SMTP_HOST');
    const port = this.configService.get<number>('SMTP_PORT');
    const user = this.configService.get<string>('SMTP_USER');
    const pass = this.configService.get<string>('SMTP_PASS');

    if (host && user && pass) {
      this.transporter = nodemailer.createTransport({
        host: host || 'localhost',
        port: port || 587,
        secure: port === 465,
        auth: { user, pass },
      });
      this.logger.log('SMTP configurado para envio de alertas.');
    } else {
      this.logger.warn(
        'SMTP não configurado (SMTP_HOST, SMTP_USER, SMTP_PASS). Alertas por e-mail desabilitados.',
      );
    }
  }

  private initWebPush() {
    const publicKey = this.configService.get<string>('VAPID_PUBLIC_KEY');
    const privateKey = this.configService.get<string>('VAPID_PRIVATE_KEY');

    if (publicKey && privateKey) {
      webPush.setVapidDetails(
        'mailto:' + (this.configService.get<string>('ALERT_FROM_EMAIL') || 'admin@bomjesus.local'),
        publicKey,
        privateKey,
      );
      this.vapidConfigured = true;
      this.logger.log('Web Push (VAPID) configurado.');
    } else {
      this.logger.warn(
        'Web Push não configurado (VAPID_PUBLIC_KEY, VAPID_PRIVATE_KEY). Push desabilitado.',
      );
    }
  }

  async getRules() {
    return this.prisma.alertRule.findMany({
      orderBy: { ruleKey: 'asc' },
    });
  }

  async updateRule(id: string, data: { active?: boolean; cooldownMinutes?: number; severity?: AlertSeverity; channels?: string[] }) {
    return this.prisma.alertRule.update({
      where: { id },
      data,
    });
  }

  async savePushSubscription(userId: string, dto: { endpoint: string; p256dh?: string; auth?: string; keys?: { p256dh: string; auth: string } }) {
    const p256dh = dto.p256dh ?? dto.keys?.p256dh;
    const auth = dto.auth ?? dto.keys?.auth;
    if (!p256dh || !auth) {
      throw new Error('p256dh e auth são obrigatórios para a subscription.');
    }

    return this.prisma.pushSubscription.upsert({
      where: { userId },
      update: { endpoint: dto.endpoint, p256dh, auth },
      create: { userId, endpoint: dto.endpoint, p256dh, auth },
    });
  }

  async getRecentEvents(ruleId?: string, limit = 50) {
    return this.prisma.alertEvent.findMany({
      where: ruleId ? { ruleId } : undefined,
      orderBy: { createdAt: 'desc' },
      take: limit,
      include: { rule: { select: { ruleKey: true, name: true } } },
    });
  }

  private async isInCooldown(rule: AlertRule): Promise<boolean> {
    const lastSent = await this.prisma.alertEvent.findFirst({
      where: { ruleId: rule.id, status: AlertDeliveryStatus.SENT },
      orderBy: { sentAt: 'desc' },
      select: { sentAt: true },
    });
    if (!lastSent?.sentAt) return false;
    const cooldownMs = rule.cooldownMinutes * 60 * 1000;
    return Date.now() - lastSent.sentAt.getTime() < cooldownMs;
  }

  private async queryEstoqueMadura(): Promise<AlertPayload | null> {
    type Row = { product_id: string; product_name: string; boxes: number };
    const rows = await this.prisma.$queryRaw<Row[]>(Prisma.sql`
      SELECT l."productId" AS product_id, p.name AS product_name,
             SUM(l."boxes")::int AS boxes
      FROM "Lot" l
      JOIN "Product" p ON p.id = l."productId"
      WHERE l."maturityState" = 'MADURA'::"MaturityState"
      GROUP BY l."productId", p.name
      HAVING SUM(l."boxes") > 20
    `);

    let severity: AlertSeverity = AlertSeverity.WARNING;
    const critical: Array<{ name: string; boxes: number }> = [];
    const warning: Array<{ name: string; boxes: number }> = [];

    for (const r of rows) {
      const boxes = Number(r.boxes);
      if (boxes >= 50) {
        critical.push({ name: r.product_name, boxes });
        severity = AlertSeverity.CRITICAL;
      } else if (boxes > 20) {
        warning.push({ name: r.product_name, boxes });
      }
    }

    if (critical.length > 0 || warning.length > 0) {
      return {
        ruleKey: 'estoque_madura',
        message:
          severity === AlertSeverity.CRITICAL
            ? `Estoque maduro CRÍTICO: ${critical.map((c) => `${c.name} (${c.boxes} caixas)`).join(', ')}`
            : `Estoque maduro em risco: ${[...critical, ...warning]
                .map((x) => `${x.name} (${x.boxes})`)
                .join(', ')}`,
        data: { critical, warning },
      };
    }
    return null;
  }

  private async queryPerdasDia(): Promise<AlertPayload | null> {
    const dayStart = new Date();
    dayStart.setHours(0, 0, 0, 0);
    const sevenDaysAgo = new Date(dayStart);
    sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);

    const dailyTotals = await this.prisma.$queryRaw<Array<{ d: Date; caixas: bigint }>>(
      Prisma.sql`
      SELECT "happenedAt"::date AS d, SUM("boxes")::bigint AS caixas
      FROM "LossRecord"
      WHERE "happenedAt" >= ${sevenDaysAgo} AND "happenedAt" < ${dayStart}
      GROUP BY 1
    `,
    );

    const values = dailyTotals.map((r) => Number(r.caixas));
    const mean = values.length ? values.reduce((a, b) => a + b, 0) / values.length : 0;
    const variance =
      values.length > 1
        ? values.reduce((acc, v) => acc + (v - mean) ** 2, 0) / (values.length - 1)
        : 0;
    const sigma = Math.sqrt(variance);

    const today = await this.prisma.lossRecord.aggregate({
      _sum: { boxes: true },
      where: { happenedAt: { gte: dayStart } },
    });
    const hoje = today._sum.boxes ?? 0;
    const threshold = mean + 2 * sigma;

    if (values.length >= 3 && hoje > threshold && threshold > 0) {
      return {
        ruleKey: 'perdas_dia',
        message: `Perdas hoje (${hoje} caixas) acima da média 7d + 2σ (${Math.round(threshold)}).`,
        data: { hoje, mean, sigma, threshold },
      };
    }
    return null;
  }

  private async queryDevolucoesCliente(): Promise<AlertPayload | null> {
    const now = new Date();
    const sevenDaysAgo = new Date(now);
    sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);
    const fourWeeksAgo = new Date(now);
    fourWeeksAgo.setDate(fourWeeksAgo.getDate() - 28);

    const [clientes7d, media4semanas] = await Promise.all([
      this.prisma.$queryRaw<
        Array<{ client_id: string; cliente: string; caixas: bigint }>
      >(
        Prisma.sql`
        SELECT r."clientId" AS client_id, c.name AS cliente,
               SUM(r."boxes")::bigint AS caixas
        FROM "ReturnRecord" r
        JOIN "Client" c ON c.id = r."clientId"
        WHERE r."happenedAt" >= ${sevenDaysAgo}
        GROUP BY r."clientId", c.name
      `,
      ),
      this.prisma.$queryRaw<
        Array<{ client_id: string; media_caixas: number }>
      >(
        Prisma.sql`
        WITH base AS (
          SELECT r."clientId", SUM(r."boxes")::numeric AS total
          FROM "ReturnRecord" r
          WHERE r."happenedAt" >= ${fourWeeksAgo} AND r."happenedAt" < ${sevenDaysAgo}
          GROUP BY r."clientId"
        )
        SELECT "clientId" AS client_id,
               (total / 4)::numeric AS media_caixas
        FROM base
      `,
      ),
    ]);

    const mediaMap = new Map(media4semanas.map((m) => [m.client_id, Number(m.media_caixas)]));
    const above: Array<{ cliente: string; caixas: number; media: number }> = [];

    for (const c of clientes7d) {
      const caixas = Number(c.caixas);
      const media = mediaMap.get(c.client_id) ?? 0;
      if (media > 0 && caixas > media * 1.5) {
        above.push({ cliente: c.cliente, caixas, media });
      }
    }

    if (above.length > 0) {
      const top = above[0];
      return {
        ruleKey: 'devolucoes_cliente_7d',
        message: `Devoluções 7d elevadas: ${top.cliente} (${top.caixas} caixas, média 4 sem: ${Math.round(top.media)})`,
        data: { acima: above },
      };
    }
    return null;
  }

  private async queryRawBacklog(): Promise<AlertPayload | null> {
    const [pendingCount, oldestPending] = await Promise.all([
      this.prisma.rawEventProcessingState.count({
        where: { processingStatus: ProcessingStatus.PENDING },
      }),
      this.prisma.rawEventProcessingState.findFirst({
        where: { processingStatus: ProcessingStatus.PENDING },
        orderBy: { ingestedAt: 'asc' },
        select: { ingestedAt: true },
      }),
    ]);

    const thresholdCount = 50;
    const thresholdMinutes = 30;
    const now = new Date();
    const minutesStale = oldestPending?.ingestedAt
      ? (now.getTime() - oldestPending.ingestedAt.getTime()) / (60 * 1000)
      : 0;

    const countTrigger = pendingCount > thresholdCount;
    const timeTrigger = pendingCount > 0 && minutesStale > thresholdMinutes;

    if (countTrigger || timeTrigger) {
      return {
        ruleKey: 'raw_pending_backlog',
        message:
          countTrigger
            ? `Backlog RAW: ${pendingCount} eventos pendentes (limite: ${thresholdCount})`
            : `Backlog RAW: ${pendingCount} eventos há mais de ${thresholdMinutes} min sem processar`,
        data: { pendingCount, minutesStale },
      };
    }
    return null;
  }

  private async evaluateRule(rule: AlertRule): Promise<AlertPayload | null> {
    switch (rule.ruleKey) {
      case 'estoque_madura':
        return this.queryEstoqueMadura();
      case 'perdas_dia':
        return this.queryPerdasDia();
      case 'devolucoes_cliente_7d':
        return this.queryDevolucoesCliente();
      case 'raw_pending_backlog':
        return this.queryRawBacklog();
      default:
        return null;
    }
  }

  private async getAlertRecipients(): Promise<Array<{ email: string; userId?: string }>> {
    const users = await this.prisma.user.findMany({
      where: { role: { in: ['MANAGER', 'ADMIN'] } },
      select: { id: true, email: true },
    });
    return users.map((u) => ({ email: u.email, userId: u.id }));
  }

  private async sendEmail(to: string, subject: string, text: string): Promise<boolean> {
    if (!this.transporter) return false;
    const from = this.configService.get<string>('ALERT_FROM_EMAIL') || 'alerts@bomjesus.local';
    try {
      await this.transporter.sendMail({
        from,
        to,
        subject: `[Bom Jesus] ${subject}`,
        text,
      });
      return true;
    } catch (err) {
      this.logger.error(`Falha envio e-mail para ${to}: ${err}`);
      return false;
    }
  }

  private async sendPush(userId: string, payload: AlertPayload): Promise<boolean> {
    if (!this.vapidConfigured) return false;
    const sub = await this.prisma.pushSubscription.findUnique({
      where: { userId },
    });
    if (!sub) return false;
    try {
      await webPush.sendNotification(
        {
          endpoint: sub.endpoint,
          keys: { p256dh: sub.p256dh, auth: sub.auth },
        },
        JSON.stringify({
          title: payload.ruleKey,
          body: payload.message,
          data: payload.data,
        }),
        { TTL: 3600 },
      );
      return true;
    } catch (err) {
      this.logger.warn(`Push falhou para user ${userId}: ${err}`);
      return false;
    }
  }

  private channelToEnum(ch: string): AlertChannel {
    return ch === 'EMAIL' ? AlertChannel.EMAIL : AlertChannel.PUSH;
  }

  private async createAndDeliver(
    rule: AlertRule,
    payload: AlertPayload,
    recipients: Array<{ email: string; userId?: string }>,
  ) {
    const channels = (rule.channels || []).filter((c) =>
      ['PUSH', 'EMAIL'].includes(c.toUpperCase()),
    );
    const severity = rule.severity;

    for (const ch of channels) {
      const channel = this.channelToEnum(ch);

      if (channel === AlertChannel.EMAIL) {
        for (const r of recipients) {
          const event = await this.prisma.alertEvent.create({
            data: {
              ruleId: rule.id,
              payload: payload as unknown as Prisma.JsonObject,
              severity,
              channel: AlertChannel.EMAIL,
              status: AlertDeliveryStatus.PENDING,
              recipientEmail: r.email,
              recipientUserId: r.userId ?? undefined,
            },
          });
          const ok = await this.sendEmail(r.email, payload.ruleKey, payload.message);
          await this.prisma.alertEvent.update({
            where: { id: event.id },
            data: {
              status: ok ? AlertDeliveryStatus.SENT : AlertDeliveryStatus.FAILED,
              sentAt: ok ? new Date() : undefined,
              errorMessage: ok ? undefined : 'SMTP não configurado ou falha',
            },
          });
        }
      }

      if (channel === AlertChannel.PUSH) {
        for (const r of recipients) {
          if (!r.userId) continue;
          const event = await this.prisma.alertEvent.create({
            data: {
              ruleId: rule.id,
              payload: payload as unknown as Prisma.JsonObject,
              severity,
              channel: AlertChannel.PUSH,
              status: AlertDeliveryStatus.PENDING,
              recipientUserId: r.userId,
            },
          });
          const ok = await this.sendPush(r.userId, payload);
          await this.prisma.alertEvent.update({
            where: { id: event.id },
            data: {
              status: ok ? AlertDeliveryStatus.SENT : AlertDeliveryStatus.FAILED,
              sentAt: ok ? new Date() : undefined,
              errorMessage: ok ? undefined : 'Push não configurado ou subscription ausente',
            },
          });
        }
      }
    }
  }

  async runAlerts(): Promise<{ fired: number; skipped: number }> {
    const rules = await this.prisma.alertRule.findMany({
      where: { active: true },
    });

    let fired = 0;
    let skipped = 0;

    for (const rule of rules) {
      if (await this.isInCooldown(rule)) {
        skipped++;
        continue;
      }

      const payload = await this.evaluateRule(rule);
      if (!payload) continue;

      const recipients = await this.getAlertRecipients();
      if (recipients.length === 0) {
        this.logger.warn(`Nenhum destinatário para alerta ${rule.ruleKey}`);
        continue;
      }

      await this.createAndDeliver(rule, payload, recipients);
      fired++;
      this.logger.log(`Alerta ${rule.ruleKey} disparado: ${payload.message}`);
    }

    return { fired, skipped };
  }

  getVapidPublicKey(): string | null {
    return this.configService.get<string>('VAPID_PUBLIC_KEY') ?? null;
  }
}
