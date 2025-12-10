# 🔐 Sistema de Permissões - Sistema Operacional Bom Jesus

## Visão Geral

O sistema utiliza um modelo de **roles (papéis)** para controlar acesso a funcionalidades e recursos.

---

## 👥 Roles Disponíveis

### 1. ADMIN
**Nível:** Máximo  
**Descrição:** Acesso completo ao sistema

**Permissões:**
- ✅ Todas as funcionalidades
- ✅ Gerenciar usuários
- ✅ Configurações do sistema
- ✅ Relatórios completos
- ✅ Auditoria e logs

**Uso:** Administradores do sistema

---

### 2. MANAGER
**Nível:** Alto  
**Descrição:** Acesso gerencial com algumas restrições

**Permissões:**
- ✅ Visualizar e gerenciar operações
- ✅ Aprovar ações críticas
- ✅ Relatórios gerenciais
- ✅ Gerenciar clientes e pedidos
- ❌ Gerenciar usuários
- ❌ Configurações do sistema

**Uso:** Gerentes e supervisores

---

### 3. OPERATOR
**Nível:** Médio  
**Descrição:** Acesso operacional para trabalho diário

**Permissões:**
- ✅ Registrar cargas
- ✅ Registrar pesagens
- ✅ Registrar movimentações
- ✅ Registrar perdas
- ✅ Criar e atualizar pedidos
- ✅ Visualizar relatórios básicos
- ❌ Aprovar ações críticas
- ❌ Gerenciar usuários
- ❌ Configurações

**Uso:** Operadores e funcionários do dia a dia

---

### 4. VIEWER
**Nível:** Mínimo  
**Descrição:** Acesso somente leitura

**Permissões:**
- ✅ Visualizar dados
- ✅ Visualizar relatórios
- ✅ Exportar dados
- ❌ Criar/editar/deletar
- ❌ Ações operacionais

**Uso:** Consultores, auditores, visualizadores

---

## 🛡️ Implementação

### Backend - Decorador de Roles

```python
from app.core.security import requires_role, get_current_user

@router.get("/admin-only")
@requires_role(["ADMIN"])
async def admin_route(current_user: User = Depends(get_current_user)):
    # Apenas ADMIN pode acessar
    pass

@router.get("/manager-or-admin")
@requires_role(["ADMIN", "MANAGER"])
async def manager_route(current_user: User = Depends(get_current_user)):
    # ADMIN ou MANAGER podem acessar
    pass
```

### Verificação de Role

```python
from app.models.user import UserRole

# Verificar role no código
if current_user.role == UserRole.ADMIN:
    # Lógica para admin
    pass
```

### Frontend - Verificação de Permissões

```typescript
import { useAuthStore } from "@/store/auth.store"

function MyComponent() {
  const { user } = useAuthStore()
  
  const canEdit = user?.role === "admin" || user?.role === "manager"
  const isAdmin = user?.role === "admin"
  
  return (
    <div>
      {canEdit && <button>Editar</button>}
      {isAdmin && <button>Configurações</button>}
    </div>
  )
}
```

---

## 📋 Matriz de Permissões

| Funcionalidade | ADMIN | MANAGER | OPERATOR | VIEWER |
|----------------|-------|---------|----------|--------|
| **Usuários** |
| Criar usuário | ✅ | ❌ | ❌ | ❌ |
| Editar usuário | ✅ | ❌ | ❌ | ❌ |
| Deletar usuário | ✅ | ❌ | ❌ | ❌ |
| Listar usuários | ✅ | ✅ | ❌ | ❌ |
| **Cargas** |
| Criar carga | ✅ | ✅ | ✅ | ❌ |
| Editar carga | ✅ | ✅ | ✅ | ❌ |
| Deletar carga | ✅ | ✅ | ❌ | ❌ |
| Visualizar cargas | ✅ | ✅ | ✅ | ✅ |
| **Pedidos** |
| Criar pedido | ✅ | ✅ | ✅ | ❌ |
| Editar pedido | ✅ | ✅ | ✅ | ❌ |
| Cancelar pedido | ✅ | ✅ | ❌ | ❌ |
| Visualizar pedidos | ✅ | ✅ | ✅ | ✅ |
| **Pesagens** |
| Registrar pesagem | ✅ | ✅ | ✅ | ❌ |
| Editar pesagem | ✅ | ✅ | ✅ | ❌ |
| Visualizar pesagens | ✅ | ✅ | ✅ | ✅ |
| **Relatórios** |
| Relatórios básicos | ✅ | ✅ | ✅ | ✅ |
| Relatórios gerenciais | ✅ | ✅ | ❌ | ❌ |
| Relatórios completos | ✅ | ❌ | ❌ | ❌ |
| **Configurações** |
| Configurações do sistema | ✅ | ❌ | ❌ | ❌ |
| Auditoria e logs | ✅ | ✅ | ❌ | ❌ |

