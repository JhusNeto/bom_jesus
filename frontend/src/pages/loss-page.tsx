import type { FormEvent } from 'react';
import { useEffect, useState } from 'react';
import { listLocations, listProducts, listReasons } from '../api/catalog';
import { PageTitle } from '../components/page-title';
import { useAuth } from '../state/auth-context';
import { queueEvent } from '../sync/queue-event';
import { createLocalId } from '../utils/id';
import { validateLoss } from '../validation/event-validation';

export function LossPage() {
  const { user } = useAuth();
  const [lotId, setLotId] = useState('');
  const [reason, setReason] = useState('');
  const [productId, setProductId] = useState('');
  const [locationId, setLocationId] = useState('');
  const [boxes, setBoxes] = useState('');
  const [kg, setKg] = useState('');
  const [status, setStatus] = useState('');
  const [warnings, setWarnings] = useState<string[]>([]);
  const [lossReasons, setLossReasons] = useState<Array<{ id: string; name: string }>>([]);
  const [products, setProducts] = useState<Array<{ id: string; name: string }>>([]);
  const [locations, setLocations] = useState<Array<{ id: string; name: string }>>([]);

  useEffect(() => {
    async function loadReasons() {
      const [reasons, productsData, locationsData] = await Promise.all([
        listReasons('LOSS'),
        listProducts(),
        listLocations(),
      ]);
      setLossReasons(reasons);
      setProducts(productsData);
      setLocations(locationsData);
      if (!reason && reasons[0]) setReason(reasons[0].name);
      if (!productId && productsData[0]) setProductId(productsData[0].id);
      if (!locationId && locationsData[0]) setLocationId(locationsData[0].id);
    }

    void loadReasons();
  }, []);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const eventTsIso = new Date().toISOString();
    const validation = validateLoss({
      lotId: lotId || undefined,
      productId: productId || undefined,
      locationId,
      reason,
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
      lotId: lotId || undefined,
      productId: productId || undefined,
      locationId,
      reason,
      boxes: boxes ? Number(boxes) : undefined,
      kg: kg ? Number(kg) : undefined,
      happenedAt: eventTsIso,
      userId: user?.id ?? '',
      idempotencyKey: createLocalId(),
    };

    const result = await queueEvent('/losses', 'LOSS_REGISTERED', payload);
    setStatus(result.synced ? 'Perda sincronizada.' : 'Perda salva offline.');
  }

  return (
    <>
      <PageTitle>Registrar perda</PageTitle>
      <form className="panel form-stack" onSubmit={onSubmit}>
        <label>
          Lote (ID)
          <input value={lotId} onChange={(e) => setLotId(e.target.value)} />
        </label>
        <label>
          Produto (opcional se lote informado)
          <select value={productId} onChange={(e) => setProductId(e.target.value)}>
            <option value="">Selecione</option>
            {products.map((item) => (
              <option key={item.id} value={item.id}>
                {item.name}
              </option>
            ))}
          </select>
        </label>
        <label>
          Localizacao
          <select value={locationId} onChange={(e) => setLocationId(e.target.value)}>
            <option value="">Selecione</option>
            {locations.map((item) => (
              <option key={item.id} value={item.id}>
                {item.name}
              </option>
            ))}
          </select>
        </label>
        <label>
          Motivo
          <select value={reason} onChange={(e) => setReason(e.target.value)}>
            <option value="">Selecione</option>
            {lossReasons.map((item) => (
              <option key={item.id} value={item.name}>
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
        <button type="submit">Salvar perda</button>
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
