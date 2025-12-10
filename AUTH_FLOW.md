# 🔐 Fluxo de Autenticação - Sistema Operacional Bom Jesus

## Visão Geral

O sistema utiliza autenticação baseada em **JWT (JSON Web Tokens)** com **refresh tokens** armazenados no **Redis** para segurança adicional.

---

## 🎯 Arquitetura de Autenticação

### Componentes

1. **Access Token** (JWT)
   - Expira em **10 minutos**
   - Contém: `sub` (email), `user_id`, `role`
   - Usado em todas as requisições autenticadas
   - Enviado no header: `Authorization: Bearer <token>`

2. **Refresh Token** (JWT)
   - Expira em **7 dias**
   - Armazenado no **Redis** (whitelist)
   - Usado apenas para obter novo access token
   - Revogado no logout

3. **Redis Whitelist**
   - Armazena refresh tokens válidos
   - Chave: `refresh_token:{user_id}:{refresh_token}`
   - TTL: 7 dias
   - Permite revogação imediata (logout)

---

## 📋 Fluxos Principais

### 1. Login

```
┌─────────┐                    ┌──────────┐                    ┌─────────┐
│ Frontend│                    │ Backend  │                    │ Redis   │
└────┬────┘                    └────┬─────┘                    └────┬────┘
     │                               │                               │
     │ POST /auth/login              │                               │
     │ {email, password}             │                               │
     ├──────────────────────────────>│                               │
     │                               │                               │
     │                               │ Verifica email/senha          │
     │                               │ (bcrypt)                      │
     │                               │                               │
     │                               │ Gera Access Token (10min)     │
     │                               │ Gera Refresh Token (7 dias)   │
     │                               │                               │
     │                               │ Salva refresh no Redis        │
     │                               ├───────────────────────────────>│
     │                               │                               │
     │                               │ Retorna tokens                │
     │<──────────────────────────────┤                               │
     │                               │                               │
     │ Salva tokens no localStorage  │                               │
     │ Redireciona para /dashboard   │                               │
     │                               │                               │
```

**Endpoint:** `POST /api/v1/auth/login`

**Request:**
```json
{
  "email": "usuario@example.com",
  "password": "senha123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "usuario@example.com",
    "name": "Nome do Usuário",
    "role": "admin"
  }
}
```

---

### 2. Requisição Autenticada

```
┌─────────┐                    ┌──────────┐
│ Frontend│                    │ Backend  │
└────┬────┘                    └────┬─────┘
     │                               │
     │ GET /api/v1/cargas            │
     │ Authorization: Bearer <token>  │
     ├──────────────────────────────>│
     │                               │
     │                               │ Valida token JWT
     │                               │ Decodifica payload
     │                               │ Busca usuário no banco
     │                               │ Verifica se está ativo
     │                               │
     │                               │ Retorna dados
     │<──────────────────────────────┤
     │                               │
```

**Middleware:** `get_current_user` dependency

---

### 3. Refresh Automático (Access Token Expirado)

```
┌─────────┐                    ┌──────────┐                    ┌─────────┐
│ Frontend│                    │ Backend  │                    │ Redis   │
└────┬────┘                    └────┬─────┘                    └────┬────┘
     │                               │                               │
     │ GET /api/v1/cargas            │                               │
     │ Authorization: Bearer <expired>│                               │
     ├──────────────────────────────>│                               │
     │                               │                               │
     │                               │ Token expirado (401)          │
     │<──────────────────────────────┤                               │
     │                               │                               │
     │ Interceptor detecta 401       │                               │
     │                               │                               │
     │ POST /auth/refresh             │                               │
     │ {refresh_token}                │                               │
     ├──────────────────────────────>│                               │
     │                               │                               │
     │                               │ Verifica refresh no Redis     │
     │                               ├───────────────────────────────>│
     │                               │<───────────────────────────────┤
     │                               │                               │
     │                               │ Gera novo access token        │
     │                               │                               │
     │                               │ Retorna novo access token     │
     │<──────────────────────────────┤                               │
     │                               │                               │
     │ Salva novo token               │                               │
     │ Retenta requisição original    │                               │
     │                               │                               │
```

**Interceptor Axios:** Implementado em `frontend/services/api.ts`

**Endpoint:** `POST /api/v1/auth/refresh`

**Request:**
```json
{
  "refresh_token": "eyJhbGc..."
}
```

**Response:**
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

---

### 4. Logout

```
┌─────────┐                    ┌──────────┐                    ┌─────────┐
│ Frontend│                    │ Backend  │                    │ Redis   │
└────┬────┘                    └────┬─────┘                    └────┬────┘
     │                               │                               │
     │ POST /auth/logout              │                               │
     │ {refresh_token}                │                               │
     ├──────────────────────────────>│                               │
     │                               │                               │
     │                               │ Remove refresh do Redis       │
     │                               ├───────────────────────────────>│
     │                               │<───────────────────────────────┤
     │                               │                               │
     │                               │ Retorna sucesso               │
     │<──────────────────────────────┤                               │
     │                               │                               │
     │ Remove tokens do localStorage  │                               │
     │ Redireciona para /login       │                               │
     │                               │                               │
```

