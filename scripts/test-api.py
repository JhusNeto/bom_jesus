#!/usr/bin/env python3
"""
Script de Testes de API - Sistema Operacional Bom Jesus
Testa todos os endpoints HTTP e autenticação
"""
import sys
import json
import argparse
import requests
from datetime import datetime
from typing import Dict, List, Any
from urllib.parse import urljoin

# Configurações
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

# Credenciais de teste
TEST_EMAIL = "admin@bomjesus.com"
TEST_PASSWORD = "admin123"

# Resultados dos testes
test_results: List[Dict[str, Any]] = []


def log_test(name: str, status: str, category: str = "api", error: str = None, details: Dict = None):
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


def test_endpoint(method: str, endpoint: str, expected_status: int = 200, 
                  headers: Dict = None, data: Dict = None, json_data: Dict = None,
                  name: str = None, category: str = "api") -> requests.Response:
    """Testa um endpoint HTTP"""
    if name is None:
        name = f"{method} {endpoint}"
    
    try:
        url = urljoin(API_BASE if endpoint.startswith("/") else BASE_URL, endpoint)
        response = requests.request(
            method=method,
            url=url,
            headers=headers or {},
            data=data,
            json=json_data,
            timeout=10
        )
        
        if response.status_code == expected_status:
            log_test(name, "PASSED", category, details={"status_code": response.status_code})
            return response
        else:
            error_msg = f"Status esperado {expected_status}, recebido {response.status_code}"
            if response.text:
                error_msg += f": {response.text[:200]}"
            log_test(name, "FAILED", category, error=error_msg)
            return response
    except requests.exceptions.RequestException as e:
        log_test(name, "FAILED", category, error=str(e))
        raise


# ============================================
# TESTES DE ENDPOINTS BÁSICOS
# ============================================

def test_root_endpoint():
    """Testa endpoint raiz"""
    print("\n📡 Testando Endpoints Básicos...")
    test_endpoint("GET", "/", name="GET / (Endpoint raiz)", category="api_basic")


def test_health_endpoint():
    """Testa health check"""
    response = test_endpoint("GET", "/api/v1/health", name="GET /api/v1/health", category="api_basic")
    if response and response.status_code == 200:
        data = response.json()
        if data.get("status") != "healthy":
            log_test("Health check status", "FAILED", "api_basic", 
                    error=f"Status não é 'healthy': {data.get('status')}")


def test_readiness_endpoint():
    """Testa readiness check"""
    test_endpoint("GET", "/api/v1/health/ready", name="GET /api/v1/health/ready", category="api_basic")


def test_db_health_endpoint():
    """Testa database health check"""
    response = test_endpoint("GET", "/api/v1/db/health", name="GET /api/v1/db/health", category="api_basic")
    if response and response.status_code == 200:
        data = response.json()
        if data.get("status") != "ok":
            log_test("DB health check status", "FAILED", "api_basic",
                    error=f"Status não é 'ok': {data.get('status')}")


def test_swagger_ui():
    """Testa Swagger UI"""
    test_endpoint("GET", "/docs", name="GET /docs (Swagger UI)", category="api_basic")


def test_redoc():
    """Testa ReDoc"""
    test_endpoint("GET", "/redoc", name="GET /redoc (ReDoc)", category="api_basic")


def test_openapi_json():
    """Testa OpenAPI JSON"""
    response = test_endpoint("GET", "/openapi.json", name="GET /openapi.json", category="api_basic")
    if response and response.status_code == 200:
        try:
            data = response.json()
            if "openapi" not in data:
                log_test("OpenAPI schema válido", "FAILED", "api_basic",
                        error="Resposta não é um schema OpenAPI válido")
        except json.JSONDecodeError:
            log_test("OpenAPI JSON válido", "FAILED", "api_basic",
                    error="Resposta não é JSON válido")


# ============================================
# TESTES DE AUTENTICAÇÃO
# ============================================

def test_login_valid():
    """Testa login com credenciais válidas"""
    print("\n🔐 Testando Autenticação...")
    response = test_endpoint(
        "POST",
        "/api/v1/auth/login",
        expected_status=200,
        json_data={"email": TEST_EMAIL, "password": TEST_PASSWORD},
        name="POST /auth/login (credenciais válidas)",
        category="auth"
    )
    
    if response and response.status_code == 200:
        data = response.json()
        if "access_token" not in data or "refresh_token" not in data:
            log_test("Login retorna tokens", "FAILED", "auth",
                    error="Resposta não contém access_token ou refresh_token")
        else:
            # Salvar tokens para outros testes
            test_login_valid.access_token = data.get("access_token")
            test_login_valid.refresh_token = data.get("refresh_token")
            test_login_valid.user_id = data.get("user", {}).get("id")
    return response


