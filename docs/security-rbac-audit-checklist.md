# Checklist de Segurança, RBAC e Auditoria

## 1. Autenticação

| Item | Status | Notas |
|------|--------|-------|
| JWT access token | ✅ | Expiração configurável (`JWT_ACCESS_EXPIRES_IN`, default 1h) |
| Refresh token rotativo | ✅ | `JWT_REFRESH_EXPIRES_IN` (default 7d), hash em DB |
| Senha com bcrypt | ✅ | Hash na criação/migração |
| Rotação de refresh | ✅ | Novo token a cada refresh, antigo revogado |

## 2. RBAC por Perfil

| Perfil | Papel | Responsabilidades |
|--------|-------|-------------------|
| Operador | `OPERATOR` | Cria eventos (entrada, movimentação, perdas, devoluções, uploads) |
| Administrativo | `ADMINISTRATIVE` | Revisa needs_review, visualiza dashboard, regras de validação |
| Gestor | `MANAGER` | Idem ADM + regras de alerta, exportações |
| Admin | `ADMIN` | Cadastros (produtos, locais, clientes, lojas, motivos), alertas, usuários |

## 3. RBAC por Endpoint

| Endpoint | OPERATOR | ADMINISTRATIVE | MANAGER | ADMIN |
|----------|----------|----------------|---------|-------|
| `POST /events`, `POST /lots/*`, `POST /losses`, `POST /returns`, `POST /uploads` | ✅ | ✅ | ✅ | ✅ |
| `GET /dashboard/*`, `GET /lots`, `GET /losses`, `GET /returns` | ✅ | ✅ | ✅ | ✅ |
| `GET/PATCH /review/needs-review`, `GET/PATCH /reviews/validation-issues` | ❌ | ✅ | ✅ | ✅ |
| `GET/PATCH /events/process`, `reprocess`, `raw`, `metrics` | ❌ | ✅ | ✅ | ✅ |
| `GET/PATCH /validation-rules` | ❌ | ✅ | ✅ | ✅ |
| `GET/POST /catalog/*` (produtos, locais, clientes, lojas, motivos) | ❌ | ✅ | ✅ | ✅ |
| `GET/PATCH /alerts/rules`, `GET /alerts/events` | ❌ | ❌ | ✅ | ✅ |
| `PATCH /alerts/rules/:id` (editar regra) | ❌ | ❌ | ❌ | ✅ |
| `POST /alerts/push-subscription`, `GET /vapid-public-key` | ✅ | ✅ | ✅ | ✅ |

## 4. Audit Trail

| Item | Status | Implementação |
|------|--------|---------------|
| RAW imutável | ✅ | Trigger `raw.prevent_raw_event_mutation` bloqueia UPDATE/DELETE em RawEvent |
| CLEAN referencia RAW | ✅ | `StockMovement`, `LossRecord`, `ReturnRecord` com `sourceRawEventId` |
| Cadastros auditados | ✅ | `AuditLog` em create de Product, Location, Client, Store, Reason |
| Resolução de issues | ✅ | `ReviewAction` com actorUserId e notas |

## 5. Hardening Pendente / Recomendações

- [ ] Rate limiting em `/auth/login` (evitar brute-force)
- [ ] CORS restrito em produção (origem explícita)
- [ ] Helmet ou headers de segurança (X-Content-Type-Options, etc.)
- [ ] Logs de acesso (quem acessou o quê, quando) — opcional
- [ ] Gestão de usuários (CRUD) — endpoint Admin para criar/editar usuários com RBAC

## 6. Retenção (Valores Assumidos)

| Dado | Retenção Mínima | Ação |
|------|-----------------|------|
| RAW events | 2 anos | Arquivar/archive antes de purge |
| Fotos (bucket) | 1 ano | Versionamento/snapshot; depois arquivar |
| Logs técnicos | 30–90 dias | Rotação configurável |
| AuditLog | 2 anos (recomendado) | Alinhar com RAW |

*Ajustar com dono do negócio na Semana 2.*
