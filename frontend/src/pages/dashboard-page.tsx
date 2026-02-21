import { useEffect, useState } from 'react';
import { apiRequest } from '../api/client';
import { listClients } from '../api/catalog';
import { PageTitle } from '../components/page-title';
import { Tooltip } from '../components/tooltip';

interface DashboardKpis {
  caixasDoDia: number;
  kgDoDia: number;
  estoquePorMaturacao: Record<string, { boxes: number; kg: number }>;
  perdas: {
    hoje: { caixas: number; kg: number };
    mes: { caixas: number; kg: number };
  };
  devolucoesTopClientes: Array<{
    clientId: string;
    cliente: string;
    caixas: number;
    registros: number;
  }>;
  atualizadoEm: string;
}

interface TrendResponse {
  series: Array<{ date: string; movements: number; losses: number; returns: number }>;
}

export function DashboardPage() {
  const [kpis, setKpis] = useState<DashboardKpis | null>(null);
  const [trends, setTrends] = useState<TrendResponse | null>(null);
  const [clients, setClients] = useState<Array<{ id: string; name: string }>>([]);
  const [from, setFrom] = useState('');
  const [to, setTo] = useState('');
  const [clientId, setClientId] = useState('');
  const [error, setError] = useState('');

  const query = new URLSearchParams();
  if (from) query.set('from', from);
  if (to) query.set('to', to);
  if (clientId) query.set('clientId', clientId);
  const cacheKey = `dashboard-cache:${query.toString()}`;

  async function loadDashboard() {
    try {
      setError('');
      const [kpiData, trendData] = await Promise.all([
        apiRequest<DashboardKpis>(`/dashboard/kpis?${query.toString()}`),
        apiRequest<TrendResponse>(`/dashboard/trends?days=7&${query.toString()}`),
      ]);
      setKpis(kpiData);
      setTrends(trendData);
      localStorage.setItem(
        cacheKey,
        JSON.stringify({ ts: Date.now(), kpis: kpiData, trends: trendData }),
      );
    } catch (loadError) {
      setError(
        loadError instanceof Error
          ? loadError.message
          : 'Falha ao carregar dashboard.',
      );
    }
  }

  useEffect(() => {
    async function boot() {
      const cached = localStorage.getItem(cacheKey);
      if (cached) {
        const parsed = JSON.parse(cached) as {
          ts: number;
          kpis: DashboardKpis;
          trends: TrendResponse;
        };
        if (Date.now() - parsed.ts <= 60_000) {
          setKpis(parsed.kpis);
          setTrends(parsed.trends);
        }
      }
      const clientsData = await listClients();
      setClients(clientsData);
      await loadDashboard();
    }
    void boot();
    const timer = window.setInterval(() => {
      void loadDashboard();
    }, 60_000);
    return () => window.clearInterval(timer);
  }, [from, to, clientId]);

  const maxTrendValue = Math.max(
    1,
    ...(trends?.series.flatMap((day) => [
      day.movements,
      day.losses,
      day.returns,
    ]) ?? [1]),
  );

  return (
    <>
      <PageTitle subtitle="Atualizacao ate 5 minutos">Dashboard MVP</PageTitle>
      <section className="panel form-stack dashboard-filters">
        <label>
          Data inicial
          <input type="date" value={from} onChange={(e) => setFrom(e.target.value)} />
        </label>
        <label>
          Data final
          <input type="date" value={to} onChange={(e) => setTo(e.target.value)} />
        </label>
        <label>
          Cliente
          <select value={clientId} onChange={(e) => setClientId(e.target.value)}>
            <option value="">Todos</option>
            {clients.map((client) => (
              <option key={client.id} value={client.id}>
                {client.name}
              </option>
            ))}
          </select>
        </label>
        <button type="button" onClick={() => void loadDashboard()}>
          Atualizar agora
        </button>
      </section>
      {error ? <p className="error">{error}</p> : null}
      {!kpis ? (
        <p>Carregando...</p>
      ) : (
        <div className="kpi-grid">
          <article className="panel">
            <h3>
              <Tooltip text="Saídas (EXIT) do dia atual.">Caixas vendidas hoje</Tooltip>
            </h3>
            <strong>{kpis.caixasDoDia}</strong>
            <p>{kpis.kgDoDia} kg</p>
          </article>
          <article className="panel">
            <h3>
              <Tooltip text="Verde, de vez, madura (atualização diária).">Estoque por maturacao</Tooltip>
            </h3>
            <p>Verde: {kpis.estoquePorMaturacao.VERDE?.boxes ?? 0}</p>
            <p>De vez: {kpis.estoquePorMaturacao.DE_VEZ?.boxes ?? 0}</p>
            <p>Madura: {kpis.estoquePorMaturacao.MADURA?.boxes ?? 0}</p>
          </article>
          <article className="panel">
            <h3>Perdas</h3>
            <p>Hoje: {kpis.perdas.hoje.caixas} caixas</p>
            <p>Mes: {kpis.perdas.mes.caixas} caixas</p>
          </article>
          <article className="panel">
            <h3>Devolucoes (7d)</h3>
            {kpis.devolucoesTopClientes.map((row) => (
              <p key={row.clientId}>
                {row.cliente}: {row.caixas} caixas ({row.registros} registros)
              </p>
            ))}
          </article>
        </div>
      )}
      <section className="panel">
        <h3>Serie ultimos 7 dias</h3>
        <div className="trend-grid">
          {trends?.series.map((day) => (
            <article key={day.date} className="trend-day">
              <strong>{day.date.slice(5)}</strong>
              <div
                className="bar sold"
                style={{ width: `${(day.movements / maxTrendValue) * 100}%` }}
              >
                vendas {day.movements}
              </div>
              <div
                className="bar loss"
                style={{ width: `${(day.losses / maxTrendValue) * 100}%` }}
              >
                perdas {day.losses}
              </div>
              <div
                className="bar returns"
                style={{ width: `${(day.returns / maxTrendValue) * 100}%` }}
              >
                devolucoes {day.returns}
              </div>
            </article>
          ))}
        </div>
      </section>
    </>
  );
}
