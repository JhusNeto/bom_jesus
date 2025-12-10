#!/usr/bin/env python3
"""
Script de Teste de Endpoints de Auditoria
"""
import sys
import os
import requests
from typing import Dict, Any, List

BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

TEST_EMAIL = "admin@bomjesus.com"
TEST_PASSWORD = "admin123"

test_results: List[Dict[str, Any]] = []


def log_test(name: str, status: str, error: str = None, details: Dict = None):
    if status == "PASSED":
        print(f"✅ {name}")
    else:
        print(f"❌ {name}: {error}")
    result = {"name": name, "status": status}
    if error:
        result["error"] = error
    if details:
        result["details"] = details
    test_results.append(result)


def main():
    print("\n🔍 Testando Endpoints de Auditoria...")
    
    # Login
    login_resp = requests.post(
        f"{API_BASE}/auth/login",
        json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
    )
    if login_resp.status_code != 200:
        print(f"❌ Login falhou: {login_resp.status_code}")
        return 1
    
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Teste 1: Listar logs
    try:
        resp = requests.get(f"{API_BASE}/audit/logs?limit=10", headers=headers)
        if resp.status_code == 200:
            logs = resp.json()
            log_test("GET /audit/logs - Listagem", "PASSED",
                    details={"count": len(logs) if isinstance(logs, list) else 0})
        else:
            log_test("GET /audit/logs - Listagem", "FAILED", f"Status: {resp.status_code}")
    except Exception as e:
        log_test("GET /audit/logs - Listagem", "FAILED", str(e))
    
    # Teste 2: Estatísticas
    try:
        resp = requests.get(f"{API_BASE}/audit/stats", headers=headers)
        if resp.status_code == 200:
            stats = resp.json()
            log_test("GET /audit/stats - Estatísticas", "PASSED",
                    details={"total_logs": stats.get("total_logs", 0)})
        else:
            log_test("GET /audit/stats - Estatísticas", "FAILED", f"Status: {resp.status_code}")
    except Exception as e:
        log_test("GET /audit/stats - Estatísticas", "FAILED", str(e))
    
    # Teste 3: Dashboard
    try:
        resp = requests.get(f"{API_BASE}/audit/dashboard", headers=headers)
        if resp.status_code == 200:
            dashboard = resp.json()
            log_test("GET /audit/dashboard - Dashboard", "PASSED",
                    details={"has_resumo": "resumo" in dashboard})
        else:
            log_test("GET /audit/dashboard - Dashboard", "FAILED", f"Status: {resp.status_code}")
    except Exception as e:
        log_test("GET /audit/dashboard - Dashboard", "FAILED", str(e))
    
    # Teste 4: Proteção por role (tentar como OPERATOR - deve falhar)
    operator_login = requests.post(
        f"{API_BASE}/auth/login",
        json={"email": "operador@bomjesus.com", "password": "operador123"}
    )
    if operator_login.status_code == 200:
        operator_token = operator_login.json()["access_token"]
        operator_headers = {"Authorization": f"Bearer {operator_token}"}
        resp = requests.get(f"{API_BASE}/audit/logs", headers=operator_headers)
        if resp.status_code == 403:
            log_test("Proteção por role (OPERATOR bloqueado)", "PASSED")
        else:
            log_test("Proteção por role (OPERATOR bloqueado)", "FAILED",
                    f"Status: {resp.status_code} (esperado 403)")
    
    # Resumo
    passed = sum(1 for t in test_results if t["status"] == "PASSED")
    failed = sum(1 for t in test_results if t["status"] == "FAILED")
    print(f"\n✅ Passou: {passed}, ❌ Falhou: {failed}")
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

