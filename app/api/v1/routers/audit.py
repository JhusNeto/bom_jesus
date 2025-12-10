"""
Router para consulta de logs de auditoria
"""
from typing import List, Optional, Dict, Any
from uuid import UUID
from fastapi import APIRouter, Depends, Query, Response
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timedelta

from app.db.session import get_db
from app.core.security import get_current_user, requires_role
from app.models.user import User
from app.models.log_operacional import LogOperacional, TipoLog
from app.repositories.log_operacional import LogOperacionalRepository
from app.schemas.log_operacional import LogOperacionalRead
from pydantic import BaseModel

router = APIRouter(prefix="/audit", tags=["Auditoria"])


class AuditStatsResponse(BaseModel):
    """Resposta com estatísticas de auditoria"""
    total_logs: int
    logs_por_tipo: Dict[str, int]
    logs_por_usuario: Dict[str, int]
    logs_hoje: int
    logs_ultimos_7_dias: int
    logs_ultimos_30_dias: int
    ultima_atividade: Optional[datetime]
    top_usuarios: List[Dict[str, Any]]
    logs_recentes: List[LogOperacionalRead]


class DashboardResponse(BaseModel):
    """Resposta do dashboard de auditoria"""
    resumo: AuditStatsResponse
    logs_por_dia: List[Dict[str, Any]]
    tipos_mais_comuns: List[Dict[str, Any]]


@router.get("/logs", response_model=List[LogOperacionalRead])
@requires_role(["ADMIN", "MANAGER"])
async def get_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    tipo: Optional[TipoLog] = None,
    usuario_id: Optional[UUID] = None,
    referencia_id: Optional[UUID] = None,
    data_inicio: Optional[datetime] = None,
    data_fim: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Consulta logs de auditoria
    
    Apenas ADMIN e MANAGER podem consultar logs de auditoria.
    """
    repository = LogOperacionalRepository(db)
    
    # Construir filtros
    filters = {}
    if tipo:
        filters["tipo"] = tipo
    if usuario_id:
        filters["usuario_id"] = usuario_id
    if referencia_id:
        filters["referencia_id"] = referencia_id
    
    logs = repository.get_all(skip=skip, limit=limit, filters=filters)
    
    # Filtrar por data se fornecido
    if data_inicio or data_fim:
        filtered_logs = []
        for log in logs:
            if data_inicio and log.data < data_inicio:
                continue
            if data_fim and log.data > data_fim:
                continue
            filtered_logs.append(log)
        logs = filtered_logs
    
    return logs


@router.get("/logs/{log_id}", response_model=LogOperacionalRead)
@requires_role(["ADMIN", "MANAGER"])
async def get_audit_log(
    log_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Consulta um log de auditoria específico
    """
    repository = LogOperacionalRepository(db)
    log = repository.get(log_id)
    
    if not log:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Log de auditoria não encontrado"
        )
    
    return log


