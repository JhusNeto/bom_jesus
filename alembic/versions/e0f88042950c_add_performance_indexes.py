"""add_performance_indexes

Revision ID: e0f88042950c
Revises: 432576a07748
Create Date: 2025-12-03 17:45:00.505165

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e0f88042950c'
down_revision = '432576a07748'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Adiciona índices de performance para otimizar queries comuns.
    
    Estratégia:
    1. Índices em campos de data para ordenação e filtros temporais
    2. Índices compostos para queries frequentes (cliente + status, carga + status, etc.)
    3. Índices em campos de busca (fornecedor, cidade, bairro)
    4. Índices em campos de filtro (is_active, devolucao)
    """
    
    # ============================================
    # ÍNDICES SIMPLES - Campos de Data
    # ============================================
    # Para ordenação e filtros temporais
    
    # Cargas
    op.create_index('ix_cargas_data_chegada', 'cargas', ['data_chegada'], unique=False)
    op.create_index('ix_cargas_created_at', 'cargas', ['created_at'], unique=False)
    
    # Pedidos
    op.create_index('ix_pedidos_created_at', 'pedidos', ['created_at'], unique=False)
    
    # Pesagens
    op.create_index('ix_pesagens_created_at', 'pesagens', ['created_at'], unique=False)
    
    # Movimentações Câmara
    op.create_index('ix_movimentacoes_camara_created_at', 'movimentacoes_camara', ['created_at'], unique=False)
    
    # Perdas
    op.create_index('ix_perdas_created_at', 'perdas', ['created_at'], unique=False)
    
    # Devoluções
    op.create_index('ix_devolucoes_created_at', 'devolucoes', ['created_at'], unique=False)
    
    # Gastos Internos
    op.create_index('ix_gastos_internos_created_at', 'gastos_internos', ['created_at'], unique=False)
    
    # Logs Operacionais
    op.create_index('ix_logs_operacionais_created_at', 'logs_operacionais', ['created_at'], unique=False)
    
    # OCR Inputs
    op.create_index('ix_ocr_inputs_created_at', 'ocr_inputs', ['created_at'], unique=False)
    
    # Rotas
    op.create_index('ix_rotas_created_at', 'rotas', ['created_at'], unique=False)
    
    # Entregas Cliente
    op.create_index('ix_entregas_cliente_created_at', 'entregas_cliente', ['created_at'], unique=False)
    
    # Users
    op.create_index('ix_users_created_at', 'users', ['created_at'], unique=False)
    
    # Auth Tokens
    op.create_index('ix_auth_tokens_created_at', 'auth_tokens', ['created_at'], unique=False)
    
    # ============================================
    # ÍNDICES COMPOSTOS - Queries Frequentes
    # ============================================
    # Otimiza queries que filtram por múltiplos campos
    
    # Pedidos: buscar por cliente e status (query muito comum)
    op.create_index('ix_pedidos_cliente_status', 'pedidos', ['cliente_id', 'status'], unique=False)
    
    # Pedidos: buscar por cliente e data (relatórios por período)
    op.create_index('ix_pedidos_cliente_data', 'pedidos', ['cliente_id', 'data'], unique=False)
    
    # Pesagens: buscar por cliente e status
    op.create_index('ix_pesagens_cliente_status', 'pesagens', ['cliente_id', 'status'], unique=False)
    
    # Pesagens: buscar por carga e status
    op.create_index('ix_pesagens_carga_status', 'pesagens', ['carga_id', 'status'], unique=False)
    
    # Movimentações Câmara: buscar por câmara, tipo e data
    op.create_index('ix_movimentacoes_camara_camara_tipo_data', 'movimentacoes_camara', 
                    ['camara_id', 'tipo_movimento', 'data'], unique=False)
    
    # Movimentações Câmara: buscar por câmara e data (relatórios)
    op.create_index('ix_movimentacoes_camara_camara_data', 'movimentacoes_camara', 
                    ['camara_id', 'data'], unique=False)
    
    # Perdas: buscar por carga e data
    op.create_index('ix_perdas_carga_data', 'perdas', ['carga_id', 'data'], unique=False)
    
    # Logs Operacionais: buscar por usuário, tipo e data
    op.create_index('ix_logs_operacionais_usuario_tipo_data', 'logs_operacionais', 
                    ['usuario_id', 'tipo', 'data'], unique=False)
    
    # Logs Operacionais: buscar por tipo e data (auditoria)
    op.create_index('ix_logs_operacionais_tipo_data', 'logs_operacionais', 
                    ['tipo', 'data'], unique=False)
    
    # Auth Tokens: buscar tokens ativos de um usuário (validação de sessão)
    op.create_index('ix_auth_tokens_user_active_expires', 'auth_tokens', 
                    ['user_id', 'is_active', 'expires_at'], unique=False)
    
    # ============================================
    # ÍNDICES - Campos de Busca
    # ============================================
    # Para buscas por texto (LIKE queries)
    
    # Clientes: buscar por cidade
    op.create_index('ix_clientes_cidade', 'clientes', ['cidade'], unique=False)
    
    # Clientes: buscar por bairro
    op.create_index('ix_clientes_bairro', 'clientes', ['bairro'], unique=False)
    
    # Cargas: buscar por fornecedor
    op.create_index('ix_cargas_fornecedor', 'cargas', ['fornecedor'], unique=False)
    
    # Cargas: buscar por fazenda
    op.create_index('ix_cargas_fazenda', 'cargas', ['fazenda'], unique=False)
    
    # ============================================
    # ÍNDICES - Campos de Filtro
    # ============================================
    # Para filtros booleanos e de status
    
    # Users: filtrar por ativo/inativo
    op.create_index('ix_users_is_active', 'users', ['is_active'], unique=False)
    
    # Entregas Cliente: filtrar por devolução
    op.create_index('ix_entregas_cliente_devolucao', 'entregas_cliente', ['devolucao'], unique=False)
    
    # ============================================
    # ÍNDICES ADICIONAIS - Otimizações Específicas
    # ============================================
    
    # Item Pedido: buscar itens por pedido e tipo (relatórios)
    op.create_index('ix_itens_pedido_pedido_tipo', 'itens_pedido', ['pedido_id', 'tipo_banana'], unique=False)
    
    # Entrega Cliente: buscar entregas por rota e cliente
    op.create_index('ix_entregas_cliente_rota_cliente', 'entregas_cliente', 
                    ['rota_id', 'cliente_id'], unique=False)
    
    # Devoluções: buscar por cliente e pedido
    op.create_index('ix_devolucoes_cliente_pedido', 'devolucoes', ['cliente_id', 'pedido_id'], unique=False)


