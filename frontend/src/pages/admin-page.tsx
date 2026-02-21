import type { FormEvent } from 'react';
import { useEffect, useState } from 'react';
import { apiRequest, apiTextRequest } from '../api/client';
import {
  listAlertRules,
  listAlertEvents,
  updateAlertRule,
  type AlertRule,
} from '../api/alerts';
import {
  listClients,
  listLocations,
  listProducts,
  listReasons,
  listStores,
} from '../api/catalog';
import { PageTitle } from '../components/page-title';

export function AdminPage() {
  const [products, setProducts] = useState<Array<{ id: string; name: string }>>([]);
  const [locations, setLocations] = useState<Array<{ id: string; name: string }>>([]);
  const [clients, setClients] = useState<Array<{ id: string; name: string }>>([]);
  const [stores, setStores] = useState<Array<{ id: string; name: string }>>([]);
  const [reasons, setReasons] = useState<Array<{ id: string; type: string; name: string }>>(
    [],
  );
  const [status, setStatus] = useState('');
  const [issues, setIssues] = useState<
    Array<{
      id: string;
      issueCode: string;
      severity: string;
      details?: string;
      resolved: boolean;
      createdAt: string;
    }>
  >([]);
  const [issuesPage, setIssuesPage] = useState(1);
  const [issuesTotalPages, setIssuesTotalPages] = useState(1);
  const [issuesSeverityFilter, setIssuesSeverityFilter] = useState('');
  const [issuesCodeFilter, setIssuesCodeFilter] = useState('');
  const [pipelineStatusFilter, setPipelineStatusFilter] = useState<
    '' | 'PENDING' | 'PROCESSED' | 'FAILED'
  >('PENDING');
  const [pipelineEventTypeFilter, setPipelineEventTypeFilter] = useState('');
  const [pipelineIdempotencyFilter, setPipelineIdempotencyFilter] = useState('');
  const [pipelineFromFilter, setPipelineFromFilter] = useState('');
  const [pipelineToFilter, setPipelineToFilter] = useState('');
  const [alertRules, setAlertRules] = useState<AlertRule[]>([]);
  const [alertEvents, setAlertEvents] = useState<
    Array<{
      id: string;
      ruleId: string;
      payload: Record<string, unknown>;
      severity: string;
      channel: string;
      status: string;
      recipientEmail: string | null;
      sentAt: string | null;
      createdAt: string;
      rule?: { ruleKey: string; name: string };
    }>
  >([]);
  const [pipelineEvents, setPipelineEvents] = useState<
    Array<{
      id: string;
      eventType: string;
      idempotencyKey: string;
      processingState?: {
        validationStatus: string;
        processingStatus: string;
        ingestedAt: string;
        processedAt?: string | null;
        lastError?: string | null;
      } | null;
    }>
  >([]);
  const [pipelineMetrics, setPipelineMetrics] = useState<{
    processing: { pending: number; processed: number; failed: number };
    validation: { valid: number; needsReview: number };
    generatedAt: string;
  } | null>(null);

  const [newProduct, setNewProduct] = useState('');
  const [newLocation, setNewLocation] = useState('');
  const [newLocationType, setNewLocationType] = useState('CAMARA');
  const [newClient, setNewClient] = useState('');
  const [newStoreClientId, setNewStoreClientId] = useState('');
  const [newStore, setNewStore] = useState('');
  const [newReasonType, setNewReasonType] = useState<'LOSS' | 'RETURN'>('LOSS');
  const [newReason, setNewReason] = useState('');

  function buildPipelineQuery(limit: number) {
    const params = new URLSearchParams();
    params.set('limit', String(limit));
    if (pipelineStatusFilter) params.set('status', pipelineStatusFilter);
    if (pipelineEventTypeFilter) params.set('eventType', pipelineEventTypeFilter);
    if (pipelineIdempotencyFilter) {
      params.set('idempotencyKey', pipelineIdempotencyFilter);
    }
    if (pipelineFromFilter) params.set('from', pipelineFromFilter);
    if (pipelineToFilter) params.set('to', pipelineToFilter);
    return params.toString();
  }

  async function refresh() {
    const [productsData, locationsData, clientsData, storesData, lossReasons, returnReasons] =
      await Promise.all([
        listProducts(),
        listLocations(),
        listClients(),
        listStores(),
        listReasons('LOSS'),
        listReasons('RETURN'),
      ]);
    const issuesData = await apiRequest<{
      items: Array<{
        id: string;
        issueCode: string;
        severity: string;
        details?: string;
        resolved: boolean;
        createdAt: string;
      }>;
      page: number;
      totalPages: number;
    }>(
      `/reviews/validation-issues?resolved=false&page=${issuesPage}&pageSize=10&severity=${encodeURIComponent(
        issuesSeverityFilter,
      )}&issueCode=${encodeURIComponent(issuesCodeFilter)}`,
    );
    const [metricsData, eventsData, rulesData, alertEventsData] = await Promise.all([
      apiRequest<{
        processing: { pending: number; processed: number; failed: number };
        validation: { valid: number; needsReview: number };
        generatedAt: string;
      }>('/events/metrics'),
      apiRequest<
        Array<{
          id: string;
          eventType: string;
          idempotencyKey: string;
          processingState?: {
            validationStatus: string;
            processingStatus: string;
            ingestedAt: string;
            processedAt?: string | null;
            lastError?: string | null;
          } | null;
        }>
      >(`/events/raw?${buildPipelineQuery(30)}`),
      listAlertRules().catch(() => [] as AlertRule[]),
      listAlertEvents().catch(() => []),
    ]);
    setProducts(productsData);
    setLocations(locationsData);
    setClients(clientsData);
    setStores(storesData);
    setReasons([...lossReasons, ...returnReasons]);
    setIssues(issuesData.items);
    setIssuesPage(issuesData.page);
    setIssuesTotalPages(issuesData.totalPages);
    setPipelineMetrics(metricsData);
    setPipelineEvents(eventsData);
    setAlertRules(rulesData);
    setAlertEvents(alertEventsData);
    if (!newStoreClientId && clientsData[0]) setNewStoreClientId(clientsData[0].id);
  }

  useEffect(() => {
    void refresh();
  }, [
    issuesPage,
    issuesSeverityFilter,
    issuesCodeFilter,
    pipelineStatusFilter,
    pipelineEventTypeFilter,
    pipelineIdempotencyFilter,
    pipelineFromFilter,
    pipelineToFilter,
  ]);

  async function submitProduct(event: FormEvent) {
    event.preventDefault();
    if (!newProduct) return;
    await apiRequest('/catalog/products', {
      method: 'POST',
      body: JSON.stringify({ name: newProduct }),
    });
    setNewProduct('');
    setStatus('Produto criado.');
    await refresh();
  }

  async function submitLocation(event: FormEvent) {
    event.preventDefault();
    if (!newLocation) return;
    await apiRequest('/catalog/locations', {
      method: 'POST',
      body: JSON.stringify({ name: newLocation, type: newLocationType }),
    });
    setNewLocation('');
    setStatus('Localizacao criada.');
    await refresh();
  }

  async function submitClient(event: FormEvent) {
    event.preventDefault();
    if (!newClient) return;
    await apiRequest('/catalog/clients', {
      method: 'POST',
      body: JSON.stringify({ name: newClient }),
    });
    setNewClient('');
    setStatus('Cliente criado.');
    await refresh();
  }

  async function submitStore(event: FormEvent) {
    event.preventDefault();
    if (!newStoreClientId || !newStore) return;
    await apiRequest('/catalog/stores', {
      method: 'POST',
      body: JSON.stringify({ clientId: newStoreClientId, name: newStore }),
    });
    setNewStore('');
    setStatus('Loja criada.');
    await refresh();
  }

  async function submitReason(event: FormEvent) {
    event.preventDefault();
    if (!newReason) return;
    await apiRequest('/catalog/reasons', {
      method: 'POST',
      body: JSON.stringify({ type: newReasonType, name: newReason }),
    });
    setNewReason('');
    setStatus('Motivo criado.');
    await refresh();
  }

  async function resolveIssue(id: string) {
    await apiRequest(`/reviews/validation-issues/${id}/resolve`, {
      method: 'PATCH',
    });
    setStatus('Inconsistencia resolvida.');
    await refresh();
  }

  async function downloadCsv(path: string, fileName: string) {
    const csv = await apiTextRequest(path);
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = fileName;
    anchor.click();
    URL.revokeObjectURL(url);
  }

  async function processPending() {
    const result = await apiRequest<{ processedCount: number; totalPending: number }>(
      '/events/process?limit=100',
      { method: 'POST' },
    );
    setStatus(
      `Pipeline processado: ${result.processedCount}/${result.totalPending} eventos.`,
    );
    await refresh();
  }

  async function reprocessFailed() {
    const result = await apiRequest<{ processedCount: number; totalPending: number }>(
      '/events/reprocess-failed?limit=100',
      { method: 'POST' },
    );
    setStatus(
      `Reprocessamento de falhas: ${result.processedCount}/${result.totalPending}.`,
    );
    await refresh();
  }

  async function reprocessEvent(id: string) {
    await apiRequest(`/events/reprocess/${id}`, { method: 'POST' });
    setStatus(`Evento ${id.slice(0, 8)} reprocessado.`);
    await refresh();
  }

  async function downloadRawCsv() {
    await downloadCsv(`/events/raw/export.csv?${buildPipelineQuery(500)}`, 'raw-events.csv');
  }

  async function toggleAlertRule(rule: AlertRule) {
    await updateAlertRule(rule.id, { active: !rule.active });
    setStatus(`Regra ${rule.name} ${rule.active ? 'desativada' : 'ativada'}.`);
    await refresh();
  }

  return (
    <>
      <PageTitle subtitle="Cadastros base do MVP">Admin Cadastros</PageTitle>
      {status ? <p className="muted">{status}</p> : null}

      <form className="panel form-stack" onSubmit={submitProduct}>
        <strong>Novo produto</strong>
        <input value={newProduct} onChange={(e) => setNewProduct(e.target.value)} />
        <button type="submit">Criar produto</button>
      </form>

      <form className="panel form-stack" onSubmit={submitLocation}>
        <strong>Nova localizacao</strong>
        <input value={newLocation} onChange={(e) => setNewLocation(e.target.value)} />
        <input
          value={newLocationType}
          onChange={(e) => setNewLocationType(e.target.value)}
          placeholder="Tipo"
        />
        <button type="submit">Criar localizacao</button>
      </form>

      <form className="panel form-stack" onSubmit={submitClient}>
        <strong>Novo cliente</strong>
        <input value={newClient} onChange={(e) => setNewClient(e.target.value)} />
        <button type="submit">Criar cliente</button>
      </form>

      <form className="panel form-stack" onSubmit={submitStore}>
        <strong>Nova loja</strong>
        <select
          value={newStoreClientId}
          onChange={(e) => setNewStoreClientId(e.target.value)}
        >
          <option value="">Selecione cliente</option>
          {clients.map((item) => (
            <option key={item.id} value={item.id}>
              {item.name}
            </option>
          ))}
        </select>
        <input value={newStore} onChange={(e) => setNewStore(e.target.value)} />
        <button type="submit">Criar loja</button>
      </form>

      <form className="panel form-stack" onSubmit={submitReason}>
        <strong>Novo motivo</strong>
        <select
          value={newReasonType}
          onChange={(e) => setNewReasonType(e.target.value as 'LOSS' | 'RETURN')}
        >
          <option value="LOSS">Perda</option>
          <option value="RETURN">Devolucao</option>
        </select>
        <input value={newReason} onChange={(e) => setNewReason(e.target.value)} />
        <button type="submit">Criar motivo</button>
      </form>

      <section className="panel">
        <strong>Resumo de cadastros</strong>
        <p>Produtos: {products.length}</p>
        <p>Localizacoes: {locations.length}</p>
        <p>Clientes: {clients.length}</p>
        <p>Lojas: {stores.length}</p>
        <p>Motivos: {reasons.length}</p>
      </section>

      <section className="panel form-stack">
        <strong>Exportacao CSV</strong>
        <button
          type="button"
          onClick={() => void downloadCsv('/dashboard/export/kpis.csv', 'kpis.csv')}
        >
          Baixar KPIs CSV
        </button>
        <button
          type="button"
          onClick={() => void downloadCsv('/dashboard/export/trends.csv?days=7', 'trends.csv')}
        >
          Baixar Tendencias CSV
        </button>
      </section>

      <section className="panel">
        <strong>Regras de alerta</strong>
        <p className="muted">
          Ative/desative regras. Cooldown evita spam. Canais: PUSH (PWA) e EMAIL.
        </p>
        {alertRules.length === 0 ? (
          <p>Carregando regras...</p>
        ) : (
          <ul className="form-stack" style={{ listStyle: 'none', padding: 0 }}>
            {alertRules.map((rule) => (
              <li key={rule.id} className="history-item">
                <p>
                  <strong>{rule.name}</strong> ({rule.ruleKey})
                </p>
                {rule.description ? <p className="muted">{rule.description}</p> : null}
                <p>
                  Severidade: {rule.severity} | Cooldown: {rule.cooldownMinutes} min | Canais:{' '}
                  {rule.channels.join(', ')}
                </p>
                <button
                  type="button"
                  onClick={() => void toggleAlertRule(rule)}
                  className={rule.active ? 'secondary' : ''}
                >
                  {rule.active ? 'Desativar' : 'Ativar'}
                </button>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="panel">
        <strong>Eventos de alerta (ultimos 50)</strong>
        {alertEvents.length === 0 ? (
          <p>Nenhum evento recente.</p>
        ) : (
          <ul className="form-stack" style={{ listStyle: 'none', padding: 0, maxHeight: 300, overflowY: 'auto' }}>
            {alertEvents.slice(0, 20).map((ev) => (
              <li key={ev.id} className="history-item">
                <p>
                  <strong>{ev.rule?.name ?? ev.ruleId}</strong> | {ev.channel} | {ev.status}
                </p>
                <p className="muted">
                  {(ev.payload as { message?: string })?.message ?? JSON.stringify(ev.payload)}
                </p>
                <p>{new Date(ev.createdAt).toLocaleString()}</p>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="panel">
        <strong>Inconsistencias pendentes</strong>
        <div className="form-stack">
          <select
            value={issuesSeverityFilter}
            onChange={(e) => {
              setIssuesPage(1);
              setIssuesSeverityFilter(e.target.value);
            }}
          >
            <option value="">Todas severidades</option>
            <option value="warning">warning</option>
            <option value="critical">critical</option>
          </select>
          <input
            placeholder="Filtrar por issueCode"
            value={issuesCodeFilter}
            onChange={(e) => {
              setIssuesPage(1);
              setIssuesCodeFilter(e.target.value);
            }}
          />
        </div>
        {issues.length === 0 ? <p>Nenhuma inconsistencia pendente.</p> : null}
        {issues.map((item) => (
          <article key={item.id} className="history-item">
            <p>
              <strong>{item.issueCode}</strong> ({item.severity})
            </p>
            <p>{item.details ?? 'Sem detalhes'}</p>
            <p>{new Date(item.createdAt).toLocaleString()}</p>
            <button type="button" onClick={() => void resolveIssue(item.id)}>
              Marcar como resolvida
            </button>
          </article>
        ))}
        <div className="form-stack">
          <p>
            Pagina {issuesPage} de {issuesTotalPages}
          </p>
          <button
            type="button"
            disabled={issuesPage <= 1}
            onClick={() => setIssuesPage((prev) => prev - 1)}
          >
            Pagina anterior
          </button>
          <button
            type="button"
            disabled={issuesPage >= issuesTotalPages}
            onClick={() => setIssuesPage((prev) => prev + 1)}
          >
            Proxima pagina
          </button>
        </div>
      </section>

      <section className="panel">
        <strong>Pipeline de dados</strong>
        {pipelineMetrics ? (
          <>
            <p>
              Processing - pendentes: {pipelineMetrics.processing.pending} | processados:{' '}
              {pipelineMetrics.processing.processed} | falhos:{' '}
              {pipelineMetrics.processing.failed}
            </p>
            <p>
              Validacao - validos: {pipelineMetrics.validation.valid} | needs_review:{' '}
              {pipelineMetrics.validation.needsReview}
            </p>
            <p className="muted">
              Atualizado em: {new Date(pipelineMetrics.generatedAt).toLocaleString()}
            </p>
          </>
        ) : (
          <p>Carregando metricas...</p>
        )}
        <div className="form-stack">
          <button type="button" onClick={() => void processPending()}>
            Processar pendentes
          </button>
          <button type="button" onClick={() => void reprocessFailed()}>
            Reprocessar falhos
          </button>
          <select
            value={pipelineStatusFilter}
            onChange={(e) =>
              setPipelineStatusFilter(
                (e.target.value as '' | 'PENDING' | 'PROCESSED' | 'FAILED') ?? '',
              )
            }
          >
            <option value="">Todos status</option>
            <option value="PENDING">PENDING</option>
            <option value="PROCESSED">PROCESSED</option>
            <option value="FAILED">FAILED</option>
          </select>
          <select
            value={pipelineEventTypeFilter}
            onChange={(e) => setPipelineEventTypeFilter(e.target.value)}
          >
            <option value="">Todos event types</option>
            <option value="LOT_ENTRY_REGISTERED">LOT_ENTRY_REGISTERED</option>
            <option value="LOT_MOVED">LOT_MOVED</option>
            <option value="LOSS_REGISTERED">LOSS_REGISTERED</option>
            <option value="RETURN_REGISTERED">RETURN_REGISTERED</option>
            <option value="MATURITY_OVERRIDE">MATURITY_OVERRIDE</option>
            <option value="ORDER_PHOTO_CAPTURED">ORDER_PHOTO_CAPTURED</option>
          </select>
          <input
            placeholder="Buscar por idempotencyKey"
            value={pipelineIdempotencyFilter}
            onChange={(e) => setPipelineIdempotencyFilter(e.target.value)}
          />
          <label>
            De (data/hora)
            <input
              type="datetime-local"
              value={pipelineFromFilter}
              onChange={(e) => setPipelineFromFilter(e.target.value)}
            />
          </label>
          <label>
            Ate (data/hora)
            <input
              type="datetime-local"
              value={pipelineToFilter}
              onChange={(e) => setPipelineToFilter(e.target.value)}
            />
          </label>
          <button type="button" onClick={() => void downloadRawCsv()}>
            Baixar fila RAW (CSV)
          </button>
        </div>
        {pipelineEvents.map((event) => (
          <article key={event.id} className="history-item">
            <p>
              <strong>{event.eventType}</strong> -{' '}
              {event.processingState?.processingStatus ?? 'PENDING'} /{' '}
              {event.processingState?.validationStatus ?? 'VALID'}
            </p>
            <p>Idempotency: {event.idempotencyKey}</p>
            <p>
              Ingested:{' '}
              {event.processingState?.ingestedAt
                ? new Date(event.processingState.ingestedAt).toLocaleString()
                : '-'}
            </p>
            {event.processingState?.lastError ? (
              <p>Erro: {event.processingState.lastError}</p>
            ) : null}
            <button type="button" onClick={() => void reprocessEvent(event.id)}>
              Reprocessar evento
            </button>
          </article>
        ))}
      </section>
    </>
  );
}