---

## 🔒 Proteção de Rotas por Role

### Exemplo: Rota Admin

```python
@router.delete("/users/{user_id}")
@requires_role(["ADMIN"])
async def delete_user(
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Apenas ADMIN pode deletar usuários
    user_repo = UserRepository(db)
    user_repo.delete(user_id)
    return {"message": "Usuário deletado"}
```

### Exemplo: Rota Manager ou Admin

```python
@router.get("/reports/manager")
@requires_role(["ADMIN", "MANAGER"])
async def manager_report(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # ADMIN ou MANAGER podem acessar
    # Lógica do relatório gerencial
    pass
```

---

## 🎯 Boas Práticas

### 1. Princípio do Menor Privilégio
- Atribua a role mínima necessária
- VIEWER por padrão para novos usuários

### 2. Verificação Dupla
- Backend: Sempre verificar role no endpoint
- Frontend: Ocultar/mostrar UI baseado em role

### 3. Auditoria
- Registrar ações sensíveis no `LogOperacional`
- Incluir role do usuário nos logs

### 4. Testes
- Testar cada role isoladamente
- Verificar que roles inferiores não acessam recursos superiores

---

## 📝 Exemplos de Uso

### Backend - Service com Verificação de Role

```python
class PedidoService:
    def cancelar_pedido(self, pedido_id: UUID, user: User):
        # Verifica permissão
        if user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
            raise HTTPException(
                status_code=403,
                detail="Apenas ADMIN ou MANAGER podem cancelar pedidos"
            )
        
        # Lógica de cancelamento
        pedido = self.pedido_repo.get(pedido_id)
        pedido.status = StatusPedido.CANCELADO
        self.pedido_repo.update(pedido_id, {"status": pedido.status})
```

### Frontend - Componente Condicional

```typescript
import { useAuthStore } from "@/store/auth.store"

export function PedidoActions({ pedido }) {
  const { user } = useAuthStore()
  const canCancel = user?.role === "admin" || user?.role === "manager"
  const canEdit = user?.role !== "viewer"
  
  return (
    <div>
      {canEdit && <button>Editar</button>}
      {canCancel && <button>Cancelar</button>}
      <button>Visualizar</button>
    </div>
  )
}
```

---

## 🔄 Atualização de Roles

### Como Alterar Role de um Usuário

**Apenas ADMIN pode alterar roles:**

```python
@router.patch("/users/{user_id}/role")
@requires_role(["ADMIN"])
async def update_user_role(
    user_id: UUID,
    new_role: UserRole,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_repo = UserRepository(db)
    user = user_repo.get(user_id)
    if not user:
        raise HTTPException(404, "Usuário não encontrado")
    
    user.role = new_role
    user_repo.update(user_id, {"role": new_role})
    return {"message": "Role atualizada"}
```

---

## ⚠️ Segurança

### Importante

1. **Nunca confie apenas no frontend**
   - Backend sempre valida role
   - Frontend apenas para UX (ocultar/mostrar)

2. **Tokens não contêm permissões dinâmicas**
   - Role vem do banco de dados
   - Token apenas identifica usuário

3. **Refresh token não renova permissões**
   - Se role mudar, usuário precisa fazer login novamente
   - Ou implementar invalidação de tokens

4. **Logs de auditoria**
   - Registrar todas as ações sensíveis
   - Incluir role do usuário

---

## 📊 Hierarquia de Roles

```
ADMIN (Máximo)
  │
  ├── MANAGER (Alto)
  │     │
  │     ├── OPERATOR (Médio)
  │     │     │
  │     │     └── VIEWER (Mínimo)
  │     │
  │     └── VIEWER (Mínimo)
  │
  └── OPERATOR (Médio)
        │
        └── VIEWER (Mínimo)
```

**Regra:** Roles superiores herdam permissões de roles inferiores (exceto VIEWER que é somente leitura).

---

**Última atualização:** 2025-12-03  
**Versão:** 1.0.0

