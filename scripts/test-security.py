#!/usr/bin/env python3
"""
Script de Teste de Segurança - Sistema Operacional Bom Jesus
Testa JWT, hash de senhas, proteção de rotas, CORS, refresh token whitelist
"""
import sys
import os
import requests
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.security import (
    create_access_token, create_refresh_token,
    decode_access_token, decode_refresh_token,
    verify_password, get_password_hash,
    get_current_user
)
from app.core.config import settings

# Configurações
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

# Credenciais de teste
TEST_EMAIL = "admin@bomjesus.com"
TEST_PASSWORD = "admin123"

# Resultados
test_results: List[Dict[str, Any]] = []


def log_test(name: str, status: str, error: str = None, details: Dict = None):
    """Registra resultado de um teste"""
    result = {
        "name": name,
        "status": status,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    if error:
        result["error"] = error
    if details:
        result["details"] = details
    test_results.append(result)
    
    if status == "PASSED":
        print(f"✅ {name}")
    else:
        print(f"❌ {name}: {error}")


def test_jwt_creation():
    """Testa criação de tokens JWT"""
    print("\n🔐 Testando Criação de Tokens JWT...")
    
    # Teste 1: Access token
    try:
        data = {"sub": TEST_EMAIL, "user_id": "test-id", "role": "ADMIN"}
        token = create_access_token(data)
        if token:
            log_test("Criação de access token", "PASSED", details={"token_length": len(token)})
        else:
            log_test("Criação de access token", "FAILED", "Token não foi criado")
    except Exception as e:
        log_test("Criação de access token", "FAILED", str(e))
    
    # Teste 2: Refresh token
    try:
        data = {"sub": TEST_EMAIL, "user_id": "test-id", "role": "ADMIN"}
        token = create_refresh_token(data)
        if token:
            log_test("Criação de refresh token", "PASSED", details={"token_length": len(token)})
        else:
            log_test("Criação de refresh token", "FAILED", "Token não foi criado")
    except Exception as e:
        log_test("Criação de refresh token", "FAILED", str(e))
    
    # Teste 3: Decodificação de access token
    try:
        data = {"sub": TEST_EMAIL, "user_id": "test-id", "role": "ADMIN"}
        token = create_access_token(data)
        payload = decode_access_token(token)
        if payload and payload.get("type") == "access":
            log_test("Decodificação de access token", "PASSED")
        else:
            log_test("Decodificação de access token", "FAILED", "Token não decodificado ou tipo incorreto")
    except Exception as e:
        log_test("Decodificação de access token", "FAILED", str(e))
    
    # Teste 4: Decodificação de refresh token
    try:
        data = {"sub": TEST_EMAIL, "user_id": "test-id", "role": "ADMIN"}
        token = create_refresh_token(data)
        payload = decode_refresh_token(token)
        if payload and payload.get("type") == "refresh":
            log_test("Decodificação de refresh token", "PASSED")
        else:
            log_test("Decodificação de refresh token", "FAILED", "Token não decodificado ou tipo incorreto")
    except Exception as e:
        log_test("Decodificação de refresh token", "FAILED", str(e))
    
    # Teste 5: Rejeição de token inválido
    try:
        payload = decode_access_token("token_invalido")
        if payload is None:
            log_test("Rejeição de token inválido", "PASSED")
        else:
            log_test("Rejeição de token inválido", "FAILED", "Token inválido foi aceito")
    except Exception as e:
        log_test("Rejeição de token inválido", "FAILED", str(e))
    
    # Teste 6: Verificação de tipo de token (access vs refresh)
    try:
        data = {"sub": TEST_EMAIL, "user_id": "test-id", "role": "ADMIN"}
        access_token = create_access_token(data)
        refresh_token = create_refresh_token(data)
        
        access_payload = decode_access_token(access_token)
        refresh_payload = decode_refresh_token(refresh_token)
        
        if (access_payload and access_payload.get("type") == "access" and
            refresh_payload and refresh_payload.get("type") == "refresh"):
            log_test("Verificação de tipo de token", "PASSED")
        else:
            log_test("Verificação de tipo de token", "FAILED", "Tipos de token incorretos")
    except Exception as e:
        log_test("Verificação de tipo de token", "FAILED", str(e))


def test_password_hashing():
    """Testa hash de senhas"""
    print("\n🔒 Testando Hash de Senhas...")
    
    # Teste 1: Hash de senha
    try:
        password = "test123"
        hashed = get_password_hash(password)
        if hashed and hashed != password:
            log_test("Hash de senha", "PASSED", details={"hash_length": len(hashed)})
        else:
            log_test("Hash de senha", "FAILED", "Hash não foi gerado")
    except Exception as e:
        log_test("Hash de senha", "FAILED", str(e))
    
    # Teste 2: Verificação de senha correta
    try:
        password = "test123"
        hashed = get_password_hash(password)
        if verify_password(password, hashed):
            log_test("Verificação de senha correta", "PASSED")
        else:
            log_test("Verificação de senha correta", "FAILED", "Senha correta foi rejeitada")
    except Exception as e:
        log_test("Verificação de senha correta", "FAILED", str(e))
    
    # Teste 3: Rejeição de senha incorreta
    try:
        password = "test123"
        wrong_password = "wrong123"
        hashed = get_password_hash(password)
        if not verify_password(wrong_password, hashed):
            log_test("Rejeição de senha incorreta", "PASSED")
        else:
            log_test("Rejeição de senha incorreta", "FAILED", "Senha incorreta foi aceita")
    except Exception as e:
        log_test("Rejeição de senha incorreta", "FAILED", str(e))
    
    # Teste 4: Verificar força do hash (salt rounds)
    try:
        password = "test123"
        hashed1 = get_password_hash(password)
        hashed2 = get_password_hash(password)
        # Hashes diferentes indicam salt único
        if hashed1 != hashed2:
            log_test("Salt único em cada hash", "PASSED")
        else:
            log_test("Salt único em cada hash", "FAILED", "Hashes idênticos (sem salt)")
    except Exception as e:
        log_test("Salt único em cada hash", "FAILED", str(e))


def test_route_protection():
    """Testa proteção de rotas"""
    print("\n🛡️ Testando Proteção de Rotas...")
    
    # Teste 1: Endpoint sem token (deve retornar 401)
    try:
        response = requests.get(f"{API_BASE}/auth/me")
        if response.status_code == 401:
            log_test("Endpoint sem token retorna 401", "PASSED")
        else:
            log_test("Endpoint sem token retorna 401", "FAILED", 
                    f"Status code: {response.status_code}")
    except Exception as e:
        log_test("Endpoint sem token retorna 401", "FAILED", str(e))
    
    # Teste 2: Endpoint com token inválido (deve retornar 401)
    try:
        headers = {"Authorization": "Bearer token_invalido"}
        response = requests.get(f"{API_BASE}/auth/me", headers=headers)
        if response.status_code == 401:
            log_test("Endpoint com token inválido retorna 401", "PASSED")
        else:
            log_test("Endpoint com token inválido retorna 401", "FAILED",
                    f"Status code: {response.status_code}")
    except Exception as e:
        log_test("Endpoint com token inválido retorna 401", "FAILED", str(e))
    
    # Teste 3: Endpoint com token válido (deve retornar 200)
    try:
        # Fazer login para obter token válido
        login_response = requests.post(
            f"{API_BASE}/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        if login_response.status_code == 200:
            token = login_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(f"{API_BASE}/auth/me", headers=headers)
            if response.status_code == 200:
                log_test("Endpoint com token válido retorna 200", "PASSED")
            else:
                log_test("Endpoint com token válido retorna 200", "FAILED",
                        f"Status code: {response.status_code}")
        else:
            log_test("Endpoint com token válido retorna 200", "FAILED",
                    "Não foi possível fazer login")
    except Exception as e:
        log_test("Endpoint com token válido retorna 200", "FAILED", str(e))


def test_cors():
    """Testa configuração CORS"""
    print("\n🌐 Testando CORS...")
    
    # Teste 1: Requisição de origem permitida
    try:
        headers = {
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST"
        }
        response = requests.options(f"{API_BASE}/auth/login", headers=headers)
        cors_headers = {
            "access-control-allow-origin": response.headers.get("access-control-allow-origin"),
            "access-control-allow-methods": response.headers.get("access-control-allow-methods"),
            "access-control-allow-credentials": response.headers.get("access-control-allow-credentials")
        }
        if cors_headers["access-control-allow-origin"]:
            log_test("CORS configurado para origem permitida", "PASSED", 
                    details=cors_headers)
        else:
            log_test("CORS configurado para origem permitida", "FAILED",
                    "Headers CORS não encontrados")
    except Exception as e:
        log_test("CORS configurado para origem permitida", "FAILED", str(e))
    
    # Teste 2: Verificar CORS em resposta real
    try:
        headers = {"Origin": "http://localhost:3000"}
        response = requests.post(
            f"{API_BASE}/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
            headers=headers
        )
        if "access-control-allow-origin" in response.headers:
            log_test("Headers CORS em resposta", "PASSED",
                    details={"origin": response.headers.get("access-control-allow-origin")})
        else:
            log_test("Headers CORS em resposta", "FAILED", "Headers CORS não encontrados")
    except Exception as e:
        log_test("Headers CORS em resposta", "FAILED", str(e))


def test_refresh_token_whitelist():
    """Testa refresh token whitelist no Redis"""
    print("\n🔄 Testando Refresh Token Whitelist...")
    
    # Teste 1: Login e verificar refresh token salvo
    try:
        response = requests.post(
            f"{API_BASE}/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        if response.status_code == 200:
            data = response.json()
            refresh_token = data.get("refresh_token")
            if refresh_token:
                log_test("Refresh token retornado no login", "PASSED")
                
                # Teste 2: Usar refresh token válido
                refresh_response = requests.post(
                    f"{API_BASE}/auth/refresh",
                    json={"refresh_token": refresh_token}
                )
                if refresh_response.status_code == 200:
                    log_test("Refresh token válido funciona", "PASSED")
                else:
                    log_test("Refresh token válido funciona", "FAILED",
                            f"Status: {refresh_response.status_code}")
            else:
                log_test("Refresh token retornado no login", "FAILED",
                        "Refresh token não retornado")
        else:
            log_test("Refresh token retornado no login", "FAILED",
                    f"Login falhou: {response.status_code}")
    except Exception as e:
        log_test("Refresh token retornado no login", "FAILED", str(e))
    
    # Teste 3: Logout e verificar revogação
    try:
        # Login
        login_response = requests.post(
            f"{API_BASE}/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        if login_response.status_code == 200:
            data = login_response.json()
            refresh_token = data["refresh_token"]
            access_token = data["access_token"]
            
            # Logout
            logout_response = requests.post(
                f"{API_BASE}/auth/logout",
                json={"refresh_token": refresh_token},
                headers={"Authorization": f"Bearer {access_token}"}
            )
            if logout_response.status_code == 200:
                # Tentar usar refresh token revogado
                refresh_response = requests.post(
                    f"{API_BASE}/auth/refresh",
                    json={"refresh_token": refresh_token}
                )
                if refresh_response.status_code != 200:
                    log_test("Refresh token revogado não funciona", "PASSED")
                else:
                    log_test("Refresh token revogado não funciona", "FAILED",
                            "Refresh token revogado ainda funciona")
            else:
                log_test("Logout funciona", "FAILED",
                        f"Status: {logout_response.status_code}")
    except Exception as e:
        log_test("Logout funciona", "FAILED", str(e))


def main():
    """Executa todos os testes de segurança"""
    print("=" * 60)
    print("🔐 BATERIA DE TESTES DE SEGURANÇA")
    print("=" * 60)
    
    test_jwt_creation()
    test_password_hashing()
    test_route_protection()
    test_cors()
    test_refresh_token_whitelist()
    
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
    print(f"Taxa de sucesso: {(passed/total*100):.1f}%")
    
    if failed > 0:
        print("\n❌ Testes que falharam:")
        for test in test_results:
            if test["status"] == "FAILED":
                print(f"  - {test['name']}: {test.get('error', 'Sem detalhes')}")
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

