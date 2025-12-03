"use client"

import { useAuthStore } from "@/store/auth.store"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { useQuery } from "@tanstack/react-query"
import api from "@/services/api"

export default function DashboardPage() {
  const { user } = useAuthStore()

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

