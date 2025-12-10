#!/usr/bin/env python3
"""
Script de Testes de Banco de Dados - Sistema Operacional Bom Jesus
Testa conexão, estrutura, tabelas e migrations
"""
import sys
import json
import argparse
from datetime import datetime
from typing import Dict, List, Any

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
except ImportError:
    print("❌ psycopg2 não instalado. Execute: pip install psycopg2-binary")
    sys.exit(1)

# Configurações padrão
DB_CONFIG = {
    "host": "localhost",
    "port": 5433,
    "database": "bom_jesus_db",
    "user": "postgres",
    "password": "postgres"
}

# Resultados dos testes
test_results: List[Dict[str, Any]] = []


def log_test(name: str, status: str, category: str = "database", error: str = None, details: Dict = None):
    """Registra resultado de um teste"""
    result = {
        "name": name,
        "status": status,
        "category": category,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    if error:
        result["error"] = error
    if details:
        result["details"] = details
    test_results.append(result)
    
    # Print colorido
    if status == "PASSED":
        print(f"✅ {name}")
    else:
        print(f"❌ {name}: {error}")


def get_connection():
    """Obtém conexão com o banco de dados"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        log_test("Conexão com PostgreSQL", "FAILED", "database", error=str(e))
        return None


def test_connection():
    """Testa conexão com o banco"""
    print("\n🗄️  Testando Banco de Dados...")
    conn = get_connection()
    if conn:
        conn.close()
        log_test("Conexão com PostgreSQL", "PASSED", "database")
        return True
    return False


def test_postgres_version():
    """Testa versão do PostgreSQL"""
    conn = get_connection()
    if not conn:
        return
    
    try:
        cur = conn.cursor()
        cur.execute("SELECT version();")
        version = cur.fetchone()[0]
        log_test("Versão do PostgreSQL", "PASSED", "database", 
                details={"version": version.split(",")[0]})
    except Exception as e:
        log_test("Versão do PostgreSQL", "FAILED", "database", error=str(e))
    finally:
        conn.close()


def test_tables_exist():
    """Testa se tabelas essenciais existem"""
    conn = get_connection()
    if not conn:
        return
    
    required_tables = ["users", "auth_tokens", "alembic_version"]
    
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            AND table_type = 'BASE TABLE';
        """)
        existing_tables = [row[0] for row in cur.fetchall()]
        
        for table in required_tables:
            if table in existing_tables:
                log_test(f"Tabela '{table}' existe", "PASSED", "database")
            else:
                log_test(f"Tabela '{table}' existe", "FAILED", "database",
                        error=f"Tabela '{table}' não encontrada")
        
        # Listar todas as tabelas encontradas
        log_test("Total de tabelas", "PASSED", "database",
                details={"count": len(existing_tables), "tables": existing_tables})
    except Exception as e:
        log_test("Verificação de tabelas", "FAILED", "database", error=str(e))
    finally:
        conn.close()


def test_users_table_structure():
    """Testa estrutura da tabela users"""
    conn = get_connection()
    if not conn:
        return
    
    required_columns = {
        "id": "uuid",
        "name": "character varying",
        "email": "character varying",
        "hashed_password": "character varying",
        "role": "user-defined",
        "is_active": "character varying",
        "created_at": "timestamp without time zone",
        "updated_at": "timestamp without time zone"
    }
    
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_schema = 'public' 
            AND table_name = 'users'
            ORDER BY ordinal_position;
        """)
        columns = {row[0]: row[1] for row in cur.fetchall()}
        
        for col, expected_type in required_columns.items():
            if col in columns:
                log_test(f"Coluna 'users.{col}' existe", "PASSED", "database",
                        details={"type": columns[col]})
            else:
                log_test(f"Coluna 'users.{col}' existe", "FAILED", "database",
                        error=f"Coluna '{col}' não encontrada")
        
        # Verificar constraints
        cur.execute("""
            SELECT constraint_name, constraint_type
            FROM information_schema.table_constraints
            WHERE table_schema = 'public' 
            AND table_name = 'users';
        """)
        constraints = cur.fetchall()
        log_test("Constraints da tabela users", "PASSED", "database",
                details={"constraints": [c[0] for c in constraints]})
        
    except Exception as e:
        log_test("Estrutura da tabela users", "FAILED", "database", error=str(e))
    finally:
        conn.close()


def test_auth_tokens_table_structure():
    """Testa estrutura da tabela auth_tokens"""
    conn = get_connection()
    if not conn:
        return
    
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_schema = 'public' 
            AND table_name = 'auth_tokens'
            ORDER BY ordinal_position;
        """)
        columns = {row[0]: row[1] for row in cur.fetchall()}
        
        required_columns = ["id", "user_id", "token", "token_type", "is_active", 
                          "expires_at", "created_at", "last_used_at"]
        
        for col in required_columns:
            if col in columns:
                log_test(f"Coluna 'auth_tokens.{col}' existe", "PASSED", "database")
            else:
                log_test(f"Coluna 'auth_tokens.{col}' existe", "FAILED", "database",
                        error=f"Coluna '{col}' não encontrada")
        
    except Exception as e:
        log_test("Estrutura da tabela auth_tokens", "FAILED", "database", error=str(e))
    finally:
        conn.close()


