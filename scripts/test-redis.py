#!/usr/bin/env python3
"""
Script de Testes de Redis - Sistema Operacional Bom Jesus
Testa conexão e operações de refresh tokens
"""
import sys
import json
import argparse
from datetime import datetime
from typing import Dict, List, Any
import time

try:
    import redis
except ImportError:
    print("❌ redis não instalado. Execute: pip install redis")
    sys.exit(1)

# Configurações padrão
REDIS_CONFIG = {
    "host": "localhost",
    "port": 6379,
    "db": 0,
    "decode_responses": True
}

# Resultados dos testes
test_results: List[Dict[str, Any]] = []


def log_test(name: str, status: str, category: str = "redis", error: str = None, details: Dict = None):
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


def get_redis_client():
    """Obtém cliente Redis"""
    try:
        r = redis.Redis(**REDIS_CONFIG, socket_connect_timeout=5)
        return r
    except Exception as e:
        log_test("Conexão com Redis", "FAILED", "redis", error=str(e))
        return None


def test_connection():
    """Testa conexão com Redis"""
    print("\n🔴 Testando Redis...")
    r = get_redis_client()
    if not r:
        return False
    
    try:
        r.ping()
        log_test("Conexão com Redis", "PASSED", "redis")
        r.close()
        return True
    except Exception as e:
        log_test("Conexão com Redis", "FAILED", "redis", error=str(e))
        return False


def test_ping():
    """Testa operação PING"""
    r = get_redis_client()
    if not r:
        return
    
    try:
        result = r.ping()
        if result:
            log_test("Redis PING", "PASSED", "redis")
        else:
            log_test("Redis PING", "FAILED", "redis", error="PING não retornou True")
    except Exception as e:
        log_test("Redis PING", "FAILED", "redis", error=str(e))
    finally:
        r.close()


def test_save_refresh_token():
    """Testa salvar refresh token"""
    r = get_redis_client()
    if not r:
        return
    
    test_user_id = "test-user-123"
    test_token = "test-refresh-token-12345"
    ttl = 3600  # 1 hora
    
    try:
        key = f"refresh_token:{test_user_id}:{test_token}"
        r.setex(key, ttl, "1")
        
        # Verificar se foi salvo
        exists = r.exists(key)
        if exists:
            log_test("Salvar refresh token", "PASSED", "redis",
                    details={"key": key, "ttl": ttl})
            test_save_refresh_token.test_key = key
            test_save_refresh_token.test_user_id = test_user_id
            test_save_refresh_token.test_token = test_token
        else:
            log_test("Salvar refresh token", "FAILED", "redis",
                    error="Token não foi salvo")
    except Exception as e:
        log_test("Salvar refresh token", "FAILED", "redis", error=str(e))
    finally:
        r.close()


def test_verify_refresh_token():
    """Testa verificar refresh token"""
    if not hasattr(test_save_refresh_token, 'test_key'):
        log_test("Verificar refresh token", "SKIPPED", "redis",
                error="Token de teste não disponível")
        return
    
    r = get_redis_client()
    if not r:
        return
    
    try:
        exists = r.exists(test_save_refresh_token.test_key)
        if exists:
            log_test("Verificar refresh token", "PASSED", "redis")
        else:
            log_test("Verificar refresh token", "FAILED", "redis",
                    error="Token não encontrado")
    except Exception as e:
        log_test("Verificar refresh token", "FAILED", "redis", error=str(e))
    finally:
        r.close()


def test_ttl_refresh_token():
    """Testa TTL de refresh token"""
    if not hasattr(test_save_refresh_token, 'test_key'):
        log_test("TTL de refresh token", "SKIPPED", "redis",
                error="Token de teste não disponível")
        return
    
    r = get_redis_client()
    if not r:
        return
    
    try:
        ttl = r.ttl(test_save_refresh_token.test_key)
        if ttl > 0:
            log_test("TTL de refresh token", "PASSED", "redis",
                    details={"ttl_seconds": ttl})
        else:
            log_test("TTL de refresh token", "FAILED", "redis",
                    error=f"TTL inválido: {ttl}")
    except Exception as e:
        log_test("TTL de refresh token", "FAILED", "redis", error=str(e))
    finally:
        r.close()


