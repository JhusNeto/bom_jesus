"use client"

import { useAuthStore } from "@/store/auth.store"
import {
  hasPermission,
  hasRole,
  isAdmin,
  isManagerOrAdmin,
  canEdit,
  canDelete,
  canManageUsers,
  type UserRole,
} from "@/utils/permissions"

/**
 * Hook para verificar permissões do usuário atual
 * 
 * @example
 * ```tsx
 * const { isAdmin, canEdit, canDelete } = usePermissions()
 * 
 * return (
 *   <div>
 *     {canEdit && <button>Editar</button>}
 *     {canDelete && <button>Deletar</button>}
 *   </div>
 * )
 * ```
 */
export function usePermissions() {
  const { user } = useAuthStore()
  const userRole = user?.role

  return {
    // Roles específicas
    isAdmin: isAdmin(userRole),
    isManager: hasRole(userRole, ["manager"]),
    isOperator: hasRole(userRole, ["operator"]),
    isViewer: hasRole(userRole, ["viewer"]),

    // Permissões gerais
    canEdit: canEdit(userRole),
    canDelete: canDelete(userRole),
    canManageUsers: canManageUsers(userRole),
    isManagerOrAdmin: isManagerOrAdmin(userRole),

    // Função genérica para verificar permissões
    hasPermission: (resource: string, action: string) =>
      hasPermission(userRole, resource as any, action),

    // Role atual
    userRole: userRole as UserRole | undefined,
  }
}

