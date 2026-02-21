import { useState } from 'react';
import { PageTitle } from '../components/page-title';
import { useAuth } from '../state/auth-context';

const OPERACAO_ITEMS = [
  'Registrou todas as pesagens do dia?',
  'Registrou movimentações de câmaras?',
  'Registrou perdas?',
  'Registrou devoluções (com foto quando possível)?',
  'Conferiu o dashboard?',
  'Revisou needs_review no Admin (se tiver acesso)?',
];

const ADM_ITEMS = [
  'Exportou KPIs/trends para relatório?',
  'Analisou devoluções por cliente?',
  'Conferiu histórico de eventos?',
  'Revisou inconsistências pendentes?',
];

const GESTOR_ITEMS = [
  'Auditou indicadores do dia?',
  'Identificou riscos de maturação?',
  'Revisou fila needs_review?',
  'Conferiu pipeline de dados (Admin)?',
];

const STORAGE_KEY = 'bom-jesus-checklist';

function loadProgress(role: string, day: number, length: number): boolean[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    const data = JSON.parse(raw) as Record<string, boolean[]>;
    const key = `${role}-${day}`;
    const saved = data[key] ?? [];
    const result = Array.from({ length }, (_, i) => saved[i] ?? false);
    return result;
  } catch {
    return [];
  }
}

function saveProgress(role: string, day: number, checked: boolean[]) {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    const data = raw ? (JSON.parse(raw) as Record<string, boolean[]>) : {};
    data[`${role}-${day}`] = checked;
    localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
  } catch {
    // ignore
  }
}

function getRoleItems(role: string) {
  if (role === 'ADMIN' || role === 'MANAGER') return GESTOR_ITEMS;
  if (role === 'ADMINISTRATIVE') return ADM_ITEMS;
  return OPERACAO_ITEMS;
}

export function ChecklistPage() {
  const { user } = useAuth();
  const role = user?.role ?? 'OPERATOR';
  const items = getRoleItems(role);
  const [day, setDay] = useState(1);
  const [checked, setChecked] = useState<boolean[]>(() =>
    loadProgress(role, 1, items.length),
  );

  function handleToggle(index: number) {
    const next = [...checked];
    next[index] = !next[index];
    setChecked(next);
    saveProgress(role, day, next);
  }

  function handleDayChange(newDay: number) {
    setDay(newDay);
    setChecked(loadProgress(role, newDay, items.length));
  }

  const completed = checked.filter(Boolean).length;
  const total = items.length;

  return (
    <>
      <PageTitle subtitle="10 dias úteis — Registrou tudo? Conferiu dashboard? Revisou needs_review?">
        Checklist diário
      </PageTitle>
      <section className="panel form-stack">
        <label>
          Dia
          <select
            value={day}
            onChange={(e) => handleDayChange(Number(e.target.value))}
          >
            {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((d) => (
              <option key={d} value={d}>
                Dia {d}
              </option>
            ))}
          </select>
        </label>
        <p className="muted">
          Perfil: {role === 'ADMIN' || role === 'MANAGER' ? 'Gestor' : role === 'ADMINISTRATIVE' ? 'Administrativo' : 'Operação'} — {completed}/{total} concluídos
        </p>
      </section>
      <section className="panel checklist-items">
        <ul>
          {items.map((item, i) => (
            <li key={i} className="checklist-item">
              <label>
                <input
                  type="checkbox"
                  checked={checked[i] ?? false}
                  onChange={() => handleToggle(i)}
                />
                <span>{item}</span>
              </label>
            </li>
          ))}
        </ul>
      </section>
      <p className="muted">
        Impressão: use o menu do navegador (Ctrl/Cmd+P) para imprimir ou salvar como PDF.
      </p>
    </>
  );
}
