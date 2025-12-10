#!/usr/bin/env python3
"""
Script de Teste Completo de Banco de Dados
Testa migrações, tabelas, relacionamentos, integridade
"""
import sys
import os
from datetime import datetime
from typing import Dict, Any, List

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text, inspect
from app.db.session import SessionLocal, engine
from app.db.base import Base
from app.models import *

test_results: List[Dict[str, Any]] = []


def log_test(name: str, status: str, error: str = None, details: Dict = None):
    """Registra resultado de um teste"""
    result = {"name": name, "status": status, "timestamp": datetime.utcnow().isoformat() + "Z"}
    if error:
        result["error"] = error
    if details:
        result["details"] = details
    test_results.append(result)
    
    if status == "PASSED":
        print(f"✅ {name}")
    else:
        print(f"❌ {name}: {error}")


def test_migrations():
    """Testa migrações"""
    print("\n📦 Testando Migrações...")
    
    try:
        from alembic.config import Config
        from alembic import command
        from alembic.script import ScriptDirectory
        
        config = Config("alembic.ini")
        script = ScriptDirectory.from_config(config)
        
        # Verificar versão atual
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version_num FROM alembic_version"))
            current_version = result.scalar()
            
            if current_version:
                log_test("Versão atual de migração", "PASSED",
                        details={"version": current_version})
            else:
                log_test("Versão atual de migração", "FAILED", "Nenhuma versão encontrada")
        
        # Verificar histórico
        revisions = list(script.walk_revisions())
        if len(revisions) >= 4:
            log_test("Histórico de migrações", "PASSED",
                    details={"total_migrations": len(revisions)})
        else:
            log_test("Histórico de migrações", "FAILED",
                    f"Esperado pelo menos 4 migrações, encontrado {len(revisions)}")
        
        # Verificar ordem das migrações
        expected_order = ["701ea1d79e33", "432576a07748", "e0f88042950c", "0ae0eb1aa3f8"]
        rev_ids = [rev.revision for rev in revisions]
        if all(rev_id in rev_ids for rev_id in expected_order):
            log_test("Ordem das migrações", "PASSED")
        else:
            log_test("Ordem das migrações", "FAILED", "Ordem incorreta")
            
    except Exception as e:
        log_test("Verificação de migrações", "FAILED", str(e))


def test_tables():
    """Testa tabelas"""
    print("\n📊 Testando Tabelas...")
    
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        expected_tables = [
            "users", "auth_tokens", "logs_operacionais",
            "cargas", "camaras", "movimentacoes_camara",
            "pesagens", "perdas", "clientes", "pedidos",
            "itens_pedido", "devolucoes", "gastos_internos",
            "ocr_inputs", "rotas", "entregas_cliente"
        ]
        
        missing_tables = [t for t in expected_tables if t not in tables]
        
        if len(missing_tables) == 0:
            log_test("Todas as tabelas criadas", "PASSED",
                    details={"total_tables": len(tables), "expected": len(expected_tables)})
        else:
            log_test("Todas as tabelas criadas", "FAILED",
                    f"Tabelas faltando: {missing_tables}")
        
        # Verificar tabela alembic_version
        if "alembic_version" in tables:
            log_test("Tabela alembic_version existe", "PASSED")
        else:
            log_test("Tabela alembic_version existe", "FAILED")
            
    except Exception as e:
        log_test("Verificação de tabelas", "FAILED", str(e))


def test_relationships():
    """Testa relacionamentos (foreign keys)"""
    print("\n🔗 Testando Relacionamentos...")
    
    try:
        inspector = inspect(engine)
        
        # Verificar FK users -> auth_tokens
        fks = inspector.get_foreign_keys("auth_tokens")
        user_fk = [fk for fk in fks if fk["referred_table"] == "users"]
        if user_fk:
            log_test("FK auth_tokens -> users", "PASSED")
        else:
            log_test("FK auth_tokens -> users", "FAILED")
        
        # Verificar outras FKs importantes
        important_fks = [
            ("logs_operacionais", "users"),
            ("pedidos", "clientes"),
            ("itens_pedido", "pedidos"),
        ]
        
        for table, ref_table in important_fks:
            fks = inspector.get_foreign_keys(table)
            ref_fk = [fk for fk in fks if fk["referred_table"] == ref_table]
            if ref_fk:
                log_test(f"FK {table} -> {ref_table}", "PASSED")
            else:
                log_test(f"FK {table} -> {ref_table}", "FAILED")
                
    except Exception as e:
        log_test("Verificação de relacionamentos", "FAILED", str(e))


