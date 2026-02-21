export type EventType =
  | 'LOT_ENTRY_REGISTERED'
  | 'LOT_MOVED'
  | 'LOSS_REGISTERED'
  | 'RETURN_REGISTERED';

export interface PendingEvent {
  localId: string;
  eventType: EventType;
  endpoint: string;
  payload: Record<string, unknown>;
  createdAt: string;
  retryCount: number;
  nextRetryAt: number;
  synced: boolean;
  lastError?: string;
}

export interface AuthUser {
  id: string;
  name: string;
  email: string;
  role: 'OPERATOR' | 'ADMINISTRATIVE' | 'MANAGER' | 'ADMIN';
}
