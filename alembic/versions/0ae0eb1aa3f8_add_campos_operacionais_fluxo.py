"""add_campos_operacionais_fluxo

Revision ID: 0ae0eb1aa3f8
Revises: e0f88042950c
Create Date: 2025-12-06 21:41:49.058633

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '0ae0eb1aa3f8'
down_revision = 'e0f88042950c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Criar enum para estado_maturacao
    op.execute("CREATE TYPE estadomaturacao AS ENUM ('verde', 'de_vez', 'madura')")
    
    # Criar enum para status_entrega
    op.execute("CREATE TYPE statusentrega AS ENUM ('pendente', 'em_transito', 'entregue', 'devolvida', 'cancelada')")
    
    # Adicionar campos em cargas
    op.add_column('cargas', sa.Column('estado_maturacao', postgresql.ENUM('verde', 'de_vez', 'madura', name='estadomaturacao', create_type=False), nullable=True))
    op.add_column('cargas', sa.Column('responsavel_recebimento_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.create_index(op.f('ix_cargas_estado_maturacao'), 'cargas', ['estado_maturacao'], unique=False)
    op.create_index(op.f('ix_cargas_responsavel_recebimento_id'), 'cargas', ['responsavel_recebimento_id'], unique=False)
    op.create_foreign_key('cargas_responsavel_recebimento_id_fkey', 'cargas', 'users', ['responsavel_recebimento_id'], ['id'], ondelete='SET NULL')
    
    # Adicionar campo em rotas
    op.add_column('rotas', sa.Column('horario_saida', sa.DateTime(), nullable=True))
    op.create_index(op.f('ix_rotas_horario_saida'), 'rotas', ['horario_saida'], unique=False)
    
    # Adicionar campos em entregas_cliente
    op.add_column('entregas_cliente', sa.Column('carga_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('entregas_cliente', sa.Column('status_entrega', postgresql.ENUM('pendente', 'em_transito', 'entregue', 'devolvida', 'cancelada', name='statusentrega', create_type=False), nullable=False, server_default='pendente'))
    op.create_index(op.f('ix_entregas_cliente_carga_id'), 'entregas_cliente', ['carga_id'], unique=False)
    op.create_index(op.f('ix_entregas_cliente_status_entrega'), 'entregas_cliente', ['status_entrega'], unique=False)
    op.create_foreign_key('entregas_cliente_carga_id_fkey', 'entregas_cliente', 'cargas', ['carga_id'], ['id'], ondelete='SET NULL')


def downgrade() -> None:
    # Remover foreign keys
    op.drop_constraint('entregas_cliente_carga_id_fkey', 'entregas_cliente', type_='foreignkey')
    op.drop_constraint('cargas_responsavel_recebimento_id_fkey', 'cargas', type_='foreignkey')
    
    # Remover índices
    op.drop_index(op.f('ix_entregas_cliente_status_entrega'), table_name='entregas_cliente')
    op.drop_index(op.f('ix_entregas_cliente_carga_id'), table_name='entregas_cliente')
    op.drop_index(op.f('ix_rotas_horario_saida'), table_name='rotas')
    op.drop_index(op.f('ix_cargas_responsavel_recebimento_id'), table_name='cargas')
    op.drop_index(op.f('ix_cargas_estado_maturacao'), table_name='cargas')
    
    # Remover colunas
    op.drop_column('entregas_cliente', 'status_entrega')
    op.drop_column('entregas_cliente', 'carga_id')
    op.drop_column('rotas', 'horario_saida')
    op.drop_column('cargas', 'responsavel_recebimento_id')
    op.drop_column('cargas', 'estado_maturacao')
    
    # Remover enums
    op.execute('DROP TYPE IF EXISTS statusentrega')
    op.execute('DROP TYPE IF EXISTS estadomaturacao')
