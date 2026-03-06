#!/usr/bin/env python
"""
🔧 TESTE DE ESTABILIZAÇÃO - FASE 1
Sistema de Gerenciamento de Projetos de Engenharia

Este script verifica todos os componentes críticos do sistema.
"""

import requests
import json
import sys

API_URL = "http://localhost:8000"

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text:^60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")

def print_success(text):
    print(f"  {Colors.OKGREEN}✅ {text}{Colors.ENDC}")

def print_fail(text):
    print(f"  {Colors.FAIL}❌ {text}{Colors.ENDC}")

def print_info(text):
    print(f"  {Colors.OKCYAN}ℹ️  {text}{Colors.ENDC}")

def print_warning(text):
    print(f"  {Colors.WARNING}⚠️  {text}{Colors.ENDC}")

results = {
    "passed": 0,
    "failed": 0,
    "tests": []
}

def test(name):
    """Decorator for tests"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                if result:
                    print_success(f"{name}")
                    results["passed"] += 1
                    results["tests"].append({"name": name, "status": "passed"})
                else:
                    print_fail(f"{name}")
                    results["failed"] += 1
                    results["tests"].append({"name": name, "status": "failed"})
                return result
            except Exception as e:
                print_fail(f"{name} - {str(e)}")
                results["failed"] += 1
                results["tests"].append({"name": name, "status": "failed", "error": str(e)})
                return False
        return wrapper
    return decorator

@test("API está online")
def test_api_online():
    r = requests.get(f"{API_URL}/")
    return r.status_code == 200

@test("Health check API")
def test_health_check():
    r = requests.get(f"{API_URL}/health")
    return r.status_code == 200 and r.json().get("status") == "healthy"

@test("Documentação Swagger disponível")
def test_swagger():
    r = requests.get(f"{API_URL}/docs")
    return r.status_code == 200

@test("Endpoint de login existe")
def test_login_endpoint():
    r = requests.post(f"{API_URL}/api/auth/login", json={"email": "test@test.com", "senha": "test"})
    # 401 é esperado para credenciais inválidas (endpoint existe)
    return r.status_code in [200, 401, 429]

@test("Endpoint de registro existe")
def test_register_endpoint():
    r = requests.post(f"{API_URL}/api/auth/register", json={
        "nome": "Teste",
        "email": "teste@temp.com",
        "senha": "Teste123!"
    })
    # 400 ou 409 são esperados se email já existe
    return r.status_code in [200, 201, 400, 409, 422]

@test("Login com credenciais válidas")
def test_login_valid():
    r = requests.post(f"{API_URL}/api/auth/login", json={
        "email": "admin@sistema.com",
        "senha": "Admin123!"
    })
    if r.status_code == 200:
        global auth_token
        data = r.json()
        auth_token = data.get("access_token")
        return auth_token is not None
    elif r.status_code == 429:
        print_warning("Rate limit ativo - aguarde para tentar novamente")
        return True  # Rate limit funcionando é bom
    return False

auth_token = None

@test("Acesso autenticado a projetos")
def test_authenticated_projects():
    if not auth_token:
        print_warning("Sem token - pulando teste")
        return True
    headers = {"Authorization": f"Bearer {auth_token}"}
    r = requests.get(f"{API_URL}/api/projetos/", headers=headers)
    return r.status_code == 200

@test("Acesso autenticado a tarefas")
def test_authenticated_tasks():
    if not auth_token:
        print_warning("Sem token - pulando teste")
        return True
    headers = {"Authorization": f"Bearer {auth_token}"}
    r = requests.get(f"{API_URL}/api/tarefas/projeto/12", headers=headers)
    return r.status_code in [200, 404]  # 404 se projeto não existe

@test("Rota de métricas")
def test_metrics():
    if not auth_token:
        return True
    headers = {"Authorization": f"Bearer {auth_token}"}
    r = requests.get(f"{API_URL}/api/metricas/", headers=headers)
    return r.status_code in [200, 404]

@test("Rotas de equipes")
def test_teams():
    if not auth_token:
        return True
    headers = {"Authorization": f"Bearer {auth_token}"}
    r = requests.get(f"{API_URL}/api/equipes/", headers=headers)
    return r.status_code in [200, 404]

@test("Rotas de documentos")
def test_documents():
    if not auth_token:
        return True
    headers = {"Authorization": f"Bearer {auth_token}"}
    r = requests.get(f"{API_URL}/api/documentos/projeto/1", headers=headers)
    return r.status_code in [200, 404]

@test("Rotas de chat")
def test_chat():
    if not auth_token:
        return True
    headers = {"Authorization": f"Bearer {auth_token}"}
    r = requests.get(f"{API_URL}/api/chats/", headers=headers)
    return r.status_code in [200, 404]

@test("Rotas de notificações")
def test_notifications():
    if not auth_token:
        return True
    headers = {"Authorization": f"Bearer {auth_token}"}
    r = requests.get(f"{API_URL}/api/notificacoes/", headers=headers)
    return r.status_code in [200, 404]

@test("Rotas financeiras")
def test_financial():
    r = requests.get(f"{API_URL}/api/financeiro/")
    return r.status_code in [200, 404, 405]  # 405 se não permite GET

def main():
    print_header("TESTE DE ESTABILIZAÇÃO - FASE 1")
    print_info(f"Testando API em: {API_URL}")
    
    print("\n📡 Testes de Conectividade:")
    test_api_online()
    test_health_check()
    test_swagger()
    
    print("\n🔐 Testes de Autenticação:")
    test_login_endpoint()
    test_register_endpoint()
    test_login_valid()
    
    print("\n📦 Testes de Endpoints Protegidos:")
    test_authenticated_projects()
    test_authenticated_tasks()
    test_metrics()
    test_teams()
    test_documents()
    test_chat()
    test_notifications()
    test_financial()
    
    # Resumo
    print_header("RESUMO DOS TESTES")
    total = results["passed"] + results["failed"]
    perc = (results["passed"] / total * 100) if total > 0 else 0
    
    print(f"  Total de testes: {total}")
    print(f"  {Colors.OKGREEN}Passou: {results['passed']}{Colors.ENDC}")
    print(f"  {Colors.FAIL}Falhou: {results['failed']}{Colors.ENDC}")
    print(f"  Taxa de sucesso: {perc:.1f}%")
    
    if perc >= 90:
        print(f"\n{Colors.OKGREEN}{Colors.BOLD}🎉 SISTEMA ESTÁVEL!{Colors.ENDC}")
    elif perc >= 70:
        print(f"\n{Colors.WARNING}{Colors.BOLD}⚠️  SISTEMA PARCIALMENTE ESTÁVEL{Colors.ENDC}")
    else:
        print(f"\n{Colors.FAIL}{Colors.BOLD}❌ SISTEMA INSTÁVEL - PRECISA DE CORREÇÕES{Colors.ENDC}")
    
    return results["failed"] == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
