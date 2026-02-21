import { apiRequest } from './client';

export interface AlertRule {
  id: string;
  ruleKey: string;
  name: string;
  description: string | null;
  thresholdConfig: Record<string, number>;
  cooldownMinutes: number;
  severity: string;
  channels: string[];
  active: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface AlertEvent {
  id: string;
  ruleId: string;
  payload: Record<string, unknown>;
  severity: string;
  channel: string;
  status: string;
  recipientEmail: string | null;
  recipientUserId: string | null;
  errorMessage: string | null;
  sentAt: string | null;
  createdAt: string;
  rule?: { ruleKey: string; name: string };
}

export async function listAlertRules(): Promise<AlertRule[]> {
  return apiRequest<AlertRule[]>('/alerts/rules');
}

export async function updateAlertRule(
  id: string,
  data: { active?: boolean; cooldownMinutes?: number; severity?: string; channels?: string[] },
): Promise<AlertRule> {
  return apiRequest<AlertRule>(`/alerts/rules/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  });
}

export async function listAlertEvents(): Promise<AlertEvent[]> {
  return apiRequest<AlertEvent[]>('/alerts/events');
}

export async function getVapidPublicKey(): Promise<{ publicKey: string | null }> {
  return apiRequest<{ publicKey: string | null }>('/alerts/vapid-public-key');
}

export async function savePushSubscription(
  subscription: PushSubscriptionJSON | { endpoint: string; keys?: { p256dh: string; auth: string } },
): Promise<unknown> {
  const payload =
    'keys' in subscription && subscription.keys
      ? {
          endpoint: subscription.endpoint,
          keys: {
            p256dh: subscription.keys.p256dh,
            auth: subscription.keys.auth,
          },
        }
      : { endpoint: subscription.endpoint, ...subscription };
  return apiRequest('/alerts/push-subscription', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}