**Endpoint:** `POST /api/v1/auth/logout`

**Request:**
```json
{
  "refresh_token": "eyJhbGc..."
}
```

**Response:**
```json
{
  "message": "Logout realizado com sucesso"
}
```

---

### 5. Obter Usuário Atual

```
┌─────────┐                    ┌──────────┐
│ Frontend│                    │ Backend  │
└────┬────┘                    └────┬─────┘
     │                               │
     │ GET /auth/me                   │
     │ Authorization: Bearer <token>  │
     ├──────────────────────────────>│
     │                               │
     │                               │ Valida token
     │                               │ Busca usuário
     │                               │
     │                               │ Retorna dados do usuário
     │<──────────────────────────────┤
     │                               │
```

**Endpoint:** `GET /api/v1/auth/me`

**Response:**
```json
{
  "id": "uuid",
  "email": "usuario@example.com",
  "name": "Nome do Usuário",
  "role": "admin",
  "is_active": "Y",
  "created_at": "2025-01-01T00:00:00",
  "updated_at": "2025-01-01T00:00:00"
}
```

---

## 🔒 Segurança

### Proteção de Rotas

**Backend:**
```python
from app.core.security import get_current_user

@router.get("/protected")
async def protected_route(current_user: User = Depends(get_current_user)):
    # Rota protegida
    pass
```

**Frontend:**
```typescript
// Layout de rotas autenticadas
import { useAuth } from "@/hooks/use-auth"

export default function AuthLayout({ children }) {
  const { isAuthenticated } = useAuth(true) // requireAuth = true
  
  if (!isAuthenticated) {
    return null // Hook já redireciona
  }
  
  return <>{children}</>
}
```

### Proteção por Roles

**Backend:**
```python
from app.core.security import requires_role

@router.get("/admin")
@requires_role(["ADMIN", "MANAGER"])
async def admin_route(current_user: User = Depends(get_current_user)):
    # Rota protegida por role
    pass
```

---

## 🛠️ Implementação Técnica

### Backend

**Arquivos principais:**
- `app/core/security.py` - JWT, hash, validação
- `app/core/redis.py` - Gerenciamento de refresh tokens
- `app/services/auth_service.py` - Lógica de autenticação
- `app/api/v1/routers/auth.py` - Endpoints HTTP
- `app/repositories/user.py` - Acesso a dados

### Frontend

**Arquivos principais:**
- `frontend/services/auth.service.ts` - Serviço de autenticação
- `frontend/services/api.ts` - Interceptor Axios (refresh automático)
- `frontend/store/auth.store.ts` - Estado global (Zustand)
- `frontend/hooks/use-auth.ts` - Hook de autenticação
- `frontend/app/(auth)/layout.tsx` - Layout protegido

---

## 📝 Variáveis de Ambiente

**Backend (.env):**
```env
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=10
REFRESH_TOKEN_EXPIRE_DAYS=7
REDIS_URL=redis://localhost:6379/0
```

**Frontend (.env.local):**
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 🧪 Testes Manuais

### 1. Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "senha123"}'
```

### 2. Requisição Autenticada
```bash
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer <access_token>"
```

### 3. Refresh Token
```bash
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "<refresh_token>"}'
```

### 4. Logout
```bash
curl -X POST http://localhost:8000/api/v1/auth/logout \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "<refresh_token>"}'
```

---

## ⚠️ Tratamento de Erros

### Erros Comuns

1. **401 Unauthorized**
   - Token inválido ou expirado
   - Frontend tenta refresh automático
   - Se refresh falhar → logout

2. **403 Forbidden**
   - Usuário inativo
   - Role insuficiente
   - Frontend mostra mensagem de erro

3. **Refresh Token Inválido**
   - Token não está na whitelist (Redis)
   - Token expirado
   - Frontend faz logout automático

---

## 🔄 Fluxo Completo (Diagrama)

```
┌─────────────────────────────────────────────────────────────┐
│                        FLUXO COMPLETO                         │
└─────────────────────────────────────────────────────────────┘

1. Login
   Frontend → POST /auth/login → Backend
   Backend → Valida credenciais → Gera tokens → Salva no Redis
   Backend → Retorna tokens → Frontend salva no localStorage

2. Requisição Autenticada
   Frontend → GET /api/v1/... (com access_token) → Backend
   Backend → Valida token → Retorna dados

3. Token Expirado (401)
   Frontend → Interceptor detecta 401 → POST /auth/refresh
   Backend → Valida refresh_token (Redis) → Gera novo access_token
   Frontend → Salva novo token → Retenta requisição original

4. Logout
   Frontend → POST /auth/logout (com refresh_token) → Backend
   Backend → Remove refresh_token do Redis
   Frontend → Remove tokens do localStorage → Redireciona /login
```

---

**Última atualização:** 2025-12-03  
**Versão:** 1.0.0