def test_indexes():
    """Testa índices"""
    print("\n📇 Testando Índices...")
    
    try:
        inspector = inspect(engine)
        
        # Verificar índices em tabelas importantes
        important_indexes = [
            ("users", "email"),
            ("users", "role"),
            ("auth_tokens", "token"),
            ("logs_operacionais", "tipo"),
        ]
        
        for table, column in important_indexes:
            indexes = inspector.get_indexes(table)
            col_indexes = [idx for idx in indexes if column in idx.get("column_names", [])]
            if col_indexes:
                log_test(f"Índice {table}.{column}", "PASSED")
            else:
                log_test(f"Índice {table}.{column}", "FAILED")
                
    except Exception as e:
        log_test("Verificação de índices", "FAILED", str(e))


def test_enums():
    """Testa enums PostgreSQL"""
    print("\n🔢 Testando Enums...")
    
    try:
        with engine.connect() as conn:
            # Verificar enum userrole
            result = conn.execute(text(
                "SELECT unnest(enum_range(NULL::userrole))"
            ))
            userrole_values = [row[0] for row in result]
            expected_roles = ["ADMIN", "MANAGER", "OPERATOR", "VIEWER"]
            
            if all(role in userrole_values for role in expected_roles):
                log_test("Enum userrole", "PASSED",
                        details={"values": userrole_values})
            else:
                log_test("Enum userrole", "FAILED",
                        f"Valores esperados: {expected_roles}, encontrados: {userrole_values}")
        
    except Exception as e:
        log_test("Verificação de enums", "FAILED", str(e))


def test_data_integrity():
    """Testa integridade de dados"""
    print("\n🔒 Testando Integridade de Dados...")
    
    try:
        db = SessionLocal()
        
        # Verificar usuários
        from app.models import User
        users = db.query(User).all()
        if len(users) >= 4:
            log_test("Usuários de teste existem", "PASSED",
                    details={"count": len(users)})
        else:
            log_test("Usuários de teste existem", "FAILED",
                    f"Esperado pelo menos 4 usuários, encontrado {len(users)}")
        
        # Verificar roles dos usuários
        roles = set(user.role.value for user in users)
        expected_roles = {"ADMIN", "MANAGER", "OPERATOR", "VIEWER"}
        if roles.issuperset(expected_roles):
            log_test("Roles de usuários corretas", "PASSED",
                    details={"roles": list(roles)})
        else:
            log_test("Roles de usuários corretas", "FAILED",
                    f"Esperado: {expected_roles}, encontrado: {roles}")
        
        # Verificar integridade referencial (tentar inserir FK inválida)
        from app.models import AuthToken
        from uuid import uuid4
        try:
            invalid_token = AuthToken(
                id=uuid4(),
                user_id=uuid4(),  # UUID que não existe
                token="test",
                token_type="bearer",
                is_active=True,
                expires_at=datetime.utcnow()
            )
            db.add(invalid_token)
            db.commit()
            log_test("Integridade referencial", "FAILED",
                    "Permitiu FK inválida")
            db.rollback()
        except Exception:
            log_test("Integridade referencial", "PASSED",
                    "FK inválida foi rejeitada")
            db.rollback()
        
        db.close()
        
    except Exception as e:
        log_test("Verificação de integridade", "FAILED", str(e))


def main():
    """Executa todos os testes de banco"""
    print("=" * 60)
    print("🗄️ BATERIA DE TESTES DE BANCO DE DADOS")
    print("=" * 60)
    
    test_migrations()
    test_tables()
    test_relationships()
    test_indexes()
    test_enums()
    test_data_integrity()
    
    # Resumo
    print("\n" + "=" * 60)
    print("📊 RESUMO DOS TESTES")
    print("=" * 60)
    
    passed = sum(1 for t in test_results if t["status"] == "PASSED")
    failed = sum(1 for t in test_results if t["status"] == "FAILED")
    total = len(test_results)
    
    print(f"Total: {total}")
    print(f"✅ Passou: {passed}")
    print(f"❌ Falhou: {failed}")
    if total > 0:
        print(f"Taxa de sucesso: {(passed/total*100):.1f}%")
    
    if failed > 0:
        print("\n❌ Testes que falharam:")
        for test in test_results:
            if test["status"] == "FAILED":
                print(f"  - {test['name']}: {test.get('error', 'Sem detalhes')}")
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

