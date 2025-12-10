/**
 * Utilitário de Permissões - Sistema Operacional Bom Jesus
 * Centraliza a lógica de verificação de permissões por role
 */

export type UserRole = "admin" | "manager" | "operator" | "viewer"

/**
 * Matriz de permissões por recurso e ação
 * Baseado na documentação PERMISSOES.md
 */
export const PERMISSIONS = {
  USERS: {
    CREATE: ["admin"] as UserRole[],
    UPDATE: ["admin"] as UserRole[],
    DELETE: ["admin"] as UserRole[],
    LIST: ["admin", "manager"] as UserRole[],
  },
  CARGAS: {
    CREATE: ["admin", "manager", "operator"] as UserRole[],
    UPDATE: ["admin", "manager", "operator"] as UserRole[],
    DELETE: ["admin", "manager"] as UserRole[],
    VIEW: ["admin", "manager", "operator", "viewer"] as UserRole[],
  },
  PEDIDOS: {
    CREATE: ["admin", "manager", "operator"] as UserRole[],
    UPDATE: ["admin", "manager", "operator"] as UserRole[],
    DELETE: ["admin", "manager"] as UserRole[],
    CANCEL: ["admin", "manager"] as UserRole[],
    VIEW: ["admin", "manager", "operator", "viewer"] as UserRole[],
  },
  PESAGENS: {
    CREATE: ["admin", "manager", "operator"] as UserRole[],
    UPDATE: ["admin", "manager", "operator"] as UserRole[],
    DELETE: ["admin", "manager"] as UserRole[],
    VIEW: ["admin", "manager", "operator", "viewer"] as UserRole[],
  },
  RELATORIOS: {
    BASICOS: ["admin", "manager", "operator", "viewer"] as UserRole[],
    GERENCIAIS: ["admin", "manager"] as UserRole[],
    COMPLETOS: ["admin"] as UserRole[],
  },
  CONFIGURACOES: {
    VIEW: ["admin"] as UserRole[],
    UPDATE: ["admin"] as UserRole[],
  },
  AUDITORIA: {
    VIEW: ["admin", "manager"] as UserRole[],
  },
} as const

/**
 * Verifica se um usuário tem permissão para uma ação específica
 * 
 * @param userRole - Role do usuário
 * @param resource - Recurso (ex: "USERS", "PEDIDOS")
 * @param action - Ação (ex: "CREATE", "UPDATE")
 * @returns true se o usuário tem permissão
 */
export function hasPermission(
  userRole: string | undefined | null,
  resource: keyof typeof PERMISSIONS,
  action: string
): boolean {
  if (!userRole) return false

  const normalizedRole = userRole.toLowerCase() as UserRole
  const resourcePermissions = PERMISSIONS[resource]
  
  if (!resourcePermissions) return false
  
  const allowedRoles = (resourcePermissions as any)[action] as UserRole[] | undefined

  if (!allowedRoles || !Array.isArray(allowedRoles)) return false

  return allowedRoles.includes(normalizedRole)
}

/**
 * Verifica se o usuário tem uma role específica
 */
export function hasRole(userRole: string | undefined | null, roles: UserRole[]): boolean {
  if (!userRole) return false
  return roles.includes(userRole.toLowerCase() as UserRole)
}

/**
 * Verifica se o usuário é admin
 */
export function isAdmin(userRole: string | undefined | null): boolean {
  return hasRole(userRole, ["admin"])
}

/**
 * Verifica se o usuário é manager ou admin
 */
export function isManagerOrAdmin(userRole: string | undefined | null): boolean {
  return hasRole(userRole, ["admin", "manager"])
}

/**
 * Verifica se o usuário pode editar (não é viewer)
 */
export function canEdit(userRole: string | undefined | null): boolean {
  return hasRole(userRole, ["admin", "manager", "operator"])
}

/**
 * Verifica se o usuário pode deletar (admin ou manager)
 */
export function canDelete(userRole: string | undefined | null): boolean {
  return hasRole(userRole, ["admin", "manager"])
}

/**
 * Verifica se o usuário pode gerenciar usuários (apenas admin)
 */
export function canManageUsers(userRole: string | undefined | null): boolean {
  return isAdmin(userRole)
}