def test_revoke_refresh_token():
    """Testa revogar refresh token"""
    if not hasattr(test_save_refresh_token, 'test_key'):
        log_test("Revogar refresh token", "SKIPPED", "redis",
                error="Token de teste não disponível")
        return
    
    r = get_redis_client()
    if not r:
        return
    
    try:
        deleted = r.delete(test_save_refresh_token.test_key)
        if deleted > 0:
            log_test("Revogar refresh token", "PASSED", "redis")
        else:
            log_test("Revogar refresh token", "FAILED", "redis",
                    error="Token não foi deletado")
    except Exception as e:
        log_test("Revogar refresh token", "FAILED", "redis", error=str(e))
    finally:
        r.close()


def test_revoke_all_tokens():
    """Testa revogar todos os tokens de um usuário"""
    r = get_redis_client()
    if not r:
        return
    
    test_user_id = "test-user-revoke-all"
    
    try:
        # Criar alguns tokens de teste
        tokens = [f"token-{i}" for i in range(3)]
        for token in tokens:
            key = f"refresh_token:{test_user_id}:{token}"
            r.setex(key, 3600, "1")
        
        # Revogar todos
        pattern = f"refresh_token:{test_user_id}:*"
        keys = r.keys(pattern)
        if keys:
            deleted = r.delete(*keys)
            if deleted == len(tokens):
                log_test("Revogar todos os tokens", "PASSED", "redis",
                        details={"deleted_count": deleted})
            else:
                log_test("Revogar todos os tokens", "FAILED", "redis",
                        error=f"Esperado deletar {len(tokens)}, deletou {deleted}")
        else:
            log_test("Revogar todos os tokens", "FAILED", "redis",
                    error="Nenhum token encontrado para revogar")
    except Exception as e:
        log_test("Revogar todos os tokens", "FAILED", "redis", error=str(e))
    finally:
        r.close()


def test_info():
    """Testa comando INFO"""
    r = get_redis_client()
    if not r:
        return
    
    try:
        info = r.info()
        if info:
            log_test("Redis INFO", "PASSED", "redis",
                    details={"redis_version": info.get("redis_version", "unknown")})
        else:
            log_test("Redis INFO", "FAILED", "redis", error="INFO não retornou dados")
    except Exception as e:
        log_test("Redis INFO", "FAILED", "redis", error=str(e))
    finally:
        r.close()


def main():
    global REDIS_CONFIG
    
    parser = argparse.ArgumentParser(description="Testes de Redis")
    parser.add_argument("--output", help="Arquivo JSON de saída", default="test-redis-results.json")
    parser.add_argument("--host", help="Host do Redis", default=REDIS_CONFIG["host"])
    parser.add_argument("--port", type=int, help="Porta do Redis", default=REDIS_CONFIG["port"])
    parser.add_argument("--db", type=int, help="Database number", default=REDIS_CONFIG["db"])
    args = parser.parse_args()
    
    # Atualizar configuração
    REDIS_CONFIG.update({
        "host": args.host,
        "port": args.port,
        "db": args.db
    })
    
    print("=" * 60)
    print("  TESTES DE REDIS - Sistema Operacional Bom Jesus")
    print("=" * 60)
    print(f"Host: {REDIS_CONFIG['host']}:{REDIS_CONFIG['port']}")
    print(f"Database: {REDIS_CONFIG['db']}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    try:
        if test_connection():
            test_ping()
            test_save_refresh_token()
            test_verify_refresh_token()
            test_ttl_refresh_token()
            test_revoke_refresh_token()
            test_revoke_all_tokens()
            test_info()
    except Exception as e:
        log_test("Erro geral nos testes", "FAILED", "error", error=str(e))
    
    # Salvar resultados
    with open(args.output, 'w') as f:
        json.dump(test_results, f, indent=2)
    
    # Resumo
    passed = sum(1 for t in test_results if t["status"] == "PASSED")
    failed = sum(1 for t in test_results if t["status"] == "FAILED")
    skipped = sum(1 for t in test_results if t["status"] == "SKIPPED")
    
    print()
    print("=" * 60)
    print("  RESUMO")
    print("=" * 60)
    print(f"Total: {len(test_results)}")
    print(f"✅ Passaram: {passed}")
    print(f"❌ Falharam: {failed}")
    print(f"⏭️  Pulados: {skipped}")
    print()
    
    if failed > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()

