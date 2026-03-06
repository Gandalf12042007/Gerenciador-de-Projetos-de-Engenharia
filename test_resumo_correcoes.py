#!/usr/bin/env python3
"""
Resumo de Correções Realizadas no Sistema
"""

import requests
import json

BASE_URL = "http://localhost:8000"
PRINT_WIDTH = 70

def print_header(title):
    print("\n" + "=" * PRINT_WIDTH)
    print(f"  {title}")
    print("=" * PRINT_WIDTH)

def print_result(name, success, msg=""):
    status = "✅ PASSOU" if success else "❌ FALHOU"
    print(f"{status}: {name}")
    if msg:
        print(f"   └─ {msg}")

print("\n" + "🔧 RESUMO DE CORREÇÕES E TESTES FINAIS".center(PRINT_WIDTH))
print("=" * PRINT_WIDTH)

print("""
PROBLEMAS IDENTIFICADOS E CORRIGIDOS:

1. ✅ login.html retornando 405
   → Corrigido: Adicionou StaticFiles mount para raiz da pasta /web
   
2. ✅ manifest.json retornando 404
   → Corrigido: Adicionou rota /manifest.json no backend
   
3. ✅ Teste enviando "password" em vez de "senha"
   → Corrigido: Alterado test_debug_dashboard.py e test_quick.py
   
4. ✅ Falta de /api/projetos (estava testando /api/projects)
   → Confirmado: Endpoint correto é /api/projetos/ (com slash)

5. ✅ JS não carregando de /js folder
   → Corrigido: Adicionado mount para /js no app.py
""")

results = {}

# Teste 1: Backend Health
print_header("1. SAÚDE DO BACKEND")
try:
    r = requests.get(f"{BASE_URL}/health", timeout=3)
    results['health'] = r.status_code == 200
    print_result("Health Check", results['health'], f"Status {r.status_code}")
except Exception as e:
    results['health'] = False
    print_result("Health Check", False, str(e))

# Teste 2: Login
print_header("2. AUTENTICAÇÃO")
token = None
try:
    r = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": "vicentedesouza762@gmail.com",
        "senha": "Admin@2026"
    }, timeout=3)
    if r.status_code == 200:
        token = r.json()['access_token']
        results['login'] = True
        print_result("Login", True, f"Token obtido")
    else:
        results['login'] = False
        print_result("Login", False, f"Status {r.status_code}")
except Exception as e:
    results['login'] = False
    print_result("Login", False, str(e))

# Teste 3: Endpoints de Arquivo
print_header("3. SERVIMENTO DE ARQUIVOS ESTÁTICOS")
files_test = [
    ('/login.html', 'Login Page'),
    ('/projects/index.html', 'Dashboard HTML'),
    ('/manifest.json', 'PWA Manifest'),
    ('/api-client.js', 'API Client JS')
]

results['files'] = {}
for path, name in files_test:
    try:
        r = requests.head(f"{BASE_URL}{path}", timeout=3)
        results['files'][path] = r.status_code == 200
        print_result(name, results['files'][path], f"Status {r.status_code}")
    except Exception as e:
        results['files'][path] = False
        print_result(name, False, str(e))

# Teste 4: API de Projetos
print_header("4. API DE PROJETOS")
if token:
    try:
        r = requests.get(f"{BASE_URL}/api/projetos/", 
            headers={"Authorization": f"Bearer {token}"}, timeout=3)
        if r.status_code == 200:
            data = r.json()
            results['projetos'] = True
            print_result("GET /api/projetos/", True, f"{len(data)} projetos")
        else:
            results['projetos'] = False
            print_result("GET /api/projetos/", False, f"Status {r.status_code}")
    except Exception as e:
        results['projetos'] = False
        print_result("GET /api/projetos/", False, str(e))
else:
    results['projetos'] = False
    print_result("GET /api/projetos/", False, "Sem token")

# Teste 5: PWA
print_header("5. PWA (Progressive Web App)")
try:
    r = requests.get(f"{BASE_URL}/manifest.json", timeout=3)
    if r.status_code == 200:
        manifest = r.json()
        results['pwa'] = True
        print_result("Manifest", True, f"App name: {manifest.get('name', 'N/A')}")
    else:
        results['pwa'] = False
        print_result("Manifest", False, f"Status {r.status_code}")
except Exception as e:
    results['pwa'] = False
    print_result("Manifest", False, str(e))

# Resume
print_header("📊 RESULTADO FINAL")
passed = sum(1 for v in results.values() if isinstance(v, bool) and v)
total = sum(1 for v in results.values() if isinstance(v, bool))

print(f"\n✅ Testes Passaram: {passed}/{total}")
print(f"\nSITUAÇÃO: ", end="")

if passed >= 6:
    print("🟢 SISTEMA FUNCIONAL")
    print("""
PRÓXIMOS PASSOS:
  1. Abra http://localhost:8000/login.html no navegador
  2. Faça login com: vicentedesouza762@gmail.com / Admin@2026
  3. Verifique se o dashboard carrega os projetos
  4. Teste navegação entre páginas
  5. Verifique console do navegador para erros
""")
else:
    print("🔴 PROBLEMAS IDENTIFICADOS")
    print(f"\nProblemas: {[k for k, v in results.items() if isinstance(v, bool) and not v]}")

print("\n" + "=" * PRINT_WIDTH)
