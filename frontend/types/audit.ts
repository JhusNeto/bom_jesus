/**
 * Tipos para o sistema de auditoria
 */

export enum TipoLog {
  LOGIN = "login",
  PESAGEM = "pesagem",
  CARREGAMENTO = "carregamento",
  ATUALIZACAO = "atualizacao",
  DEVOLUCAO = "devolucao",
  MOVIMENTACAO = "movimentacao",
  OUTRO = "outro",
}

export interface LogOperacional {
  id: string
  tipo: TipoLog
  usuario_id?: string
  referencia_id?: string
  data: string
  detalhes?: string
  created_at: string
}

export interface TopUsuario {
  usuario_id: string
  usuario_nome: string
  usuario_email?: string
  total_logs: number
}

export interface AuditStats {
  total_logs: number
  logs_por_tipo: Record<string, number>
  logs_por_usuario: Record<string, number>
  logs_hoje: number
  logs_ultimos_7_dias: number
  logs_ultimos_30_dias: number
  ultima_atividade?: string
  top_usuarios: TopUsuario[]
  logs_recentes: LogOperacional[]
}

export interface LogsPorDia {
  dia: string
  total: number
}

export interface TipoMaisComum {
  tipo: string
  total: number
}

export interface AuditDashboard {
  resumo: AuditStats
  logs_por_dia: LogsPorDia[]
  tipos_mais_comuns: TipoMaisComum[]
}

