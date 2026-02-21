import { apiRequest } from '../api/client';
import { enqueueEvent, markEventSynced, pauseRetry, updateRetry } from '../storage/db';
import type { PendingEvent } from '../types';
import { createLocalId } from '../utils/id';

export async function queueEvent(
  endpoint: string,
  eventType: PendingEvent['eventType'],
  payload: Record<string, unknown>,
) {
  const extractStatus = (errorMessage: string) => {
    const match = errorMessage.match(/\((\d{3})\)/);
    if (!match) return null;
    return Number(match[1]);
  };

  const localId = createLocalId();
  const event: PendingEvent = {
    localId,
    endpoint,
    eventType,
    payload,
    createdAt: new Date().toISOString(),
    retryCount: 0,
    nextRetryAt: Date.now(),
    synced: false,
  };

  await enqueueEvent(event);
  if (!navigator.onLine) return { queued: true, synced: false, localId };

  try {
    await apiRequest(endpoint, {
      method: 'POST',
      body: JSON.stringify(payload),
    });
    await markEventSynced(localId);
    return { queued: true, synced: true, localId };
  } catch (error) {
    const message = error instanceof Error ? error.message : 'Falha na sincronizacao';
    const status = extractStatus(message);
    const isNonRetryable = status !== null && status >= 400 && status < 500 && status !== 401;
    if (isNonRetryable) {
      await pauseRetry(
        localId,
        1,
        `${message} | Reenvio pausado: revisar evento no historico.`,
      );
    } else {
      await updateRetry(localId, 1, message);
    }
    return { queued: true, synced: false, localId };
  }
}
