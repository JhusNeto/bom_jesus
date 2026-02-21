import type { FormEvent } from 'react';
import { useEffect, useState } from 'react';
import { listLocations, listProducts } from '../api/catalog';
import { PageTitle } from '../components/page-title';
import { Tooltip } from '../components/tooltip';
import { useAuth } from '../state/auth-context';
import { queueEvent } from '../sync/queue-event';
import { createLocalId } from '../utils/id';
import { validateLotEntry } from '../validation/event-validation';

export function LotEntryPage() {
  const { user } = useAuth();
  const [productId, setProductId] = useState('');
  const [locationId, setLocationId] = useState('');
  const [boxes, setBoxes] = useState('');
  const [kg, setKg] = useState('');
  const [status, setStatus] = useState('');
  const [warnings, setWarnings] = useState<string[]>([]);
  const [products, setProducts] = useState<Array<{ id: string; name: string }>>([]);
  const [locations, setLocations] = useState<Array<{ id: string; name: string }>>([]);

  useEffect(() => {
    async function loadCatalog() {
      const [productsData, locationsData] = await Promise.all([
        listProducts(),
        listLocations(),
      ]);
      setProducts(productsData);
      setLocations(locationsData);
      if (!productId && productsData[0]) setProductId(productsData[0].id);
      if (!locationId && locationsData[0]) setLocationId(locationsData[0].id);
    }

    void loadCatalog();
  }, []);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const eventTsIso = new Date().toISOString();
    const validation = validateLotEntry({
      productId,
      locationId,
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
      productId,
      locationId,
      boxes: boxes ? Number(boxes) : undefined,
      kg: kg ? Number(kg) : undefined,
      happenedAt: eventTsIso,
      userId: user?.id ?? '',
      idempotencyKey: createLocalId(),
    };

    const result = await queueEvent('/lots/entry', 'LOT_ENTRY_REGISTERED', payload);
    setStatus(result.synced ? 'Entrada sincronizada.' : 'Entrada salva offline.');
    setBoxes('');
    setKg('');
  }

  return (
    <>
      <PageTitle>Entrada de lote</PageTitle>
      <form className="panel form-stack" onSubmit={onSubmit}>
        <label>
          <Tooltip text="Produto da balança. Obrigatório.">Produto</Tooltip>
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
          <Tooltip text="Câmara ou área de destino. Obrigatório.">Localizacao</Tooltip>
          <select value={locationId} onChange={(e) => setLocationId(e.target.value)}>
            <option value="">Sem localizacao</option>
            {locations.map((item) => (
              <option key={item.id} value={item.id}>
                {item.name}
              </option>
            ))}
          </select>
        </label>
        <label>
          <Tooltip text="Informe caixas ou kg (um dos dois obrigatório).">Caixas</Tooltip>
          <input inputMode="numeric" value={boxes} onChange={(e) => setBoxes(e.target.value)} />
        </label>
        <label>
          Kg
          <input inputMode="decimal" value={kg} onChange={(e) => setKg(e.target.value)} />
        </label>
        <button type="submit">Salvar entrada</button>
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
