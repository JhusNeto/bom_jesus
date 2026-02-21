import { openDB } from 'idb';
import type { PendingEvent } from '../types';

const DB_NAME = 'bom-jesus-ops-db';
const DB_VERSION = 1;

export async function getDb() {
  return openDB(DB_NAME, DB_VERSION, {
    upgrade(db) {
      const eventsStore = db.createObjectStore('events', { keyPath: 'localId' });
      eventsStore.createIndex('by-synced', 'synced');
      eventsStore.createIndex('by-next-retry', 'nextRetryAt');
    },
  });
}

export async function enqueueEvent(event: PendingEvent) {
  const db = await getDb();
  await db.put('events', event);
}

export async function listPendingEvents() {
  const db = await getDb();
  const allEvents = (await db.getAll('events')) as PendingEvent[];
  return allEvents.filter((event) => !event.synced);
}

export async function markEventSynced(localId: string) {
  const db = await getDb();
  const event = (await db.get('events', localId)) as PendingEvent | undefined;
  if (!event) return;
  await db.put('events', { ...event, synced: true, lastError: undefined });
}

export async function updateRetry(localId: string, retryCount: number, error: string) {
  const db = await getDb();
  const event = (await db.get('events', localId)) as PendingEvent | undefined;
  if (!event) return;
  const delayMs = Math.min(2 ** retryCount * 1000, 60000);
  await db.put('events', {
    ...event,
    retryCount,
    lastError: error,
    nextRetryAt: Date.now() + delayMs,
  });
}

export async function pauseRetry(localId: string, retryCount: number, error: string) {
  const db = await getDb();
  const event = (await db.get('events', localId)) as PendingEvent | undefined;
  if (!event) return;
  await db.put('events', {
    ...event,
    retryCount,
    lastError: error,
    // 2099 = estacionamento operacional para erro nao retentavel.
    nextRetryAt: new Date('2099-01-01T00:00:00.000Z').getTime(),
  });
}
