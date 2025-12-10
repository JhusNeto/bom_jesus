#!/usr/bin/env python3
"""
Script de Teste Geral - Integração Frontend/Backend, Fluxos Completos, Performance
"""
import sys
import os
import requests
import time
from datetime import datetime
from typing import Dict, Any, List

BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"
FRONTEND_URL = "http://localhost:3000"

TEST_EMAIL = "admin@bomjesus.com"
TEST_PASSWORD = "admin123"

test_results: List[Dict[str, Any]] = []


def log_test(name: str, status: str, error: str = None, details: Dict = None):
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


def test_frontend_backend_communication():
    """Testa comunicação frontend/backend"""
    print("\n🌐 Testando Comunicação Frontend/Backend...")
    
    # Teste 1: Frontend acessível
    try:
        resp = requests.get(FRONTEND_URL, timeout=5)
        if resp.status_code == 200:
            log_test("Frontend acessível", "PASSED")
        else:
            log_test("Frontend acessível", "FAILED", f"Status: {resp.status_code}")
    except requests.exceptions.RequestException as e:
        log_test("Frontend acessível", "FAILED", str(e))
    
    # Teste 2: Backend acessível do frontend
    try:
        resp = requests.get(f"{API_BASE}/health", timeout=5)
        if resp.status_code == 200:
            log_test("Backend acessível", "PASSED")
        else:
            log_test("Backend acessível", "FAILED", f"Status: {resp.status_code}")
    except requests.exceptions.RequestException as e:
        log_test("Backend acessível", "FAILED", str(e))