@router.get("/stats", response_model=AuditStatsResponse)
@requires_role(["ADMIN", "MANAGER"])
async def get_audit_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retorna estatísticas de auditoria
    
    Inclui:
    - Total de logs
    - Logs por tipo
    - Logs por usuário
    - Logs hoje, últimos 7 dias, últimos 30 dias
    - Última atividade
    - Top usuários
    - Logs recentes
    """
    repository = LogOperacionalRepository(db)
    
    # Total de logs
    total_logs = db.query(func.count(LogOperacional.id)).scalar() or 0
    
    # Logs por tipo
    logs_por_tipo = {}
    tipo_counts = db.query(
        LogOperacional.tipo,
        func.count(LogOperacional.id).label('count')
    ).group_by(LogOperacional.tipo).all()
    
    for tipo, count in tipo_counts:
        logs_por_tipo[tipo.value] = count
    
    # Logs por usuário
    logs_por_usuario = {}
    usuario_counts = db.query(
        LogOperacional.usuario_id,
        func.count(LogOperacional.id).label('count')
    ).filter(LogOperacional.usuario_id.isnot(None)).group_by(LogOperacional.usuario_id).all()
    
    for usuario_id, count in usuario_counts:
        logs_por_usuario[str(usuario_id)] = count
    
    # Logs hoje
    hoje = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    logs_hoje = db.query(func.count(LogOperacional.id)).filter(
        LogOperacional.data >= hoje
    ).scalar() or 0
    
    # Logs últimos 7 dias
    sete_dias_atras = datetime.utcnow() - timedelta(days=7)
    logs_ultimos_7_dias = db.query(func.count(LogOperacional.id)).filter(
        LogOperacional.data >= sete_dias_atras
    ).scalar() or 0
    
    # Logs últimos 30 dias
    trinta_dias_atras = datetime.utcnow() - timedelta(days=30)
    logs_ultimos_30_dias = db.query(func.count(LogOperacional.id)).filter(
        LogOperacional.data >= trinta_dias_atras
    ).scalar() or 0
    
    # Última atividade
    ultima_atividade = db.query(func.max(LogOperacional.data)).scalar()
    
    # Top usuários (últimos 30 dias)
    top_usuarios_query = db.query(
        LogOperacional.usuario_id,
        func.count(LogOperacional.id).label('count')
    ).filter(
        and_(
            LogOperacional.usuario_id.isnot(None),
            LogOperacional.data >= trinta_dias_atras
        )
    ).group_by(LogOperacional.usuario_id).order_by(func.count(LogOperacional.id).desc()).limit(10).all()
    
    top_usuarios = []
    for usuario_id, count in top_usuarios_query:
        # Buscar nome do usuário
        usuario = db.query(User).filter(User.id == usuario_id).first()
        top_usuarios.append({
            "usuario_id": str(usuario_id),
            "usuario_nome": usuario.name if usuario else "Desconhecido",
            "usuario_email": usuario.email if usuario else None,
            "total_logs": count
        })
    
    # Logs recentes (últimos 10)
    logs_recentes = db.query(LogOperacional).order_by(
        LogOperacional.data.desc()
    ).limit(10).all()
    
    return AuditStatsResponse(
        total_logs=total_logs,
        logs_por_tipo=logs_por_tipo,
        logs_por_usuario=logs_por_usuario,
        logs_hoje=logs_hoje,
        logs_ultimos_7_dias=logs_ultimos_7_dias,
        logs_ultimos_30_dias=logs_ultimos_30_dias,
        ultima_atividade=ultima_atividade,
        top_usuarios=top_usuarios,
        logs_recentes=[LogOperacionalRead.model_validate(log) for log in logs_recentes]
    )


@router.get("/dashboard", response_model=DashboardResponse)
@requires_role(["ADMIN", "MANAGER"])
async def get_audit_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retorna dashboard completo de auditoria
    
    Inclui estatísticas, gráficos de logs por dia, tipos mais comuns, etc.
    """
    # Obter estatísticas básicas
    stats = await get_audit_stats(db=db, current_user=current_user)
    
    # Logs por dia (últimos 30 dias)
    trinta_dias_atras = datetime.utcnow() - timedelta(days=30)
    logs_por_dia_query = db.query(
        func.date(LogOperacional.data).label('dia'),
        func.count(LogOperacional.id).label('count')
    ).filter(
        LogOperacional.data >= trinta_dias_atras
    ).group_by(func.date(LogOperacional.data)).order_by(func.date(LogOperacional.data).desc()).all()
    
    logs_por_dia = [
        {
            "dia": dia.isoformat() if dia else None,
            "total": count
        }
        for dia, count in logs_por_dia_query
    ]
    
    # Tipos mais comuns (últimos 30 dias)
    tipos_mais_comuns_query = db.query(
        LogOperacional.tipo,
        func.count(LogOperacional.id).label('count')
    ).filter(
        LogOperacional.data >= trinta_dias_atras
    ).group_by(LogOperacional.tipo).order_by(func.count(LogOperacional.id).desc()).all()
    
    tipos_mais_comuns = [
        {
            "tipo": tipo.value,
            "total": count
        }
        for tipo, count in tipos_mais_comuns_query
    ]
    
    return DashboardResponse(
        resumo=stats,
        logs_por_dia=logs_por_dia,
        tipos_mais_comuns=tipos_mais_comuns
    )


