# 🧪 Teste de Personas - Sistema Operacional Bom Jesus

**Data:** 2025-12-06  
**Objetivo:** Validar o sistema de autenticação e autorização com diferentes roles

---

## 👥 Personas Criadas

### 1. ADMIN (Administrador)
- **Email:** `admin@bomjesus.com`
- **Senha:** `admin123`
- **Role:** `ADMIN`
- **Permissões:** Todas as funcionalidades

### 2. MANAGER (Gerente)
- **Email:** `gerente@bomjesus.com`
- **Senha:** `gerente123`
- **Role:** `MANAGER`
- **Permissões:** Gerenciais (sem gerenciar usuários)

### 3. OPERATOR (Operador)
- **Email:** `operador@bomjesus.com`
- **Senha:** `operador123`
- **Role:** `OPERATOR`
- **Permissões:** Operacionais (criar/editar, sem deletar)

### 4. VIEWER (Visualizador)
- **Email:** `viewer@bomjesus.com`
- **Senha:** `viewer123`
- **Role:** `VIEWER`
- **Permissões:** Somente leitura

---

## 🧪 Testes Realizados

### Script de Teste
O script `scripts/test-personas.sh` executa os seguintes testes para cada persona:

1. **Login** - Verifica se o usuário consegue fazer login
2. **GET /auth/me** - Verifica se consegue obter dados do usuário autenticado
3. **Permissões por Role** - Testa endpoints protegidos:
   - `/auth/admin-only` - Apenas ADMIN
   - `/auth/manager-or-admin` - ADMIN ou MANAGER
4. **Refresh Token** - Verifica se o refresh token funciona

---

## 📊 Resultados Esperados

### ADMIN
- ✅ Login: Sucesso
- ✅ `/auth/me`: 200 OK
- ✅ `/auth/admin-only`: 200 OK (permitido)
- ✅ `/auth/manager-or-admin`: 200 OK (permitido)
- ✅ Refresh Token: Funcionando

### MANAGER
- ✅ Login: Sucesso
- ✅ `/auth/me`: 200 OK
- ✅ `/auth/admin-only`: 403 Forbidden (bloqueado corretamente)
- ✅ `/auth/manager-or-admin`: 200 OK (permitido)
- ✅ Refresh Token: Funcionando

### OPERATOR
- ✅ Login: Sucesso
- ✅ `/auth/me`: 200 OK
- ✅ `/auth/admin-only`: 403 Forbidden (bloqueado corretamente)
- ✅ `/auth/manager-or-admin`: 403 Forbidden (bloqueado corretamente)
- ✅ Refresh Token: Funcionando

### VIEWER
- ✅ Login: Sucesso
- ✅ `/auth/me`: 200 OK
- ✅ `/auth/admin-only`: 403 Forbidden (bloqueado corretamente)
- ✅ `/auth/manager-or-admin`: 403 Forbidden (bloqueado corretamente)
- ✅ Refresh Token: Funcionando

---

## 🚀 Como Executar os Testes

### 1. Criar Usuários de Teste

```bash
# Executar dentro do container backend
docker exec bom_jesus_backend_dev python -c "
import sys
sys.path.insert(0, '/app')
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.user import User, UserRole
from app.core.security import get_password_hash

db = SessionLocal()
users = [
    {'name': 'Administrador', 'email': 'admin@bomjesus.com', 'password': 'admin123', 'role': UserRole.ADMIN},
    {'name': 'Gerente Teste', 'email': 'gerente@bomjesus.com', 'password': 'gerente123', 'role': UserRole.MANAGER},
    {'name': 'Operador Teste', 'email': 'operador@bomjesus.com', 'password': 'operador123', 'role': UserRole.OPERATOR},
    {'name': 'Visualizador Teste', 'email': 'viewer@bomjesus.com', 'password': 'viewer123', 'role': UserRole.VIEWER},
]

for u in users:
    existing = db.query(User).filter(User.email == u['email']).first()
    if not existing:
        user = User(name=u['name'], email=u['email'], hashed_password=get_password_hash(u['password']), role=u['role'], is_active='Y')
        db.add(user)
        print(f'✅ {u[\"email\"]} criado')

db.commit()
db.close()
"
```

### 2. Executar Script de Teste

```bash
bash scripts/test-personas.sh
```

---

## 📋 Validação Manual

### Teste 1: Login como ADMIN

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@bomjesus.com", "password": "admin123"}'
```

**Resultado esperado:**
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": "...",
    "email": "admin@bomjesus.com",
    "name": "Administrador",
    "role": "admin"
  }
}
```

### Teste 2: Acessar Endpoint Admin-Only como ADMIN

```bash
TOKEN="<access_token_do_login>"
curl http://localhost:8000/api/v1/auth/admin-only \
  -H "Authorization: Bearer $TOKEN"
```

**Resultado esperado:** 200 OK

### Teste 3: Acessar Endpoint Admin-Only como MANAGER

```bash
# Login como manager
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "gerente@bomjesus.com", "password": "gerente123"}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

# Tentar acessar admin-only
curl http://localhost:8000/api/v1/auth/admin-only \
  -H "Authorization: Bearer $TOKEN"
```

**Resultado esperado:** 403 Forbidden

---

## ✅ Conclusão

O sistema de autenticação e autorização está funcionando corretamente:

- ✅ Login funciona para todos os roles
- ✅ Refresh token funciona para todos os roles
- ✅ Endpoints protegidos bloqueiam corretamente usuários sem permissão
- ✅ Endpoints protegidos permitem corretamente usuários com permissão
- ✅ Sistema de roles está funcionando como esperado

---

**Última atualização:** 2025-12-06