def test_complete_login_flow():
    """Testa fluxo completo de login"""
    print("\n🔐 Testando Fluxo Completo de Login...")
    
    try:
        # 1. Login
        login_resp = requests.post(
            f"{API_BASE}/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        if login_resp.status_code != 200:
            log_test("Fluxo de login - Login", "FAILED", f"Status: {login_resp.status_code}")
            return
        
        data = login_resp.json()
        access_token = data.get("access_token")
        refresh_token = data.get("refresh_token")
        
        if not access_token or not refresh_token:
            log_test("Fluxo de login - Tokens retornados", "FAILED", "Tokens não retornados")
            return
        
        log_test("Fluxo de login - Login", "PASSED")
        
        # 2. Obter dados do usuário
        headers = {"Authorization": f"Bearer {access_token}"}
        me_resp = requests.get(f"{API_BASE}/auth/me", headers=headers)
        if me_resp.status_code == 200:
            user_data = me_resp.json()
            if user_data.get("email") == TEST_EMAIL:
                log_test("Fluxo de login - Obter dados do usuário", "PASSED")
            else:
                log_test("Fluxo de login - Obter dados do usuário", "FAILED", "Email incorreto")
        else:
            log_test("Fluxo de login - Obter dados do usuário", "FAILED", f"Status: {me_resp.status_code}")
        
        # 3. Refresh token
        refresh_resp = requests.post(
            f"{API_BASE}/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        if refresh_resp.status_code == 200:
            new_token = refresh_resp.json().get("access_token")
            if new_token:
                log_test("Fluxo de login - Refresh token", "PASSED")
            else:
                log_test("Fluxo de login - Refresh token", "FAILED", "Novo token não retornado")
        else:
            log_test("Fluxo de login - Refresh token", "FAILED", f"Status: {refresh_resp.status_code}")
        
        # 4. Logout
        logout_resp = requests.post(
            f"{API_BASE}/auth/logout",
            json={"refresh_token": refresh_token},
            headers=headers
        )
        if logout_resp.status_code == 200:
            log_test("Fluxo de login - Logout", "PASSED")
        else:
            log_test("Fluxo de login - Logout", "FAILED", f"Status: {logout_resp.status_code}")
        
    except Exception as e:
        log_test("Fluxo completo de login", "FAILED", str(e))


def test_protected_route_access():
    """Testa acesso a rotas protegidas"""
    print("\n🛡️ Testando Acesso a Rotas Protegidas...")
    
    try:
        # Login
        login_resp = requests.post(
            f"{API_BASE}/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        if login_resp.status_code != 200:
            log_test("Acesso a rotas protegidas", "FAILED", "Login falhou")
            return
        
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Acessar endpoint protegido
        audit_resp = requests.get(f"{API_BASE}/audit/logs?limit=5", headers=headers)
        if audit_resp.status_code == 200:
            log_test("Acesso a rotas protegidas - Sucesso", "PASSED")
        else:
            log_test("Acesso a rotas protegidas - Sucesso", "FAILED", f"Status: {audit_resp.status_code}")
        
        # Tentar sem token
        no_token_resp = requests.get(f"{API_BASE}/audit/logs")
        if no_token_resp.status_code == 401:
            log_test("Acesso a rotas protegidas - Sem token", "PASSED")
        else:
            log_test("Acesso a rotas protegidas - Sem token", "FAILED", f"Status: {no_token_resp.status_code}")
        
    except Exception as e:
        log_test("Acesso a rotas protegidas", "FAILED", str(e))


def test_role_based_access():
    """Testa acesso baseado em roles"""
    print("\n👥 Testando Acesso Baseado em Roles...")
    
    # Testar como OPERATOR (deve ser bloqueado em /audit)
    try:
        operator_login = requests.post(
            f"{API_BASE}/auth/login",
            json={"email": "operador@bomjesus.com", "password": "operador123"}
        )
        if operator_login.status_code == 200:
            operator_token = operator_login.json()["access_token"]
            operator_headers = {"Authorization": f"Bearer {operator_token}"}
            
            audit_resp = requests.get(f"{API_BASE}/audit/logs", headers=operator_headers)
            if audit_resp.status_code == 403:
                log_test("Acesso baseado em roles - OPERATOR bloqueado", "PASSED")
            else:
                log_test("Acesso baseado em roles - OPERATOR bloqueado", "FAILED",
                        f"Status: {audit_resp.status_code} (esperado 403)")
        else:
            log_test("Acesso baseado em roles - OPERATOR bloqueado", "FAILED", "Login falhou")
    except Exception as e:
        log_test("Acesso baseado em roles - OPERATOR bloqueado", "FAILED", str(e))
    
    # Testar como ADMIN (deve ter acesso)
    try:
        admin_login = requests.post(
            f"{API_BASE}/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        if admin_login.status_code == 200:
            admin_token = admin_login.json()["access_token"]
            admin_headers = {"Authorization": f"Bearer {admin_token}"}
            
            audit_resp = requests.get(f"{API_BASE}/audit/logs", headers=admin_headers)
            if audit_resp.status_code == 200:
                log_test("Acesso baseado em roles - ADMIN permitido", "PASSED")
            else:
                log_test("Acesso baseado em roles - ADMIN permitido", "FAILED",
                        f"Status: {audit_resp.status_code}")
    except Exception as e:
        log_test("Acesso baseado em roles - ADMIN permitido", "FAILED", str(e))


def test_performance():
    """Testa performance básica"""
    print("\n⚡ Testando Performance Básica...")
    
    # Teste 1: Health check rápido
    try:
        start = time.time()
        resp = requests.get(f"{API_BASE}/health", timeout=5)
        elapsed = time.time() - start
        
        if resp.status_code == 200 and elapsed < 1.0:
            log_test("Health check rápido", "PASSED", details={"time_ms": f"{elapsed*1000:.2f}"})
        else:
            log_test("Health check rápido", "FAILED", f"Tempo: {elapsed:.2f}s")
    except Exception as e:
        log_test("Health check rápido", "FAILED", str(e))
    
    # Teste 2: Login rápido
    try:
        start = time.time()
        resp = requests.post(
            f"{API_BASE}/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        elapsed = time.time() - start
        
        if resp.status_code == 200 and elapsed < 2.0:
            log_test("Login rápido", "PASSED", details={"time_ms": f"{elapsed*1000:.2f}"})
        else:
            log_test("Login rápido", "FAILED", f"Tempo: {elapsed:.2f}s")
    except Exception as e:
        log_test("Login rápido", "FAILED", str(e))
    
    # Teste 3: Consulta de logs não impacta performance
    try:
        login_resp = requests.post(
            f"{API_BASE}/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        if login_resp.status_code == 200:
            token = login_resp.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            start = time.time()
            resp = requests.get(f"{API_BASE}/audit/logs?limit=10", headers=headers)
            elapsed = time.time() - start
            
            if resp.status_code == 200 and elapsed < 3.0:
                log_test("Consulta de logs rápida", "PASSED", details={"time_ms": f"{elapsed*1000:.2f}"})
            else:
                log_test("Consulta de logs rápida", "FAILED", f"Tempo: {elapsed:.2f}s")
    except Exception as e:
        log_test("Consulta de logs rápida", "FAILED", str(e))


def main():
    """Executa todos os testes gerais"""
    print("=" * 60)
    print("🌍 BATERIA DE TESTES GERAIS")
    print("=" * 60)
    
    test_frontend_backend_communication()
    test_complete_login_flow()
    test_protected_route_access()
    test_role_based_access()
    test_performance()
    
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

