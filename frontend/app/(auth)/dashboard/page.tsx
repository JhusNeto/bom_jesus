"use client"

import { useAuthStore } from "@/store/auth.store"
import { usePermissions } from "@/hooks/use-permissions"
import { RoleGuard, PermissionGuard } from "@/components/auth"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { useQuery } from "@tanstack/react-query"
import api from "@/services/api"

export default function DashboardPage() {
  const { user } = useAuthStore()
  const { isAdmin, canEdit, canDelete, canManageUsers } = usePermissions()

  // Example API call using TanStack Query
  const { data: healthData, isLoading } = useQuery({
    queryKey: ["health"],
    queryFn: async () => {
      const response = await api.get("/health")
      return response.data
    },
    staleTime: 60000, // 1 minute
  })

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <p className="text-muted-foreground">
          Bem-vindo ao Sistema Operacional Bom Jesus
        </p>
      </div>

      {/* Welcome Card */}
      <Card>
        <CardHeader>
          <CardTitle>Bem-vindo, {user?.name || user?.email}!</CardTitle>
          <CardDescription>
            Este é o dashboard principal do sistema
          </CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            Aqui você terá acesso a todas as funcionalidades do sistema, incluindo
            módulos de pesagem, estoque e rotas.
          </p>
        </CardContent>
      </Card>

      {/* API Status Card */}
      <Card>
        <CardHeader>
          <CardTitle>Status da API</CardTitle>
          <CardDescription>
            Verificação de conexão com o backend
          </CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <p className="text-sm text-muted-foreground">Verificando...</p>
          ) : healthData ? (
            <div className="space-y-2">
              <p className="text-sm">
                <span className="font-medium">Status:</span>{" "}
                <span className="text-green-600">{healthData.status}</span>
              </p>
              <p className="text-sm">
                <span className="font-medium">Versão:</span> {healthData.version}
              </p>
              <p className="text-sm">
                <span className="font-medium">Ambiente:</span> {healthData.environment}
              </p>
            </div>
          ) : (
            <p className="text-sm text-destructive">
              Não foi possível conectar à API
            </p>
          )}
        </CardContent>
      </Card>

      {/* Permissões Card - Exemplo de uso */}
      <Card>
        <CardHeader>
          <CardTitle>Suas Permissões</CardTitle>
          <CardDescription>
            Exemplo de verificação de permissões por role
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <p className="text-sm">
              <span className="font-medium">Role:</span> {user?.role || "N/A"}
            </p>
            <div className="flex flex-wrap gap-2 mt-4">
              {isAdmin && (
                <span className="px-2 py-1 text-xs bg-red-100 text-red-800 rounded-full">
                  Administrador
                </span>
              )}
              {canEdit && (
                <span className="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded-full">
                  Pode Editar
                </span>
              )}
              {canDelete && (
                <span className="px-2 py-1 text-xs bg-orange-100 text-orange-800 rounded-full">
                  Pode Deletar
                </span>
              )}
              {canManageUsers && (
                <span className="px-2 py-1 text-xs bg-purple-100 text-purple-800 rounded-full">
                  Pode Gerenciar Usuários
                </span>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Exemplos de RoleGuard */}
      <Card>
        <CardHeader>
          <CardTitle>Exemplos de Proteção por Role</CardTitle>
          <CardDescription>
            Demonstração dos componentes RoleGuard e PermissionGuard
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {/* Exemplo 1: Apenas Admin */}
            <RoleGuard allowedRoles={["admin"]}>
              <div className="p-3 bg-green-50 border border-green-200 rounded">
                <p className="text-sm font-medium text-green-800">
                  ✅ Você é ADMIN - Este conteúdo só aparece para administradores
                </p>
                <Button size="sm" className="mt-2">
                  Configurações do Sistema
                </Button>
              </div>
            </RoleGuard>

            {/* Exemplo 2: Admin ou Manager */}
            <RoleGuard allowedRoles={["admin", "manager"]}>
              <div className="p-3 bg-blue-50 border border-blue-200 rounded">
                <p className="text-sm font-medium text-blue-800">
                  ✅ Você é ADMIN ou MANAGER - Pode aprovar ações
                </p>
                <Button size="sm" variant="outline" className="mt-2">
                  Aprovar Pedidos
                </Button>
              </div>
            </RoleGuard>

            {/* Exemplo 3: PermissionGuard */}
            <PermissionGuard resource="USERS" action="CREATE">
              <div className="p-3 bg-purple-50 border border-purple-200 rounded">
                <p className="text-sm font-medium text-purple-800">
                  ✅ Você tem permissão para criar usuários
                </p>
                <Button size="sm" variant="outline" className="mt-2">
                  Criar Novo Usuário
                </Button>
              </div>
            </PermissionGuard>
          </div>
        </CardContent>
      </Card>

      {/* Modules Placeholder */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle>Pesagem</CardTitle>
            <CardDescription>Módulo de pesagem</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              Em breve: funcionalidades de pesagem
            </p>
            <PermissionGuard resource="PESAGENS" action="CREATE" fallback={
              <p className="text-xs text-muted-foreground mt-2">
                Você não tem permissão para criar pesagens
              </p>
            }>
              <Button size="sm" className="mt-2">
                Nova Pesagem
              </Button>
            </PermissionGuard>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Estoque</CardTitle>
            <CardDescription>Módulo de estoque</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              Em breve: funcionalidades de estoque
            </p>
            <PermissionGuard resource="CARGAS" action="CREATE" fallback={
              <p className="text-xs text-muted-foreground mt-2">
                Você não tem permissão para criar cargas
              </p>
            }>
              <Button size="sm" className="mt-2">
                Nova Carga
              </Button>
            </PermissionGuard>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Rotas</CardTitle>
            <CardDescription>Módulo de rotas</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              Em breve: funcionalidades de rotas
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

