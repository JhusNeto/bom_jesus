import { useEffect } from 'react';
import { apiRequest } from '../api/client';
import {
  listPendingEvents,
  markEventSynced,
  pauseRetry,
  updateRetry,
} from '../storage/db';

function extractStatus(errorMessage: string) {
  const match = errorMessage.match(/\((\d{3})\)/);
  if (!match) return null;
  return Number(match[1]);
}

async function runSync() {
  if (!navigator.onLine) return;
  const pending = await listPendingEvents();

  for (const item of pending) {
    if (item.nextRetryAt > Date.now()) continue;
    try {
      await apiRequest(item.endpoint, {
        method: 'POST',
        body: JSON.stringify(item.payload),
      });
      await markEventSynced(item.localId);
    } catch (error) {
      const message =
        error instanceof Error ? error.message : 'Falha desconhecida';
      const status = extractStatus(message);
      const isNonRetryable = status !== null && status >= 400 && status < 500 && status !== 401;
      if (isNonRetryable) {
        await pauseRetry(
          item.localId,
          item.retryCount + 1,
          `${message} | Reenvio pausado: revisar evento no historico.`,
        );
      } else {
        await updateRetry(item.localId, item.retryCount + 1, message);
      }
    }
  }
}

export function useSyncQueue() {
  useEffect(() => {
    const interval = window.setInterval(() => {
      void runSync();
    }, 5000);

    const onOnline = () => {
      void runSync();
    };
    window.addEventListener('online', onOnline);
    void runSync();

    return () => {
      clearInterval(interval);
      window.removeEventListener('online', onOnline);
    };
  }, []);
}
