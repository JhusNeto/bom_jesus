import type { ChangeEvent, FormEvent } from 'react';
import { useEffect, useState } from 'react';
import { apiRequest } from '../api/client';
import { listClients, listProducts, listReasons, listStores } from '../api/catalog';
import { PageTitle } from '../components/page-title';
import { Tooltip } from '../components/tooltip';
import { useAuth } from '../state/auth-context';
import { queueEvent } from '../sync/queue-event';
import { createLocalId } from '../utils/id';
import { validateReturn } from '../validation/event-validation';

function toBase64(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(String(reader.result));
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}

export function ReturnPage() {
  const { user } = useAuth();
  const [lotId, setLotId] = useState('');
  const [clientId, setClientId] = useState('');
  const [storeId, setStoreId] = useState('');
  const [productId, setProductId] = useState('');
  const [reason, setReason] = useState('');
  const [boxes, setBoxes] = useState('');
  const [kg, setKg] = useState('');
  const [photoUrl, setPhotoUrl] = useState('');
  const [photoFile, setPhotoFile] = useState<File | null>(null);
  const [status, setStatus] = useState('');
  const [warnings, setWarnings] = useState<string[]>([]);
  const [clients, setClients] = useState<Array<{ id: string; name: string }>>([]);
  const [products, setProducts] = useState<Array<{ id: string; name: string }>>([]);
  const [stores, setStores] = useState<Array<{ id: string; name: string }>>([]);
  const [reasons, setReasons] = useState<Array<{ id: string; name: string }>>([]);

  useEffect(() => {
    async function loadCatalog() {
      const [clientsData, reasonsData, productsData] = await Promise.all([
        listClients(),
        listReasons('RETURN'),
        listProducts(),
      ]);
      setClients(clientsData);
      setReasons(reasonsData);
      setProducts(productsData);
      if (!clientId && clientsData[0]) setClientId(clientsData[0].id);
      if (!reason && reasonsData[0]) setReason(reasonsData[0].name);
      if (!productId && productsData[0]) setProductId(productsData[0].id);
    }
    void loadCatalog();
  }, []);

  useEffect(() => {
    async function loadStores() {
      if (!clientId) return;
      const storesData = await listStores(clientId);
      setStores(storesData);
      if (storesData[0]) setStoreId(storesData[0].id);
    }
    void loadStores();
  }, [clientId]);

  async function onFile(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) return;
    setPhotoFile(file);

    if (!navigator.onLine) {
      const base64 = await toBase64(file);
      setPhotoUrl(base64);
    }
  }

  async function uploadPhotoIfNeeded() {
    if (!photoFile) return photoUrl || undefined;
    if (!navigator.onLine) return photoUrl || undefined;

    const presign = await apiRequest<{
      uploadUrl: string | null;
      publicUrl: string;
    }>('/uploads/photo/presign', {
      method: 'POST',
      body: JSON.stringify({
        fileName: photoFile.name,
        contentType: photoFile.type || 'image/jpeg',
      }),
    });

    if (presign.uploadUrl) {
      await fetch(presign.uploadUrl, {
        method: 'PUT',
        headers: { 'Content-Type': photoFile.type || 'image/jpeg' },
        body: photoFile,
      });
    }

    return presign.publicUrl;
  }

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const eventTsIso = new Date().toISOString();
    const validation = validateReturn({
      clientId,
      storeId,
      productId,
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

    const uploadedPhotoUrl = await uploadPhotoIfNeeded();
    const payload = {
      lotId: lotId || undefined,
      clientId,
      storeId,
      productId,
      reason,
      boxes: boxes ? Number(boxes) : undefined,
      kg: kg ? Number(kg) : undefined,
      photoUrl: uploadedPhotoUrl,
      happenedAt: eventTsIso,
      userId: user?.id ?? '',
      idempotencyKey: createLocalId(),
    };

    const result = await queueEvent('/returns', 'RETURN_REGISTERED', payload);
    setStatus(result.synced ? 'Devolucao sincronizada.' : 'Devolucao salva offline.');
  }

  return (
    <>
      <PageTitle>Registrar devolucao</PageTitle>
      <form className="panel form-stack" onSubmit={onSubmit}>
        <label>
          Lote (ID opcional)
          <input value={lotId} onChange={(e) => setLotId(e.target.value)} />
        </label>
        <label>
          <Tooltip text="Cliente que devolveu. Obrigatório.">Cliente</Tooltip>
          <select value={clientId} onChange={(e) => setClientId(e.target.value)}>
            <option value="">Selecione</option>
            {clients.map((item) => (
              <option key={item.id} value={item.id}>
                {item.name}
              </option>
            ))}
          </select>
        </label>
        <label>
          <Tooltip text="Ponto de venda. Obrigatório.">Loja</Tooltip>
          <select value={storeId} onChange={(e) => setStoreId(e.target.value)}>
            <option value="">Selecione</option>
            {stores.map((item) => (
              <option key={item.id} value={item.id}>
                {item.name}
              </option>
            ))}
          </select>
        </label>
        <label>
          Produto
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
          Motivo
          <select value={reason} onChange={(e) => setReason(e.target.value)}>
            <option value="">Selecione</option>
            {reasons.map((item) => (
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
        <label>
          <Tooltip text="Recomendado para evidência. Offline: foto fica pendente.">Foto (opcional)</Tooltip>
          <input type="file" accept="image/*" onChange={onFile} />
        </label>
        <button type="submit">Salvar devolucao</button>
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