@router.get("/panel", response_class=HTMLResponse)
@requires_role(["ADMIN", "MANAGER"])
async def audit_panel(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Painel HTML simples para visualização de auditoria
    """
    # Obter dados do dashboard
    dashboard = await get_audit_dashboard(db=db, current_user=current_user)
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Painel de Auditoria - Sistema Bom Jesus</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                background: #f5f5f5;
                padding: 20px;
                color: #333;
            }}
            .container {{
                max-width: 1400px;
                margin: 0 auto;
            }}
            header {{
                background: white;
                padding: 20px;
                border-radius: 8px;
                margin-bottom: 20px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            h1 {{
                color: #2c3e50;
                margin-bottom: 10px;
            }}
            .subtitle {{
                color: #7f8c8d;
                font-size: 14px;
            }}
            .stats-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-bottom: 20px;
            }}
            .stat-card {{
                background: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .stat-card h3 {{
                color: #7f8c8d;
                font-size: 14px;
                font-weight: 500;
                margin-bottom: 10px;
                text-transform: uppercase;
            }}
            .stat-card .value {{
                font-size: 32px;
                font-weight: bold;
                color: #2c3e50;
            }}
            .section {{
                background: white;
                padding: 20px;
                border-radius: 8px;
                margin-bottom: 20px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .section h2 {{
                color: #2c3e50;
                margin-bottom: 20px;
                font-size: 20px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
            }}
            th, td {{
                padding: 12px;
                text-align: left;
                border-bottom: 1px solid #e0e0e0;
            }}
            th {{
                background: #f8f9fa;
                font-weight: 600;
                color: #495057;
            }}
            tr:hover {{
                background: #f8f9fa;
            }}
            .badge {{
                display: inline-block;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 12px;
                font-weight: 500;
            }}
            .badge-login {{ background: #3498db; color: white; }}
            .badge-carregamento {{ background: #2ecc71; color: white; }}
            .badge-atualizacao {{ background: #f39c12; color: white; }}
            .badge-pesagem {{ background: #9b59b6; color: white; }}
            .badge-movimentacao {{ background: #e67e22; color: white; }}
            .badge-outro {{ background: #95a5a6; color: white; }}
            .badge-devolucao {{ background: #e74c3c; color: white; }}
            .refresh-btn {{
                background: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                cursor: pointer;
                font-size: 14px;
                margin-top: 10px;
            }}
            .refresh-btn:hover {{
                background: #2980b9;
            }}
            .json-details {{
                background: #f8f9fa;
                padding: 10px;
                border-radius: 4px;
                font-family: monospace;
                font-size: 12px;
                max-height: 200px;
                overflow-y: auto;
                white-space: pre-wrap;
                word-break: break-all;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>🔍 Painel de Auditoria</h1>
                <p class="subtitle">Sistema Operacional Bom Jesus | Usuário: {current_user.name} ({current_user.email})</p>
            </header>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <h3>Total de Logs</h3>
                    <div class="value">{dashboard.resumo.total_logs}</div>
                </div>
                <div class="stat-card">
                    <h3>Logs Hoje</h3>
                    <div class="value">{dashboard.resumo.logs_hoje}</div>
                </div>
                <div class="stat-card">
                    <h3>Últimos 7 Dias</h3>
                    <div class="value">{dashboard.resumo.logs_ultimos_7_dias}</div>
                </div>
                <div class="stat-card">
                    <h3>Últimos 30 Dias</h3>
                    <div class="value">{dashboard.resumo.logs_ultimos_30_dias}</div>
                </div>
            </div>
            
            <div class="section">
                <h2>📊 Logs por Tipo</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Tipo</th>
                            <th>Total</th>
                        </tr>
                    </thead>
                    <tbody>
    """
    
    # Adicionar logs por tipo
    for tipo, count in dashboard.resumo.logs_por_tipo.items():
        badge_class = f"badge-{tipo}"
        html_content += f"""
                        <tr>
                            <td><span class="badge {badge_class}">{tipo.upper()}</span></td>
                            <td>{count}</td>
                        </tr>
        """
    
    html_content += """
                    </tbody>
                </table>
            </div>
            
            <div class="section">
                <h2>👥 Top Usuários (Últimos 30 Dias)</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Usuário</th>
                            <th>Email</th>
                            <th>Total de Logs</th>
                        </tr>
                    </thead>
                    <tbody>
    """
    
    # Adicionar top usuários
    for usuario in dashboard.resumo.top_usuarios:
        html_content += f"""
                        <tr>
                            <td>{usuario.get('usuario_nome', 'Desconhecido')}</td>
                            <td>{usuario.get('usuario_email', 'N/A')}</td>
                            <td>{usuario.get('total_logs', 0)}</td>
                        </tr>
        """
    
    html_content += """
                    </tbody>
                </table>
            </div>
            
            <div class="section">
                <h2>📝 Logs Recentes</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Data/Hora</th>
                            <th>Tipo</th>
                            <th>Usuário</th>
                            <th>Detalhes</th>
                        </tr>
                    </thead>
                    <tbody>
    """
    
    # Adicionar logs recentes
    for log in dashboard.resumo.logs_recentes[:20]:  # Limitar a 20
        import json
        detalhes = json.loads(log.detalhes) if log.detalhes else {}
        action = detalhes.get('action', 'N/A')
        badge_class = f"badge-{log.tipo.value}"
        usuario_nome = "Sistema" if not log.usuario_id else "Usuário"
        
        html_content += f"""
                        <tr>
                            <td>{log.data.strftime('%d/%m/%Y %H:%M:%S') if log.data else 'N/A'}</td>
                            <td><span class="badge {badge_class}">{log.tipo.value.upper()}</span></td>
                            <td>{usuario_nome}</td>
                            <td>
                                <div class="json-details">{json.dumps(detalhes, indent=2, ensure_ascii=False)[:200]}...</div>
                            </td>
                        </tr>
        """
    
    html_content += """
                    </tbody>
                </table>
            </div>
            
            <div class="section">
                <button class="refresh-btn" onclick="location.reload()">🔄 Atualizar</button>
            </div>
        </div>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)

