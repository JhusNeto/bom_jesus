import { Injectable } from '@nestjs/common';
import { Prisma } from '@prisma/client';
import { PrismaService } from '../prisma/prisma.service';

export type ValidationRuleKey =
  | 'QTY_BOXES_MAX'
  | 'QTY_KG_MAX'
  | 'EVENT_FUTURE_MINUTES_MAX'
  | 'EVENT_PAST_DAYS_MAX'
  | 'MATURE_STOCK_ALERT_BOXES';

const DEFAULT_RULES: Record<ValidationRuleKey, number> = {
  QTY_BOXES_MAX: 2000,
  QTY_KG_MAX: 50000,
  EVENT_FUTURE_MINUTES_MAX: 5,
  EVENT_PAST_DAYS_MAX: 7,
  MATURE_STOCK_ALERT_BOXES: 300,
};

@Injectable()
export class ValidationRulesService {
  constructor(private readonly prisma: PrismaService) {}

  async getRules() {
    const stored = await this.prisma.validationRuleConfig.findMany();
    const map = new Map(stored.map((item) => [item.key, item]));

    const rules = Object.entries(DEFAULT_RULES).reduce(
      (acc, [key, fallback]) => {
        const current = map.get(key);
        acc[key as ValidationRuleKey] = current?.valueNumber
          ? Number(current.valueNumber.toString())
          : fallback;
        return acc;
      },
      {} as Record<ValidationRuleKey, number>,
    );

    return rules;
  }

  async setRule(key: ValidationRuleKey, valueNumber: number) {
    return this.prisma.validationRuleConfig.upsert({
      where: { key },
      update: { valueNumber: new Prisma.Decimal(valueNumber) },
      create: { key, valueNumber: new Prisma.Decimal(valueNumber) },
    });
  }
}