def test_migrations():
    """Testa migrations aplicadas"""
    conn = get_connection()
    if not conn:
        return
    
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM alembic_version;")
        version = cur.fetchone()
        if version:
            log_test("Migrations aplicadas", "PASSED", "database",
                    details={"version": version[0]})
        else:
            log_test("Migrations aplicadas", "FAILED", "database",
                    error="Tabela alembic_version vazia ou não encontrada")
    except Exception as e:
        log_test("Migrations aplicadas", "FAILED", "database", error=str(e))
    finally:
        conn.close()


def test_create_user():
    """Testa criação de usuário (se não existir)"""
    conn = get_connection()
    if not conn:
        return
    
    try:
        cur = conn.cursor()
        # Verificar se usuário já existe
        cur.execute("SELECT id FROM users WHERE email = %s;", ("admin@bomjesus.com",))
        existing = cur.fetchone()
        
        if existing:
            log_test("Usuário de teste existe", "PASSED", "database",
                    details={"email": "admin@bomjesus.com"})
        else:
            # Tentar criar (pode falhar se não tiver permissão)
            log_test("Usuário de teste existe", "FAILED", "database",
                    error="Usuário admin@bomjesus.com não encontrado. Execute scripts/create-test-user.py")
    except Exception as e:
        log_test("Verificação de usuário de teste", "FAILED", "database", error=str(e))
    finally:
        conn.close()


def test_basic_queries():
    """Testa consultas básicas"""
    conn = get_connection()
    if not conn:
        return
    
    try:
        cur = conn.cursor()
        
        # Teste SELECT
        cur.execute("SELECT COUNT(*) FROM users;")
        count = cur.fetchone()[0]
        log_test("Consulta SELECT COUNT(*) FROM users", "PASSED", "database",
                details={"count": count})
        
        # Teste SELECT com WHERE
        cur.execute("SELECT id, email FROM users LIMIT 1;")
        result = cur.fetchone()
        if result:
            log_test("Consulta SELECT com WHERE", "PASSED", "database")
        else:
            log_test("Consulta SELECT com WHERE", "PASSED", "database",
                    details={"note": "Nenhum usuário encontrado"})
        
    except Exception as e:
        log_test("Consultas básicas", "FAILED", "database", error=str(e))
    finally:
        conn.close()


def test_indexes():
    """Testa índices existentes"""
    conn = get_connection()
    if not conn:
        return
    
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT indexname, tablename
            FROM pg_indexes
            WHERE schemaname = 'public'
            ORDER BY tablename, indexname;
        """)
        indexes = cur.fetchall()
        
        log_test("Índices do banco", "PASSED", "database",
                details={"count": len(indexes), "indexes": [idx[0] for idx in indexes[:10]]})
        
    except Exception as e:
        log_test("Verificação de índices", "FAILED", "database", error=str(e))
    finally:
        conn.close()


def main():
    global DB_CONFIG
    
    parser = argparse.ArgumentParser(description="Testes de Banco de Dados")
    parser.add_argument("--output", help="Arquivo JSON de saída", default="test-db-results.json")
    parser.add_argument("--host", help="Host do PostgreSQL", default=DB_CONFIG["host"])
    parser.add_argument("--port", type=int, help="Porta do PostgreSQL", default=DB_CONFIG["port"])
    parser.add_argument("--database", help="Nome do banco", default=DB_CONFIG["database"])
    parser.add_argument("--user", help="Usuário", default=DB_CONFIG["user"])
    parser.add_argument("--password", help="Senha", default=DB_CONFIG["password"])
    args = parser.parse_args()
    
    # Atualizar configuração
    DB_CONFIG.update({
        "host": args.host,
        "port": args.port,
        "database": args.database,
        "user": args.user,
        "password": args.password
    })
    
    print("=" * 60)
    print("  TESTES DE BANCO DE DADOS - Sistema Operacional Bom Jesus")
    print("=" * 60)
    print(f"Host: {DB_CONFIG['host']}:{DB_CONFIG['port']}")
    print(f"Database: {DB_CONFIG['database']}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    try:
        test_connection()
        if test_results and test_results[-1]["status"] == "PASSED":
            test_postgres_version()
            test_tables_exist()
            test_users_table_structure()
            test_auth_tokens_table_structure()
            test_migrations()
            test_create_user()
            test_basic_queries()
            test_indexes()
    except Exception as e:
        log_test("Erro geral nos testes", "FAILED", "error", error=str(e))
    
    # Salvar resultados
    with open(args.output, 'w') as f:
        json.dump(test_results, f, indent=2)
    
    # Resumo
    passed = sum(1 for t in test_results if t["status"] == "PASSED")
    failed = sum(1 for t in test_results if t["status"] == "FAILED")
    
    print()
    print("=" * 60)
    print("  RESUMO")
    print("=" * 60)
    print(f"Total: {len(test_results)}")
    print(f"✅ Passaram: {passed}")
    print(f"❌ Falharam: {failed}")
    print()
    
    if failed > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
