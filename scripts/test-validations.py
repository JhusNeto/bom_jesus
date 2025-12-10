#!/usr/bin/env python3
"""
Script para testar as validações implementadas
"""
import sys
import os
from datetime import datetime
from decimal import Decimal

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.services.pedido import PedidoService
from app.services.movimentacao_camara import MovimentacaoCamaraService
from app.schemas.pedido import PedidoCreate
from app.schemas.movimentacao_camara import MovimentacaoCamaraCreate
from app.models.pedido import OrigemPedido, StatusPedido
from app.models.movimentacao_camara import TipoMovimento
from app.models.cliente import Cliente
from app.models.camara import Camara

def test_validations():
    """Testa as validações implementadas"""
    db: Session = SessionLocal()
    
    print("="*80)
    print("  TESTE DE VALIDAÇÕES")
    print("="*80)
    
    try:
        # Obter cliente e câmara para testes
        cliente = db.query(Cliente).first()
        camara = db.query(Camara).first()
        
        if not cliente:
            print("❌ Nenhum cliente encontrado. Execute o script de validação de cenários primeiro.")
            return False
        
        if not camara:
            print("❌ Nenhuma câmara encontrada. Execute o script de validação de cenários primeiro.")
            return False
        
        pedido_service = PedidoService(db)
        movimentacao_service = MovimentacaoCamaraService(db)
        
        # TESTE 1: Tentar criar pedido e mudar status sem itens
        print("\n" + "-"*80)
        print("TESTE 1: Pedido sem itens - mudança de status")
        print("-"*80)
        
        pedido_create = PedidoCreate(
            data=datetime.utcnow(),
            cliente_id=cliente.id,
            origem_pedido=OrigemPedido.MANUAL,
            status=StatusPedido.ABERTO
        )
        
        pedido = pedido_service.create(pedido_create)
        print(f"✅ Pedido criado: {pedido.id}")
        
        # Tentar mudar status para SEPARADO sem itens (deve falhar)
        try:
            pedido_service.update_status(pedido.id, StatusPedido.SEPARADO)
            print("❌ ERRO: Deveria ter falhado ao mudar status sem itens")
            return False
        except Exception as e:
            from fastapi import HTTPException
            if isinstance(e, HTTPException):
                error_msg = str(e.detail).lower()
                if "deve ter pelo menos um item" in error_msg or "pedido deve ter" in error_msg:
                    print("✅ Validação funcionou: Não permite mudar status sem itens")
                else:
                    print(f"❌ Erro inesperado: {e.detail}")
                    return False
            else:
                print(f"❌ Erro inesperado: {e}")
                import traceback
                traceback.print_exc()
                return False
        
        # TESTE 2: Tentar saída maior que saldo
        print("\n" + "-"*80)
        print("TESTE 2: Saída maior que saldo disponível")
        print("-"*80)
        
        saldo_atual = movimentacao_service.get_saldo_camara(camara.id)
        print(f"Saldo atual na câmara: {saldo_atual} caixas")
        
        # Tentar saída maior que saldo (deve falhar)
        quantidade_saida = saldo_atual + 100  # Mais que o saldo
        
        movimentacao_create = MovimentacaoCamaraCreate(
            camara_id=camara.id,
            carga_id=None,
            data=datetime.utcnow(),
            tipo_movimento=TipoMovimento.SAIDA,
            quantidade_caixas=quantidade_saida,
            observacao="Teste de validação"
        )
        
        try:
            movimentacao_service.create(movimentacao_create)
            print(f"❌ ERRO: Deveria ter falhado ao tentar saída de {quantidade_saida} caixas")
            return False
        except Exception as e:
            from fastapi import HTTPException
            if isinstance(e, HTTPException):
                error_msg = str(e.detail).lower()
                if "saldo insuficiente" in error_msg:
                    print(f"✅ Validação funcionou: Não permite saída maior que saldo")
                else:
                    print(f"❌ Erro inesperado: {e.detail}")
                    return False
            else:
                print(f"❌ Erro inesperado: {e}")
                import traceback
                traceback.print_exc()
                return False
        
        # TESTE 3: Saída válida (menor que saldo)
        print("\n" + "-"*80)
        print("TESTE 3: Saída válida (menor que saldo)")
        print("-"*80)
        
        if saldo_atual > 0:
            quantidade_saida_valida = min(10, saldo_atual)  # 10 ou o saldo, o que for menor
            
            movimentacao_create = MovimentacaoCamaraCreate(
                camara_id=camara.id,
                carga_id=None,
                data=datetime.utcnow(),
                tipo_movimento=TipoMovimento.SAIDA,
                quantidade_caixas=quantidade_saida_valida,
                observacao="Teste de saída válida"
            )
            
            try:
                movimentacao = movimentacao_service.create(movimentacao_create)
                print(f"✅ Saída válida criada: {quantidade_saida_valida} caixas")
                
                # Verificar novo saldo
                novo_saldo = movimentacao_service.get_saldo_camara(camara.id)
                print(f"Novo saldo: {novo_saldo} caixas (esperado: {saldo_atual - quantidade_saida_valida})")
                
                if novo_saldo == saldo_atual - quantidade_saida_valida:
                    print("✅ Cálculo de saldo correto")
                else:
                    print(f"⚠️  Saldo calculado diferente do esperado")
            except Exception as e:
                print(f"❌ Erro ao criar saída válida: {e}")
                return False
        else:
            print("⚠️  Saldo zero, pulando teste de saída válida")
        
        # TESTE 4: Entrada sempre permitida
        print("\n" + "-"*80)
        print("TESTE 4: Entrada sempre permitida")
        print("-"*80)
        
        movimentacao_entrada = MovimentacaoCamaraCreate(
            camara_id=camara.id,
            carga_id=None,
            data=datetime.utcnow(),
            tipo_movimento=TipoMovimento.ENTRADA,
            quantidade_caixas=50,
            observacao="Teste de entrada"
        )
        
        try:
            movimentacao = movimentacao_service.create(movimentacao_entrada)
            print("✅ Entrada criada com sucesso")
        except Exception as e:
            print(f"❌ Erro ao criar entrada: {e}")
            return False
        
        print("\n" + "="*80)
        print("✅ TODOS OS TESTES PASSARAM!")
        print("="*80)
        return True
        
    except Exception as e:
        print(f"\n❌ Erro geral: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = test_validations()
    sys.exit(0 if success else 1)

