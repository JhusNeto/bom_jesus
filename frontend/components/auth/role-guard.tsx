"use client"

import { useAuthStore } from "@/store/auth.store"
import { hasRole, type UserRole } from "@/utils/permissions"

interface RoleGuardProps {
  /**
   * Roles permitidas para visualizar o conteúdo
   */
  allowedRoles: UserRole[]
  /**
   * Conteúdo a ser exibido se o usuário tiver permissão
   */
  children: React.ReactNode
  /**
   * Conteúdo alternativo se o usuário não tiver permissão
   * Se não fornecido, não renderiza nada
   */
  fallback?: React.ReactNode
  /**
   * Se true, verifica se o usuário está autenticado antes de verificar role
   */
  requireAuth?: boolean
}

/**
 * Componente que protege conteúdo baseado na role do usuário
 * 
 * @example
 * ```tsx
 * // Apenas admin pode ver
 * <RoleGuard allowedRoles={["admin"]}>
 *   <button>Configurações</button>
 * </RoleGuard>
 * 
 * // Admin ou manager podem ver
 * <RoleGuard allowedRoles={["admin", "manager"]}>
 *   <button>Aprovar</button>
 * </RoleGuard>
 * 
 * // Com fallback
 * <RoleGuard 
 *   allowedRoles={["admin"]}
 *   fallback={<p>Você não tem permissão</p>}
 * >
 *   <button>Deletar</button>
 * </RoleGuard>
 * ```
 */
export function RoleGuard({
  allowedRoles,
  children,
  fallback = null,
  requireAuth = true,
}: RoleGuardProps) {
  const { user, isAuthenticated } = useAuthStore()

  // Se requer autenticação e não está autenticado, não renderiza
  if (requireAuth && !isAuthenticated) {
    return <>{fallback}</>
  }

  // Se não tem usuário, não renderiza
  if (!user) {
    return <>{fallback}</>
  }

  // Verifica se o usuário tem uma das roles permitidas
  const hasAccess = hasRole(user.role, allowedRoles)

  if (hasAccess) {
    return <>{children}</>
  }

  return <>{fallback}</>
}

