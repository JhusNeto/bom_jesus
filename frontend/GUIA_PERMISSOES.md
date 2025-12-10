# 🔐 Guia de Uso - Sistema de Permissões no Frontend

**Como usar os utilitários de permissões e autorização no frontend**

---

## 📋 Componentes Criados

### 1. `usePermissions()` - Hook de Permissões

Hook React que fornece verificações de permissões baseadas na role do usuário.

**Localização:** `frontend/hooks/use-permissions.ts`

**Uso:**
```tsx
import { usePermissions } from "@/hooks/use-permissions"

function MyComponent() {
  const { isAdmin, canEdit, canDelete, canManageUsers, hasPermission } = usePermissions()

  return (
    <div>
      {isAdmin && <button>Configurações</button>}
      {canEdit && <button>Editar</button>}
      {canDelete && <button>Deletar</button>}
      {canManageUsers && <button>Gerenciar Usuários</button>}
      
      {hasPermission("PEDIDOS", "CANCEL") && (
        <button>Cancelar Pedido</button>
      )}
    </div>
  )
}
```

**Propriedades disponíveis:**
- `isAdmin` - true se role é "admin"
- `isManager` - true se role é "manager"
- `isOperator` - true se role é "operator"
- `isViewer` - true se role é "viewer"
- `canEdit` - true se não é viewer
- `canDelete` - true se é admin ou manager
- `canManageUsers` - true se é admin
- `isManagerOrAdmin` - true se é admin ou manager
- `hasPermission(resource, action)` - verifica permissão específica
- `userRole` - role atual do usuário

---

### 2. `RoleGuard` - Componente de Proteção por Role

Componente que renderiza conteúdo apenas se o usuário tiver uma das roles permitidas.

**Localização:** `frontend/components/auth/role-guard.tsx`

**Uso:**
```tsx
import { RoleGuard } from "@/components/auth"

// Apenas admin pode ver
<RoleGuard allowedRoles={["admin"]}>
  <button>Configurações do Sistema</button>
</RoleGuard>

// Admin ou manager podem ver
<RoleGuard allowedRoles={["admin", "manager"]}>
  <button>Aprovar Pedido</button>
</RoleGuard>

// Com fallback (mensagem alternativa)
<RoleGuard 
  allowedRoles={["admin"]}
  fallback={<p>Você não tem permissão para acessar isso</p>}
>
  <button>Deletar Usuário</button>
</RoleGuard>
```

**Props:**
- `allowedRoles: UserRole[]` - Array de roles permitidas
- `children: React.ReactNode` - Conteúdo a ser exibido se tiver permissão
- `fallback?: React.ReactNode` - Conteúdo alternativo se não tiver permissão
- `requireAuth?: boolean` - Se true, verifica autenticação antes (padrão: true)

---

### 3. `PermissionGuard` - Componente de Proteção por Permissão

Componente que renderiza conteúdo baseado em permissões específicas (recurso + ação).

**Localização:** `frontend/components/auth/permission-guard.tsx`

**Uso:**
```tsx
import { PermissionGuard } from "@/components/auth"

// Verifica permissão específica
<PermissionGuard resource="USERS" action="CREATE">
  <button>Criar Usuário</button>
</PermissionGuard>

// Com fallback
<PermissionGuard 
  resource="PEDIDOS" 
  action="CANCEL"
  fallback={<p>Apenas gerentes podem cancelar pedidos</p>}
>
  <button>Cancelar Pedido</button>
</PermissionGuard>
```

**Props:**
- `resource: string` - Recurso (ex: "USERS", "PEDIDOS", "CARGAS")
- `action: string` - Ação (ex: "CREATE", "UPDATE", "DELETE", "CANCEL")
- `children: React.ReactNode` - Conteúdo a ser exibido se tiver permissão
- `fallback?: React.ReactNode` - Conteúdo alternativo
- `requireAuth?: boolean` - Se true, verifica autenticação antes (padrão: true)

---

### 4. `permissions.ts` - Utilitário de Permissões

Utilitário centralizado com matriz de permissões e funções de verificação.

**Localização:** `frontend/utils/permissions.ts`

**Uso:**
```tsx
import { hasPermission, isAdmin, canEdit, PERMISSIONS } from "@/utils/permissions"

// Verificar permissão específica
if (hasPermission(user.role, "USERS", "CREATE")) {
  // Criar usuário
}

// Verificações rápidas
if (isAdmin(user.role)) {
  // Lógica para admin
}

if (canEdit(user.role)) {
  // Lógica para edição
}

// Acessar matriz de permissões
const allowedRoles = PERMISSIONS.PEDIDOS.CANCEL
// ["admin", "manager"]
```

**Funções disponíveis:**
- `hasPermission(userRole, resource, action)` - Verifica permissão específica
- `hasRole(userRole, roles)` - Verifica se tem uma das roles
- `isAdmin(userRole)` - Verifica se é admin
- `isManagerOrAdmin(userRole)` - Verifica se é manager ou admin
- `canEdit(userRole)` - Verifica se pode editar (não é viewer)
- `canDelete(userRole)` - Verifica se pode deletar
- `canManageUsers(userRole)` - Verifica se pode gerenciar usuários

---

## 📝 Exemplos Práticos

### Exemplo 1: Botões Condicionais

