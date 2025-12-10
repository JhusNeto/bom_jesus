"use client"

import { useQuery } from "@tanstack/react-query"
import { auditService } from "@/services/audit.service"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { TipoLog } from "@/types/audit"
import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { useAuthStore } from "@/store/auth.store"

const tipoBadgeColors: Record<TipoLog, string> = {
  [TipoLog.LOGIN]: "bg-blue-500",
  [TipoLog.CARREGAMENTO]: "bg-green-500",
  [TipoLog.ATUALIZACAO]: "bg-yellow-500",
  [TipoLog.PESAGEM]: "bg-purple-500",
  [TipoLog.MOVIMENTACAO]: "bg-orange-500",
  [TipoLog.DEVOLUCAO]: "bg-red-500",
  [TipoLog.OUTRO]: "bg-gray-500",
}

export default function AuditPage() {
  const [refreshing, setRefreshing] = useState(false)
  const router = useRouter()
  const { user, isAuthenticated, isLoading: authLoading } = useAuthStore()

  // Verificar permissão de acesso (apenas ADMIN ou MANAGER)
  useEffect(() => {
    if (!authLoading && isAuthenticated && user) {
      const userRole = user.role?.toLowerCase()
      if (userRole !== "admin" && userRole !== "manager") {
        // Redireciona para dashboard se não tiver permissão
        router.push("/dashboard")
      }
    }
  }, [authLoading, isAuthenticated, user, router])

  const { data: dashboard, isLoading, error, refetch } = useQuery({
    queryKey: ["audit-dashboard"],
    queryFn: () => auditService.getDashboard(),
    staleTime: 30000, // 30 segundos
    enabled: isAuthenticated && (user?.role?.toLowerCase() === "admin" || user?.role?.toLowerCase() === "manager"),
  })

  const handleRefresh = async () => {
    setRefreshing(true)
    await refetch()
    setTimeout(() => setRefreshing(false), 500)
  }

  // Mostrar loading enquanto verifica autenticação ou carrega dados
  if (authLoading || isLoading) {
    return (
      <div className="container mx-auto p-6">
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 mx-auto mb-4"></div>
            <p className="text-gray-600">Carregando painel de auditoria...</p>
          </div>
        </div>
      </div>
    )
  }

  // Verificar se tem permissão antes de renderizar
  const userRole = user?.role?.toLowerCase()
  if (!isAuthenticated || (userRole !== "admin" && userRole !== "manager")) {
    return null // O useEffect já redirecionou
  }

  if (error) {
    return (
      <div className="container mx-auto p-6">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <h3 className="text-red-800 font-semibold mb-2">Erro ao carregar dados</h3>
          <p className="text-red-600">
            {error instanceof Error ? error.message : "Erro desconhecido"}
          </p>
          <Button onClick={handleRefresh} className="mt-4">
            Tentar novamente
          </Button>
        </div>
      </div>
    )
  }

  if (!dashboard) {
    return null
  }

  const { resumo, logs_por_dia, tipos_mais_comuns } = dashboard

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">🔍 Painel de Auditoria</h1>
          <p className="text-gray-600 mt-1">Sistema Operacional Bom Jesus</p>
        </div>
        <Button onClick={handleRefresh} disabled={refreshing}>
          {refreshing ? "Atualizando..." : "🔄 Atualizar"}
        </Button>
      </div>

      {/* Cards de Estatísticas */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="p-6">
          <h3 className="text-sm font-medium text-gray-500 uppercase mb-2">Total de Logs</h3>
          <p className="text-3xl font-bold text-gray-900">{resumo.total_logs}</p>
        </Card>
        <Card className="p-6">
          <h3 className="text-sm font-medium text-gray-500 uppercase mb-2">Logs Hoje</h3>
          <p className="text-3xl font-bold text-blue-600">{resumo.logs_hoje}</p>
        </Card>
        <Card className="p-6">
          <h3 className="text-sm font-medium text-gray-500 uppercase mb-2">Últimos 7 Dias</h3>
          <p className="text-3xl font-bold text-green-600">{resumo.logs_ultimos_7_dias}</p>
        </Card>
        <Card className="p-6">
          <h3 className="text-sm font-medium text-gray-500 uppercase mb-2">Últimos 30 Dias</h3>
          <p className="text-3xl font-bold text-purple-600">{resumo.logs_ultimos_30_dias}</p>
        </Card>
      </div>

      {/* Logs por Tipo */}
      <Card className="p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">📊 Logs por Tipo</h2>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b">
                <th className="text-left py-3 px-4 font-semibold text-gray-700">Tipo</th>
                <th className="text-right py-3 px-4 font-semibold text-gray-700">Total</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(resumo.logs_por_tipo).map(([tipo, count]) => (
                <tr key={tipo} className="border-b hover:bg-gray-50">
                  <td className="py-3 px-4">
                    <span
                      className={`inline-block px-3 py-1 rounded-full text-white text-sm font-medium ${
                        tipoBadgeColors[tipo as TipoLog] || "bg-gray-500"
                      }`}
                    >
                      {tipo.toUpperCase()}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-right font-semibold">{count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Top Usuários */}
      {resumo.top_usuarios.length > 0 && (
        <Card className="p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">👥 Top Usuários (Últimos 30 Dias)</h2>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-3 px-4 font-semibold text-gray-700">Usuário</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-700">Email</th>
                  <th className="text-right py-3 px-4 font-semibold text-gray-700">Total de Logs</th>
                </tr>
              </thead>
              <tbody>
                {resumo.top_usuarios.map((usuario) => (
                  <tr key={usuario.usuario_id} className="border-b hover:bg-gray-50">
                    <td className="py-3 px-4 font-medium">{usuario.usuario_nome}</td>
                    <td className="py-3 px-4 text-gray-600">{usuario.usuario_email || "N/A"}</td>
                    <td className="py-3 px-4 text-right font-semibold">{usuario.total_logs}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}

      {/* Logs Recentes */}
      <Card className="p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">📝 Logs Recentes</h2>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b">
                <th className="text-left py-3 px-4 font-semibold text-gray-700">Data/Hora</th>
                <th className="text-left py-3 px-4 font-semibold text-gray-700">Tipo</th>
                <th className="text-left py-3 px-4 font-semibold text-gray-700">Usuário</th>
                <th className="text-left py-3 px-4 font-semibold text-gray-700">Detalhes</th>
              </tr>
            </thead>
            <tbody>
              {resumo.logs_recentes.slice(0, 20).map((log) => {
                let detalhes: any = {}
                try {
                  detalhes = log.detalhes ? JSON.parse(log.detalhes) : {}
                } catch {
                  detalhes = {}
                }

                const dataFormatada = new Date(log.data).toLocaleString("pt-BR", {
                  day: "2-digit",
                  month: "2-digit",
                  year: "numeric",
                  hour: "2-digit",
                  minute: "2-digit",
                })

                return (
                  <tr key={log.id} className="border-b hover:bg-gray-50">
                    <td className="py-3 px-4 text-sm">{dataFormatada}</td>
                    <td className="py-3 px-4">
                      <span
                        className={`inline-block px-3 py-1 rounded-full text-white text-xs font-medium ${
                          tipoBadgeColors[log.tipo] || "bg-gray-500"
                        }`}
                      >
                        {log.tipo.toUpperCase()}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-sm">
                      {log.usuario_id ? "Usuário" : "Sistema"}
                    </td>
                    <td className="py-3 px-4 text-sm">
                      <div className="max-w-md truncate" title={JSON.stringify(detalhes, null, 2)}>
                        {detalhes.action || detalhes.email || detalhes.error_type || "—"}
                      </div>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Gráfico de Logs por Dia (simples) */}
      {logs_por_dia.length > 0 && (
        <Card className="p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">📈 Logs por Dia (Últimos 30 Dias)</h2>
          <div className="space-y-2">
            {logs_por_dia.slice(0, 10).map((item) => {
              const maxValue = Math.max(...logs_por_dia.map((d) => d.total))
              const percentage = maxValue > 0 ? (item.total / maxValue) * 100 : 0
              const dataFormatada = new Date(item.dia).toLocaleDateString("pt-BR", {
                day: "2-digit",
                month: "2-digit",
              })

              return (
                <div key={item.dia} className="flex items-center gap-4">
                  <div className="w-20 text-sm text-gray-600">{dataFormatada}</div>
                  <div className="flex-1 bg-gray-200 rounded-full h-6 relative">
                    <div
                      className="bg-blue-500 h-6 rounded-full flex items-center justify-end pr-2"
                      style={{ width: `${percentage}%` }}
                    >
                      {item.total > 0 && (
                        <span className="text-white text-xs font-medium">{item.total}</span>
                      )}
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        </Card>
      )}

      {/* Tipos Mais Comuns */}
      {tipos_mais_comuns.length > 0 && (
        <Card className="p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">🏆 Tipos Mais Comuns (Últimos 30 Dias)</h2>
          <div className="space-y-2">
            {tipos_mais_comuns.map((item) => {
              const maxValue = Math.max(...tipos_mais_comuns.map((t) => t.total))
              const percentage = maxValue > 0 ? (item.total / maxValue) * 100 : 0

              return (
                <div key={item.tipo} className="flex items-center gap-4">
                  <div className="w-32 text-sm font-medium text-gray-700">
                    {item.tipo.toUpperCase()}
                  </div>
                  <div className="flex-1 bg-gray-200 rounded-full h-6 relative">
                    <div
                      className={`h-6 rounded-full flex items-center justify-end pr-2 ${
                        tipoBadgeColors[item.tipo as TipoLog] || "bg-gray-500"
                      }`}
                      style={{ width: `${percentage}%` }}
                    >
                      {item.total > 0 && (
                        <span className="text-white text-xs font-medium">{item.total}</span>
                      )}
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        </Card>
      )}
    </div>
  )
}

