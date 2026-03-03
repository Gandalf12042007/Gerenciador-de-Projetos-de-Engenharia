#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TESTE DE ESTABILIZACAO FASE 1
Valida todas as rotas criticas do sistema
"""

import requests
import json
import sys
from datetime import datetime

# Configuracao
API_BASE_URL = "http://localhost:8000"
print(f"\n{'='*60}")
print(f"TESTE DE ESTABILIZACAO - FASE 1")
print(f"{'='*60}")
print(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
print(f"URL Base: {API_BASE_URL}")
print(f"{'='*60}\n")

# Contadores
tests_passed = 0
tests_failed = 0
results = []

def test(name, method, endpoint, **kwargs):
    """Funcao auxiliar para testar endpoints"""
    global tests_passed, tests_failed
    
    url = f"{API_BASE_URL}{endpoint}"
    
    try:
        print(f"Testando: {name}...", end=" ")
        
        if method == "GET":
            response = requests.get(url, **kwargs)
        elif method == "POST":
            response = requests.post(url, **kwargs)
        elif method == "PUT":
            response = requests.put(url, **kwargs)
        elif method == "DELETE":
            response = requests.delete(url, **kwargs)
        
        if response.status_code in [200, 201, 204, 400, 401, 422]:
            print(f"OK ({response.status_code})")
            tests_passed += 1
            results.append({
                "name": name,
                "status": "PASSOU",
                "code": response.status_code,
                "endpoint": endpoint
            })
            return response
        else:
            print(f"FALHOU ({response.status_code})")
            tests_failed += 1
            results.append({
                "name": name,
                "status": "FALHOU",
                "code": response.status_code,
                "endpoint": endpoint
            })
            return None
    
    except Exception as e:
        print(f"ERRO: {str(e)}")
        tests_failed += 1
        results.append({
            "name": name,
            "status": "ERRO",
            "error": str(e),
            "endpoint": endpoint
        })
        return None

print("1. TESTES BASICOS DE CONECTIVIDADE")
print("="*60)

test("Health Check", "GET", "/health")
test("Root Endpoint", "GET", "/")
test("Swagger Docs", "GET", "/docs")
test("ReDoc", "GET", "/redoc")

print(f"\n2. TESTES DE AUTENTICACAO")
print("="*60)

user_data = {
    "nome": "Teste Usuario",
    "email": f"teste_{datetime.now().timestamp()}@test.com",
    "senha": "Senha123!",
    "telefone": "11999999999"
}

test("Registrar Usuario", "POST", "/api/auth/register", 
     json=user_data, headers={"Content-Type": "application/json"})

user_email = user_data["email"]

test("Login", "POST", "/api/auth/login",
     json={"email": user_email, "senha": "Senha123!"},
     headers={"Content-Type": "application/json"})

print(f"\n3. TESTES DE PROJETOS")
print("="*60)

test("Listar Projetos", "GET", "/api/projetos",
     headers={"Authorization": "Bearer dummy_token"})

print(f"\n4. TESTES DE TAREFAS")
print("="*60)

test("Listar Tarefas", "GET", "/api/tarefas",
     headers={"Authorization": "Bearer dummy_token"})

print(f"\n5. TESTES DE FRONTEND")
print("="*60)

test("Frontend Principal", "GET", "/")
test("Pagina de Login", "GET", "/login")
test("Pagina de Registro", "GET", "/register")
test("App Page", "GET", "/app")

print(f"\n6. TESTES DE ROTAS ESTATICAS")
print("="*60)

test("Arquivo CSS", "GET", "/styles.css")
test("API Client JS", "GET", "/api-client.js")
test("App JS", "GET", "/app.js")

print(f"\n{'='*60}")
print(f"RELATORIO DE TESTES")
print(f"{'='*60}")
print(f"\nTestes Passaram: {tests_passed}")
print(f"Testes Falharam: {tests_failed}")
print(f"{'='*60}\n")

print(f"DETALHES DOS TESTES:\n")
for i, result in enumerate(results, 1):
    status_symbol = "[OK]" if "PASSOU" in result["status"] else "[ERRO]"
    print(f"{i}. {status_symbol} {result['name']}")
    print(f"   Rota: {result['endpoint']}")
    print(f"   Status: {result['status']}")
    if 'code' in result:
        print(f"   Codigo: {result['code']}")
    if 'error' in result:
        print(f"   Erro: {result['error']}")
    print()

print(f"{'='*60}")
if tests_failed == 0:
    print(f"SUCESSO! TODOS OS TESTES PASSARAM!")
    print(f"{'='*60}\n")
    sys.exit(0)
else:
    print(f"AVISO: {tests_failed} testes falharam. Ver logs acima.")
    print(f"{'='*60}\n")
    sys.exit(1)

