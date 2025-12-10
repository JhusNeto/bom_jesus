"use client"

import { useAuthStore } from "@/store/auth.store"
import { hasPermission } from "@/utils/permissions"

interface PermissionGuardProps {
  /**
   * Recurso a ser verificado (ex: "USERS", "PEDIDOS")
   */
  resource: string
  /**
   * Ação a ser verificada (ex: "CREATE", "UPDATE", "DELETE")
   */
  action: string
  /**
   * Conteúdo a ser exibido se o usuário tiver permissão
   */
  children: React.ReactNode
  /**
   * Conteúdo alternativo se o usuário não tiver permissão
   */
  fallback?: React.ReactNode
  /**
   * Se true, verifica se o usuário está autenticado antes de verificar permissão
   */
  requireAuth?: boolean
}

/**
 * Componente que protege conteúdo baseado em permissões específicas
 * 
 * @example
 * ```tsx
 * // Verifica permissão específica
 * <PermissionGuard resource="USERS" action="CREATE">
 *   <button>Criar Usuário</button>
 * </PermissionGuard>
 * 
 * // Com fallback
 * <PermissionGuard 
 *   resource="PEDIDOS" 
 *   action="CANCEL"
 *   fallback={<p>Apenas gerentes podem cancelar</p>}
 * >
 *   <button>Cancelar Pedido</button>
 * </PermissionGuard>
 * ```
 */
export function PermissionGuard({
  resource,
  action,
  children,
  fallback = null,
  requireAuth = true,
}: PermissionGuardProps) {
  const { user, isAuthenticated } = useAuthStore()

  // Se requer autenticação e não está autenticado, não renderiza
  if (requireAuth && !isAuthenticated) {
    return <>{fallback}</>
  }

  // Verifica se o usuário tem a permissão específica
  const hasAccess = hasPermission(user?.role, resource as any, action)

  if (hasAccess) {
    return <>{children}</>
  }

  return <>{fallback}</>
}

