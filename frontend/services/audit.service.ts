import api from "./api"
import type { AuditStats, AuditDashboard, LogOperacional, TipoLog } from "@/types/audit"

export const auditService = {
  /**
   * Obtém estatísticas de auditoria
   */
  async getStats(): Promise<AuditStats> {
    const response = await api.get<AuditStats>("/audit/stats")
    return response.data
  },

  /**
   * Obtém dashboard completo de auditoria
   */
  async getDashboard(): Promise<AuditDashboard> {
    const response = await api.get<AuditDashboard>("/audit/dashboard")
    return response.data
  },

  /**
   * Obtém logs de auditoria com filtros
   */
  async getLogs(params?: {
    skip?: number
    limit?: number
    tipo?: TipoLog
    usuario_id?: string
    referencia_id?: string
    data_inicio?: string
    data_fim?: string
  }): Promise<LogOperacional[]> {
    const response = await api.get<LogOperacional[]>("/audit/logs", { params })
    return response.data
  },

  /**
   * Obtém um log específico por ID
   */
  async getLog(logId: string): Promise<LogOperacional> {
    const response = await api.get<LogOperacional>(`/audit/logs/${logId}`)
    return response.data
  },
}