def downgrade() -> None:
    """
    Remove todos os índices de performance adicionados.
    """
    
    # Remover índices compostos primeiro
    op.drop_index('ix_devolucoes_cliente_pedido', table_name='devolucoes')
    op.drop_index('ix_entregas_cliente_rota_cliente', table_name='entregas_cliente')
    op.drop_index('ix_itens_pedido_pedido_tipo', table_name='itens_pedido')
    op.drop_index('ix_logs_operacionais_tipo_data', table_name='logs_operacionais')
    op.drop_index('ix_logs_operacionais_usuario_tipo_data', table_name='logs_operacionais')
    op.drop_index('ix_perdas_carga_data', table_name='perdas')
    op.drop_index('ix_movimentacoes_camara_camara_data', table_name='movimentacoes_camara')
    op.drop_index('ix_movimentacoes_camara_camara_tipo_data', table_name='movimentacoes_camara')
    op.drop_index('ix_pesagens_carga_status', table_name='pesagens')
    op.drop_index('ix_pesagens_cliente_status', table_name='pesagens')
    op.drop_index('ix_pedidos_cliente_data', table_name='pedidos')
    op.drop_index('ix_pedidos_cliente_status', table_name='pedidos')
    op.drop_index('ix_auth_tokens_user_active_expires', table_name='auth_tokens')
    
    # Remover índices de filtro
    op.drop_index('ix_entregas_cliente_devolucao', table_name='entregas_cliente')
    op.drop_index('ix_users_is_active', table_name='users')
    
    # Remover índices de busca
    op.drop_index('ix_cargas_fazenda', table_name='cargas')
    op.drop_index('ix_cargas_fornecedor', table_name='cargas')
    op.drop_index('ix_clientes_bairro', table_name='clientes')
    op.drop_index('ix_clientes_cidade', table_name='clientes')
    
    # Remover índices de data
    op.drop_index('ix_auth_tokens_created_at', table_name='auth_tokens')
    op.drop_index('ix_users_created_at', table_name='users')
    op.drop_index('ix_entregas_cliente_created_at', table_name='entregas_cliente')
    op.drop_index('ix_rotas_created_at', table_name='rotas')
    op.drop_index('ix_ocr_inputs_created_at', table_name='ocr_inputs')
    op.drop_index('ix_logs_operacionais_created_at', table_name='logs_operacionais')
    op.drop_index('ix_gastos_internos_created_at', table_name='gastos_internos')
    op.drop_index('ix_devolucoes_created_at', table_name='devolucoes')
    op.drop_index('ix_perdas_created_at', table_name='perdas')
    op.drop_index('ix_movimentacoes_camara_created_at', table_name='movimentacoes_camara')
    op.drop_index('ix_pesagens_created_at', table_name='pesagens')
    op.drop_index('ix_pedidos_created_at', table_name='pedidos')
    op.drop_index('ix_cargas_created_at', table_name='cargas')
    op.drop_index('ix_cargas_data_chegada', table_name='cargas')
