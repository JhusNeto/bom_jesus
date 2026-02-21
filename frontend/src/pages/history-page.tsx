import { useEffect, useState } from 'react';
import { PageTitle } from '../components/page-title';
import { listPendingEvents } from '../storage/db';
import type { PendingEvent } from '../types';

export function HistoryPage() {
  const [events, setEvents] = useState<PendingEvent[]>([]);

  useEffect(() => {
    async function load() {
      const pending = await listPendingEvents();
      setEvents(
        [...pending].sort(
          (a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime(),
        ),
      );
    }
    void load();
  }, []);

  return (
    <>
      <PageTitle subtitle="Eventos locais com status de sincronizacao">
        Historico
      </PageTitle>
      <section className="panel">
        {events.length === 0 ? <p>Sem eventos locais.</p> : null}
        {events.map((event) => (
          <article key={event.localId} className="history-item">
            <p>
              <strong>{event.eventType}</strong> - {event.createdAt}
            </p>
            <p>Status: {event.synced ? 'sincronizado' : 'pendente'}</p>
            {event.lastError ? <p>Erro: {event.lastError}</p> : null}
          </article>
        ))}
      </section>
    </>
  );
}
