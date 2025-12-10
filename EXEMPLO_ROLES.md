# 🔐 Exemplo de Uso de Roles - Sistema Operacional Bom Jesus

**Como usar o sistema de roles para proteger endpoints**

---

## 📋 Endpoints de Exemplo

### 1. Endpoint que requer role ADMIN

**Endpoint:** `GET /api/v1/auth/admin-only`

**Proteção:** Apenas usuários com role `ADMIN` podem acessar

**Implementação:**
```python
@router.get("/admin-only", status_code=status.HTTP_200_OK)
@requires_role(["ADMIN"])
async def admin_only_endpoint(
    current_user: User = Depends(get_current_user)
):
    return {
        "message": "Acesso permitido - Você é um administrador",
        "user": {
            "email": current_user.email,
            "name": current_user.name,
            "role": current_user.role.value
        }
    }
```

**Teste:**
```bash
# 1. Fazer login como ADMIN
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@bomjesus.com", "password": "admin123"}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

# 2. Acessar endpoint (deve funcionar)
curl http://localhost:8000/api/v1/auth/admin-only \
  -H "Authorization: Bearer $TOKEN"

# Resposta esperada:
# {
#   "message": "Acesso permitido - Você é um administrador",
#   "user": { ... }
# }
```

---

### 2. Endpoint que requer role ADMIN ou MANAGER

**Endpoint:** `GET /api/v1/auth/manager-or-admin`

**Proteção:** Usuários com role `ADMIN` ou `MANAGER` podem acessar

**Implementação:**
```python
@router.get("/manager-or-admin", status_code=status.HTTP_200_OK)
@requires_role(["ADMIN", "MANAGER"])
async def manager_or_admin_endpoint(
    current_user: User = Depends(get_current_user)
):
    return {
        "message": "Acesso permitido - Você é um administrador ou gerente",
        "user": {
            "email": current_user.email,
            "name": current_user.name,
            "role": current_user.role.value
        }
    }
```

**Teste:**
```bash
# Com token de ADMIN (deve funcionar)
curl http://localhost:8000/api/v1/auth/manager-or-admin \
  -H "Authorization: Bearer $TOKEN"

# Resposta esperada:
# {
#   "message": "Acesso permitido - Você é um administrador ou gerente",
#   "user": { ... }
# }
```

---

## 🧪 Testando no Swagger UI

1. **Acesse:** http://localhost:8000/docs

2. **Faça login:**
   - Expanda: `POST /api/v1/auth/login`
   - Clique em "Try it out"
   - Preencha:
     ```json
     {
       "email": "admin@bomjesus.com",
       "password": "admin123"
     }
     ```
   - Clique em "Execute"
   - Copie o `access_token` retornado

3. **Autorize no Swagger:**
   - Clique no botão "Authorize" (canto superior direito)
   - Cole o `access_token` no campo "Value"
   - Clique em "Authorize"

4. **Teste os endpoints de roles:**
   - Expanda: `GET /api/v1/auth/admin-only`
   - Clique em "Try it out" → "Execute"
   - ✅ Deve retornar sucesso (200)

   - Expanda: `GET /api/v1/auth/manager-or-admin`
   - Clique em "Try it out" → "Execute"
   - ✅ Deve retornar sucesso (200)

---

## 🚫 Testando Acesso Negado

### Teste 1: Sem autenticação

```bash
curl http://localhost:8000/api/v1/auth/admin-only

# Resposta esperada:
# {"detail":"Could not validate credentials"}
# Status: 401 Unauthorized
```

### Teste 2: Com token inválido

```bash
curl http://localhost:8000/api/v1/auth/admin-only \
  -H "Authorization: Bearer token_invalido"

# Resposta esperada:
# {"detail":"Could not validate credentials"}
# Status: 401 Unauthorized
```

### Teste 3: Com role insuficiente

Se você criar um usuário com role `OPERATOR` ou `VIEWER` e tentar acessar `/admin-only`:

```bash
# Resposta esperada:
# {
#   "detail": "Required roles: ['ADMIN']. Your role: OPERATOR"
# }
# Status: 403 Forbidden
```

---

## 📝 Como Usar em Novos Endpoints

### Exemplo 1: Endpoint apenas para ADMIN

```python
from app.core.security import get_current_user, requires_role
from app.models.user import User

@router.get("/configuracoes-sistema")
@requires_role(["ADMIN"])
async def configuracoes_sistema(
    current_user: User = Depends(get_current_user)
):
    # Apenas ADMIN pode acessar
    return {"configuracoes": "..."}
```

### Exemplo 2: Endpoint para ADMIN ou MANAGER

```python
@router.post("/aprovar-pedido")
@requires_role(["ADMIN", "MANAGER"])
async def aprovar_pedido(
    pedido_id: str,
    current_user: User = Depends(get_current_user)
):
    # ADMIN ou MANAGER podem aprovar
    return {"message": "Pedido aprovado"}
```

### Exemplo 3: Endpoint para qualquer usuário autenticado

```python
@router.get("/meus-dados")
async def meus_dados(
    current_user: User = Depends(get_current_user)
):
    # Qualquer usuário autenticado pode acessar
    # Não precisa de @requires_role
    return {"dados": current_user}
```

---

## 🔍 Roles Disponíveis

- **ADMIN** - Administrador completo (acesso total)
- **MANAGER** - Gerente (acesso a gestão)
- **OPERATOR** - Operador (acesso operacional)
- **VIEWER** - Visualizador (somente leitura)

---

## ✅ Checklist de Implementação

Ao criar um novo endpoint protegido por role:

- [ ] Importar `requires_role` de `app.core.security`
- [ ] Importar `get_current_user` de `app.core.security`
- [ ] Adicionar `@requires_role(["ROLE1", "ROLE2"])` antes da função
- [ ] Adicionar `current_user: User = Depends(get_current_user)` nos parâmetros
- [ ] Testar no Swagger UI
- [ ] Testar com diferentes roles
- [ ] Documentar no Swagger (docstring)

---

**Última atualização:** 2025-12-06