def test_login_invalid():
    """Testa login com credenciais inválidas"""
    test_endpoint(
        "POST",
        "/api/v1/auth/login",
        expected_status=401,
        json_data={"email": "invalid@test.com", "password": "wrongpassword"},
        name="POST /auth/login (credenciais inválidas)",
        category="auth"
    )


def test_get_me_with_token():
    """Testa GET /auth/me com token válido"""
    if not hasattr(test_login_valid, 'access_token'):
        log_test("GET /auth/me (com token)", "SKIPPED", "auth",
                error="Token não disponível (login falhou)")
        return
    
    headers = {"Authorization": f"Bearer {test_login_valid.access_token}"}
    response = test_endpoint(
        "GET",
        "/api/v1/auth/me",
        expected_status=200,
        headers=headers,
        name="GET /auth/me (com token válido)",
        category="auth"
    )
    
    if response and response.status_code == 200:
        data = response.json()
        if "email" not in data or "id" not in data:
            log_test("GET /auth/me retorna dados do usuário", "FAILED", "auth",
                    error="Resposta não contém dados do usuário")


def test_get_me_without_token():
    """Testa GET /auth/me sem token"""
    test_endpoint(
        "GET",
        "/api/v1/auth/me",
        expected_status=401,
        name="GET /auth/me (sem token)",
        category="auth"
    )


def test_get_me_invalid_token():
    """Testa GET /auth/me com token inválido"""
    headers = {"Authorization": "Bearer invalid_token_12345"}
    test_endpoint(
        "GET",
        "/api/v1/auth/me",
        expected_status=401,
        headers=headers,
        name="GET /auth/me (token inválido)",
        category="auth"
    )


def test_refresh_token_valid():
    """Testa refresh token válido"""
    if not hasattr(test_login_valid, 'refresh_token'):
        log_test("POST /auth/refresh (token válido)", "SKIPPED", "auth",
                error="Refresh token não disponível (login falhou)")
        return
    
    response = test_endpoint(
        "POST",
        "/api/v1/auth/refresh",
        expected_status=200,
        json_data={"refresh_token": test_login_valid.refresh_token},
        name="POST /auth/refresh (token válido)",
        category="auth"
    )
    
    if response and response.status_code == 200:
        data = response.json()
        if "access_token" not in data:
            log_test("Refresh retorna novo access_token", "FAILED", "auth",
                    error="Resposta não contém access_token")
        else:
            test_refresh_token_valid.new_access_token = data.get("access_token")


def test_refresh_token_invalid():
    """Testa refresh token inválido"""
    test_endpoint(
        "POST",
        "/api/v1/auth/refresh",
        expected_status=401,
        json_data={"refresh_token": "invalid_refresh_token_12345"},
        name="POST /auth/refresh (token inválido)",
        category="auth"
    )


def test_logout():
    """Testa logout"""
    if not hasattr(test_login_valid, 'refresh_token'):
        log_test("POST /auth/logout", "SKIPPED", "auth",
                error="Refresh token não disponível (login falhou)")
        return
    
    if not hasattr(test_login_valid, 'access_token'):
        log_test("POST /auth/logout", "SKIPPED", "auth",
                error="Access token não disponível (login falhou)")
        return
    
    headers = {"Authorization": f"Bearer {test_login_valid.access_token}"}
    response = test_endpoint(
        "POST",
        "/api/v1/auth/logout",
        expected_status=200,
        headers=headers,
        json_data={"refresh_token": test_login_valid.refresh_token},
        name="POST /auth/logout",
        category="auth"
    )
    
    # Após logout, refresh token não deve funcionar
    if response and response.status_code == 200:
        test_endpoint(
            "POST",
            "/api/v1/auth/refresh",
            expected_status=401,
            json_data={"refresh_token": test_login_valid.refresh_token},
            name="POST /auth/refresh (após logout - deve falhar)",
            category="auth"
        )


# ============================================
# MAIN
# ============================================

def main():
    global BASE_URL, API_BASE
    
    parser = argparse.ArgumentParser(description="Testes de API")
    parser.add_argument("--output", help="Arquivo JSON de saída", default="test-api-results.json")
    parser.add_argument("--base-url", help="URL base da API", default=BASE_URL)
    args = parser.parse_args()
    
    BASE_URL = args.base_url
    API_BASE = f"{BASE_URL}/api/v1"
    
    print("=" * 60)
    print("  TESTES DE API - Sistema Operacional Bom Jesus")
    print("=" * 60)
    print(f"Base URL: {BASE_URL}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    try:
        # Testes básicos
        test_root_endpoint()
        test_health_endpoint()
        test_readiness_endpoint()
        test_db_health_endpoint()
        test_swagger_ui()
        test_redoc()
        test_openapi_json()
        
        # Testes de autenticação
        test_login_valid()
        test_login_invalid()
        test_get_me_with_token()
        test_get_me_without_token()
        test_get_me_invalid_token()
        test_refresh_token_valid()
        test_refresh_token_invalid()
        test_logout()
        
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
