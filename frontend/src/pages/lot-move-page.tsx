import type { FormEvent } from 'react';
import { useEffect, useState } from 'react';
import { listLocations } from '../api/catalog';
import { PageTitle } from '../components/page-title';
import { useAuth } from '../state/auth-context';
import { queueEvent } from '../sync/queue-event';
import { createLocalId } from '../utils/id';
import { validateLotMove } from '../validation/event-validation';

export function LotMovePage() {
  const { user } = useAuth();
  const [lotId, setLotId] = useState('');
  const [fromLocationId, setFromLocationId] = useState('');
  const [toLocationId, setToLocationId] = useState('');
  const [boxes, setBoxes] = useState('');
  const [kg, setKg] = useState('');
  const [status, setStatus] = useState('');
  const [warnings, setWarnings] = useState<string[]>([]);
  const [locations, setLocations] = useState<Array<{ id: string; name: string }>>([]);

  useEffect(() => {
    async function loadLocations() {
      const data = await listLocations();
      setLocations(data);
    }

    void loadLocations();
  }, []);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const eventTsIso = new Date().toISOString();
    const validation = validateLotMove({
      lotId,
      fromLocationId,
      toLocationId,
      boxes: boxes ? Number(boxes) : undefined,
      kg: kg ? Number(kg) : undefined,
      eventTsIso,
    });
    if (validation.blockingErrors.length > 0) {
      setStatus(validation.blockingErrors.join(' '));
      setWarnings(validation.warnings);
      return;
    }
    setWarnings(validation.warnings);

    const payload = {
      fromLocationId,
      toLocationId,
      boxes: boxes ? Number(boxes) : undefined,
      kg: kg ? Number(kg) : undefined,
      happenedAt: eventTsIso,
      userId: user?.id ?? '',
      idempotencyKey: createLocalId(),
    };

    const result = await queueEvent(`/lots/${lotId}/move`, 'LOT_MOVED', payload);
    setStatus(result.synced ? 'Movimentacao sincronizada.' : 'Movimentacao salva offline.');
  }

  return (
    <>
      <PageTitle>Mover lote</PageTitle>
      <form className="panel form-stack" onSubmit={onSubmit}>
        <label>
          Lote (ID)
          <input value={lotId} onChange={(e) => setLotId(e.target.value)} />
        </label>
        <label>
          Origem
          <select value={fromLocationId} onChange={(e) => setFromLocationId(e.target.value)}>
            <option value="">Selecione</option>
            {locations.map((item) => (
              <option key={item.id} value={item.id}>
                {item.name}
              </option>
            ))}
          </select>
        </label>
        <label>
          Destino
          <select value={toLocationId} onChange={(e) => setToLocationId(e.target.value)}>
            <option value="">Selecione</option>
            {locations.map((item) => (
              <option key={item.id} value={item.id}>
                {item.name}
              </option>
            ))}
          </select>
        </label>
        <label>
          Caixas
          <input inputMode="numeric" value={boxes} onChange={(e) => setBoxes(e.target.value)} />
        </label>
        <label>
          Kg
          <input inputMode="decimal" value={kg} onChange={(e) => setKg(e.target.value)} />
        </label>
        <button type="submit">Salvar movimentacao</button>
        {status ? <p className="muted">{status}</p> : null}
        {warnings.map((warning) => (
          <p key={warning} className="muted">
            Aviso: {warning}
          </p>
        ))}
      </form>
    </>
  );
}
