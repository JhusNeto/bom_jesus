import { Injectable } from '@nestjs/common';
import { PrismaService } from '../prisma/prisma.service';

@Injectable()
export class ReviewsService {
  constructor(private readonly prisma: PrismaService) {}

  async listValidationIssues(params: {
    resolved?: boolean;
    severity?: string;
    issueCode?: string;
    page: number;
    pageSize: number;
  }) {
    const where = {
      ...(params.resolved === undefined ? {} : { resolved: params.resolved }),
      ...(params.severity ? { severity: params.severity } : {}),
      ...(params.issueCode ? { issueCode: params.issueCode } : {}),
    };

    const [items, total] = await Promise.all([
      this.prisma.validationIssue.findMany({
        where,
        include: {
          rawEvent: true,
          actions: {
            include: { actorUser: { select: { id: true, name: true, email: true } } },
            orderBy: { createdAt: 'desc' },
          },
        },
        orderBy: { createdAt: 'desc' },
        skip: (params.page - 1) * params.pageSize,
        take: params.pageSize,
      }),
      this.prisma.validationIssue.count({ where }),
    ]);

    return {
      items,
      page: params.page,
      pageSize: params.pageSize,
      total,
      totalPages: Math.max(1, Math.ceil(total / params.pageSize)),
    };
  }

  async resolveValidationIssue(params: {
    id: string;
    actorUserId: string;
    notes?: string;
  }) {
    return this.prisma.$transaction(async (tx) => {
      const issue = await tx.validationIssue.update({
        where: { id: params.id },
        data: { resolved: true },
      });

      await tx.reviewAction.create({
        data: {
          validationIssueId: params.id,
          action: 'RESOLVED',
          notes: params.notes,
          actorUserId: params.actorUserId,
        },
      });

      return issue;
    });
  }
}
