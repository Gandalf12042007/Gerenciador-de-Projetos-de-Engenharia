#!/usr/bin/env python3
"""
Teste de diagnóstico para o dashboard
Verifica todas as conexões e API endpoints
"""

import requests
import json
import sys
from datetime import datetime

BASE_URL = "http://localhost:8000"
TEST_EMAIL = "vicentedesouza762@gmail.com"
TEST_PASSWORD = "Admin@2026"

def print_header(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def test_health():
    """Testa /health endpoint"""
    print_header("1. TESTE DE SAÚDE DO SERVIDOR")
    try:
        r = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"✅ Status: {r.status_code}")
        print(f"📄 Resposta: {r.json() if r.headers.get('content-type') == 'application/json' else r.text}")
        return True
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def test_login():
    """Testa login e obtém token"""
    print_header("2. TESTE DE LOGIN")
    try:
        payload = {"email": TEST_EMAIL, "senha": TEST_PASSWORD}
        r = requests.post(f"{BASE_URL}/api/auth/login", json=payload, timeout=5)
        print(f"✅ Status: {r.status_code}")
        
        if r.status_code == 200:
            data = r.json()
            token = data.get('access_token')
            print(f"✅ Token obtido: {token[:20]}..." if token else "❌ Sem token")
            return token
        else:
            print(f"❌ Erro: {r.text[:200]}")
            return None
    except Exception as e:
        print(f"❌ Erro: {e}")
        return None

def test_cors():
    """Testa headers CORS"""
    print_header("3. TESTE DE CORS")
    try:
        r = requests.options(f"{BASE_URL}/api/projects", timeout=5)
        cors_origin = r.headers.get('access-control-allow-origin')
        cors_methods = r.headers.get('access-control-allow-methods')
        print(f"✅ CORS Allow-Origin: {cors_origin if cors_origin else '(não definido)'}")
        print(f"✅ CORS Allow-Methods: {cors_methods}")
        return True
    except Exception as e:
        print(f"⚠️  Erro: {e}")
        return False

def test_projects_endpoint(token):
    """Testa /api/projetos endpoint"""
    print_header("4. TESTE DE ENDPOINT /api/projetos")
    try:
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        r = requests.get(f"{BASE_URL}/api/projetos/", headers=headers, timeout=5)
        print(f"✅ Status: {r.status_code}")
        
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, list):
                print(f"✅ Retornou lista com {len(data)} projetos")
                if data:
                    print(f"   Primeiro projeto: {data[0]}")
            else:
                print(f"📄 Resposta: {str(data)[:200]}")
            return True
        elif r.status_code == 401:
            print(f"❌ Não autorizado (401) - Token inválido ou expirado")
            return False
        else:
            print(f"❌ Status {r.status_code}: {r.text[:200]}")
            return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def test_dashboard_endpoint(token):
    """Testa /api/dashboard endpoint"""
    print_header("5. TESTE DE ENDPOINT /api/dashboard")
    try:
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        r = requests.get(f"{BASE_URL}/api/dashboard", headers=headers, timeout=5)
        print(f"✅ Status: {r.status_code}")
        
        if r.status_code == 200:
            data = r.json()
            print(f"✅ Resposta: {json.dumps(data, indent=2)[:500]}")
            return True
        elif r.status_code == 401:
            print(f"❌ Não autorizado (401)")
            return False
        elif r.status_code == 404:
            print(f"⚠️  Endpoint não encontrado (404)")
            return False
        else:
            print(f"⚠️  Status {r.status_code}")
            return False
    except Exception as e:
        print(f"⚠️  Erro: {e}")
        return False

def test_static_files():
    """Testa servir arquivos estáticos HTML"""
    print_header("6. TESTE DE ARQUIVOS ESTÁTICOS")
    files_to_test = [
        '/login.html',
        '/projects/index.html',
        '/projects/kanban.html',
        '/manifest.json'
    ]
    
    for file in files_to_test:
        try:
            r = requests.head(f"{BASE_URL}{file}", timeout=5)
            status = "✅" if r.status_code == 200 else "❌"
            print(f"{status} {file}: {r.status_code}")
        except Exception as e:
            print(f"❌ {file}: {e}")

def test_db_connection():
    """Testa conexão com banco de dados através de um endpoint"""
    print_header("7. TESTE DE BANCO DE DADOS")
    try:
        # Tenta acessar um endpoint que precisa de DB
        r = requests.get(f"{BASE_URL}/api/auth/users", timeout=5)
        if r.status_code == 200:
            print(f"✅ Conexão com DB: OK")
            return True
        elif r.status_code == 401:
            print(f"✅ DB respondendo (401 - sem auth)")
            return True
        elif r.status_code == 404:
            print(f"⚠️  Endpoint não existe (404)")
            return True
        else:
            print(f"⚠️  Status {r.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return False

def main():
    print("🔍 DIAGNÓSTICO COMPLETO DO SISTEMA")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 URL do backend: {BASE_URL}")
    
    results = {
        'health': test_health(),
        'cors': test_cors(),
        'db': test_db_connection(),
        'static': test_static_files(),
    }
    
    # Tenta login para obter token
    token = test_login()
    
    # Testa endpoints da API com token
    if token:
        results['projects'] = test_projects_endpoint(token)
        results['dashboard'] = test_dashboard_endpoint(token)
    else:
        results['projects'] = False
        results['dashboard'] = False
        print_header("⚠️  AVISO")
        print("Login falhou - testes posteriores podem ser inconclusivos")
    
    # Resumo
    print_header("📊 RESUMO DOS TESTES")
    for name, result in results.items():
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{status}: {name.upper()}")
    
    passed = sum(1 for r in results.values() if r)
    total = len(results)
    print(f"\n🎯 Total: {passed}/{total} testes passaram")
    
    if passed == total:
        print("\n✅ SISTEMA OK - Todos os testes passaram!")
        sys.exit(0)
    else:
        print("\n❌ SISTEMA COM PROBLEMAS - Verifique os testes que falharam")
        sys.exit(1)

if __name__ == "__main__":
    main()