```tsx
import { usePermissions } from "@/hooks/use-permissions"
import { Button } from "@/components/ui/button"

function PedidoActions({ pedido }) {
  const { canEdit, canDelete, hasPermission } = usePermissions()

  return (
    <div className="flex gap-2">
      <Button>Visualizar</Button>
      
      {canEdit && (
        <Button variant="outline">Editar</Button>
      )}
      
      {canDelete && (
        <Button variant="destructive">Deletar</Button>
      )}
      
      {hasPermission("PEDIDOS", "CANCEL") && (
        <Button variant="outline">Cancelar</Button>
      )}
    </div>
  )
}
```

### Exemplo 2: Menu Condicional

```tsx
import { RoleGuard } from "@/components/auth"
import Link from "next/link"

function Navigation() {
  return (
    <nav>
      <Link href="/dashboard">Dashboard</Link>
      <Link href="/pedidos">Pedidos</Link>
      
      <RoleGuard allowedRoles={["admin", "manager"]}>
        <Link href="/relatorios">Relatórios</Link>
      </RoleGuard>
      
      <RoleGuard allowedRoles={["admin"]}>
        <Link href="/usuarios">Usuários</Link>
        <Link href="/configuracoes">Configurações</Link>
      </RoleGuard>
    </nav>
  )
}
```

### Exemplo 3: Formulário com Campos Condicionais

```tsx
import { PermissionGuard } from "@/components/auth"

function PedidoForm() {
  return (
    <form>
      <input name="cliente" placeholder="Cliente" />
      <input name="quantidade" placeholder="Quantidade" />
      
      <PermissionGuard resource="PEDIDOS" action="CANCEL">
        <label>
          <input type="checkbox" name="urgente" />
          Marcar como urgente
        </label>
      </PermissionGuard>
      
      <PermissionGuard resource="PEDIDOS" action="UPDATE">
        <button type="submit">Salvar</button>
      </PermissionGuard>
    </form>
  )
}
```

### Exemplo 4: Card com Ações Condicionais

```tsx
import { usePermissions } from "@/hooks/use-permissions"
import { RoleGuard } from "@/components/auth"

function PedidoCard({ pedido }) {
  const { canEdit, canDelete } = usePermissions()

  return (
    <Card>
      <CardHeader>
        <CardTitle>Pedido #{pedido.id}</CardTitle>
      </CardHeader>
      <CardContent>
        <p>Cliente: {pedido.cliente}</p>
        <p>Status: {pedido.status}</p>
        
        <div className="flex gap-2 mt-4">
          <Button size="sm">Ver Detalhes</Button>
          
          {canEdit && (
            <Button size="sm" variant="outline">Editar</Button>
          )}
          
          <RoleGuard allowedRoles={["admin", "manager"]}>
            <Button size="sm" variant="destructive">Cancelar</Button>
          </RoleGuard>
          
          {canDelete && (
            <Button size="sm" variant="destructive">Deletar</Button>
          )}
        </div>
      </CardContent>
    </Card>
  )
}
```

---

## 🎯 Recursos e Ações Disponíveis

### USERS
- `CREATE` - Criar usuário (apenas admin)
- `UPDATE` - Editar usuário (apenas admin)
- `DELETE` - Deletar usuário (apenas admin)
- `LIST` - Listar usuários (admin, manager)

### CARGAS
- `CREATE` - Criar carga (admin, manager, operator)
- `UPDATE` - Editar carga (admin, manager, operator)
- `DELETE` - Deletar carga (admin, manager)
- `VIEW` - Visualizar cargas (todos)

### PEDIDOS
- `CREATE` - Criar pedido (admin, manager, operator)
- `UPDATE` - Editar pedido (admin, manager, operator)
- `DELETE` - Deletar pedido (admin, manager)
- `CANCEL` - Cancelar pedido (admin, manager)
- `VIEW` - Visualizar pedidos (todos)

### PESAGENS
- `CREATE` - Registrar pesagem (admin, manager, operator)
- `UPDATE` - Editar pesagem (admin, manager, operator)
- `DELETE` - Deletar pesagem (admin, manager)
- `VIEW` - Visualizar pesagens (todos)

### RELATORIOS
- `BASICOS` - Relatórios básicos (todos)
- `GERENCIAIS` - Relatórios gerenciais (admin, manager)
- `COMPLETOS` - Relatórios completos (apenas admin)

### CONFIGURACOES
- `VIEW` - Ver configurações (apenas admin)
- `UPDATE` - Atualizar configurações (apenas admin)

### AUDITORIA
- `VIEW` - Ver auditoria e logs (admin, manager)

---

## ⚠️ Importante

### Segurança

1. **Backend sempre valida**
   - O frontend apenas melhora a UX (oculta/mostra)
   - O backend sempre valida permissões
   - Nunca confie apenas no frontend

2. **Tokens não contêm permissões**
   - Role vem do banco de dados via `/auth/me`
   - Token apenas identifica o usuário
   - Permissões são verificadas no backend

3. **Atualização de permissões**
   - Se role mudar, usuário precisa fazer login novamente
   - Ou usar `refreshUser()` para atualizar dados

---

## 📚 Referências

- **Backend:** `app/core/security.py` - Decorator `@requires_role()`
- **Documentação:** `PERMISSOES.md` - Matriz completa de permissões
- **Exemplos:** `EXEMPLO_ROLES.md` - Exemplos de uso no backend

---

**Última atualização:** 2025-12-06

