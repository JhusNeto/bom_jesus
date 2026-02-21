# API v1 e integrações

Base URL local: `http://localhost:3000/v1`

OpenAPI (Swagger): `http://localhost:3000/v1/docs`

## Catálogo de endpoints

| Domínio | Método | Endpoint | Auth | Descrição |
|---|---|---|---|---|
| Auth | POST | `/v1/auth/login` | não | Login e emissão de tokens |
| Auth | POST | `/v1/auth/refresh` | sim | Renovar access token |
| Cadastros | GET/POST | `/v1/products` | sim | Listar/criar produtos |
| Cadastros | GET/POST | `/v1/locations` | sim | Listar/criar localizações |
| Cadastros | GET/POST | `/v1/clients` | sim | Listar/criar clientes |
| Cadastros | GET/POST | `/v1/stores` | sim | Listar/criar lojas |
| Eventos | POST | `/v1/events` | sim | Ingestão RAW unificada |
| Histórico | GET | `/v1/events` | sim | Listagem de eventos com filtros |
| Fotos | POST | `/v1/uploads` | sim | Upload multipart de foto |
| Fotos | POST | `/v1/uploads/photo/presign` | sim | Pré-assinatura para upload direto |
| Dashboard | GET | `/v1/dashboard/summary` | sim | Cards principais |
| Dashboard | GET | `/v1/dashboard/timeseries` | sim | Série temporal |
| Revisão | GET/PATCH | `/v1/review/needs-review` | sim | Fila needs_review |

## Exemplo de evento unificado

### `POST /v1/events`

```json
{
  "idempotency_key": "device-9f3c::2026-02-19T10:05:33Z::lot_received::local-uuid-123",
  "event_type": "lot_received",
  "event_ts": "2026-02-19T10:05:33.000Z",
  "device_id": "device-9f3c",
  "payload": {
    "productId": "uuid-prod-1",
    "locationId": "uuid-loc-camera1",
    "boxes": 120,
    "kg": 2160.5,
    "notes": "Entrada manha"
  }
}
```

Resposta:

```json
{
  "raw_event_id": "uuid-raw-evt-999",
  "validation_status": "valid",
  "processing_status": "pending",
  "duplicated": false
}
```

## Curl rápido

### Login

```bash
curl -X POST "http://localhost:3000/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@bomjesus.local","password":"admin1234"}'
```

### Ingestão de evento RAW

```bash
curl -X POST "http://localhost:3000/v1/events" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "idempotency_key":"device-a::2026-02-20T11:30:00Z::return_recorded::abc",
    "event_type":"return_recorded",
    "event_ts":"2026-02-20T11:30:00.000Z",
    "device_id":"device-a",
    "payload":{
      "clientId":"<client-id>",
      "storeId":"<store-id>",
      "productId":"<product-id>",
      "boxes":3,
      "reason":"madura_demais"
    }
  }'
```

### Upload multipart

```bash
curl -X POST "http://localhost:3000/v1/uploads" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -F "file=@/caminho/foto.jpg"
```

## Postman e Insomnia

- Postman collection: `docs/postman/bom-jesus-v1.postman_collection.json`
- Insomnia: importe o OpenAPI diretamente de `http://localhost:3000/v1/docs-json`
