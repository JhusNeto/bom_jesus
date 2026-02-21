# Guia de Deploy — Operação Bom Jesus

Este documento descreve como fazer o deploy do sistema (backend NestJS, frontend React/Vite PWA e Postgres) em diferentes cenários.

---

## Resumo da Arquitetura

| Componente | Stack | Porta |
|------------|------|------|
| Backend | NestJS + Prisma | 3000 |
| Frontend | React + Vite + PWA | 80 (nginx) ou 5173 |
| Banco | PostgreSQL 16 | 5432 |

---

## Variáveis de Ambiente

### Backend (obrigatórias)

| Variável | Descrição | Exemplo |
|----------|-----------|---------|
| `PORT` | Porta do servidor | `3000` |
| `DATABASE_URL` | Connection string Postgres | `postgresql://user:pass@host:5432/bom_jesus?schema=public` |
| `JWT_SECRET` | Segredo para assinatura JWT | string aleatória longa (min. 32 chars) |

### Backend (opcionais)

| Variável | Descrição |
|----------|-----------|
| `JWT_ACCESS_EXPIRES_IN` | TTL do access token | `1h` |
| `JWT_REFRESH_EXPIRES_IN` | TTL do refresh token | `7d` |
| `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS` | Config para alertas por e-mail |
| `VAPID_PUBLIC_KEY`, `VAPID_PRIVATE_KEY` | Push notifications (PWA) |
| `S3_*` | Upload de fotos (devoluções) |
| `CORS_ORIGIN` | Origem permitida (ex: `https://app.bomjesus.com.br`) |

### Frontend

| Variável | Descrição |
|----------|-----------|
| `VITE_API_URL` | URL base da API (definida em **build time**) | `https://api.bomjesus.com.br` |

---

## Fluxo Rápido (Docker Compose)

```bash
cp .env.example .env
# Edite .env: POSTGRES_PASSWORD, JWT_SECRET, VITE_API_URL (URL pública da API)
docker compose -f docker-compose.prod.yml up -d --build
docker compose -f docker-compose.prod.yml exec backend node dist/scripts/seed-for-test.js
# Acesse: frontend em :80, API em :3000
```

---

## Opção 1: Docker Compose (VPS / Servidor próprio)

Ideal para DigitalOcean, Linode, AWS EC2, Hetzner, etc.

### Pré-requisitos

- Docker e Docker Compose
- Domínio (opcional; sem SSL pode usar IP:porta)

### Passos

1. **Clone e configure**

   ```bash
   git clone <repo> bom-jesus && cd bom-jesus
   cp .env.example .env
   # Edite .env: POSTGRES_PASSWORD, JWT_SECRET, VITE_API_URL (URL da API para o browser)
   ```

2. **Gere um JWT_SECRET forte**

   ```bash
   openssl rand -base64 48
   ```

3. **Defina a URL da API para o frontend**

   Crie `frontend/.env.production`:
   ```
   VITE_API_URL=https://api.seudominio.com.br
   ```
   Ou use variável no build (ver docker-compose.prod.yml).

4. **Suba os serviços**

   ```bash
   docker compose -f docker-compose.prod.yml up -d --build
   ```

5. **Migrations e seed**

   ```bash
   docker compose -f docker-compose.prod.yml exec backend npx prisma migrate deploy
   docker compose -f docker-compose.prod.yml exec backend npm run seed:test   # ou seed customizado
   ```

6. **HTTPS (recomendado)**

   Use Caddy ou nginx como proxy reverso com Let's Encrypt. Exemplo com Caddy:

   ```caddy
   api.seudominio.com.br {
     reverse_proxy localhost:3000
   }
   app.seudominio.com.br {
     reverse_proxy localhost:80
   }
   ```

---

## Opção 2: Railway / Render

PaaS gerenciado, mais simples que VPS.

### Backend no Railway

1. Crie um projeto e adicione:
   - **Postgres** (add-on)
   - **Web Service** (deploy do backend)

2. Configure o Web Service:
   - **Root Directory**: `backend`
   - **Build Command**: `npm ci && npx prisma generate && npm run build`
   - **Start Command**: `npx prisma migrate deploy && node dist/main`
   - **Variables**: `DATABASE_URL` (do add-on Postgres), `JWT_SECRET`

3. O Railway gera uma URL pública (ex: `https://backend-xxx.railway.app`).

### Frontend no Railway ou Vercel

**Railway**:
- Adicione outro Web Service apontando para `frontend`
- Build: `npm ci && npm run build`
- Serve: use um servidor estático (ex: `npx serve -s dist -l 3000`)
- Variável de build: `VITE_API_URL=https://backend-xxx.railway.app`

**Vercel** (recomendado para frontend estático):
- Conecte o repositório
- **Root Directory**: `frontend`
- **Framework Preset**: Vite
- **Build Command**: `npm run build`
- **Output Directory**: `dist`
- **Environment Variable**: `VITE_API_URL` = URL do backend

---

## Opção 3: VPS com Script de Deploy

Script de exemplo para deploy via SSH:

```bash
#!/bin/bash
# deploy.sh - executar no servidor
set -e
cd /opt/bom-jesus
git pull
docker compose -f docker-compose.prod.yml build --no-cache
docker compose -f docker-compose.prod.yml up -d
docker compose -f docker-compose.prod.yml exec -T backend npx prisma migrate deploy
```

---

## Checklist Pós-Deploy

- [ ] Health check: `GET /v1` retorna 200
- [ ] Login funciona no frontend
- [ ] CORS permite a origem do frontend
- [ ] Migrations aplicadas
- [ ] Seed admin executado (ou usuário criado manualmente)
- [ ] Backup diário configurado (ver `docs/backup-restore-runbook.md`)
- [ ] Alertas (SMTP/VAPID) configurados se necessário

---

## CORS

Em produção, configure o CORS para a origem do frontend. Se usar a variável `CORS_ORIGIN`, atualize `main.ts`:

```ts
app.enableCors({
  origin: process.env.CORS_ORIGIN?.split(',') ?? true,
  credentials: true,
});
```

---

## Troubleshooting

| Problema | Solução |
|----------|---------|
| Frontend não conecta à API | Conferir `VITE_API_URL` no build e CORS no backend |
| 502 Bad Gateway | Backend não iniciou; ver logs do container |
| Migrations falham | `DATABASE_URL` correta; banco acessível |
| PWA não atualiza | Service worker com `registerType: 'autoUpdate'`; usuário pode precisar atualizar a aba |
