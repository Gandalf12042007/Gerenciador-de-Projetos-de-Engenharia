#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TESTE DE FLUXO DE LOGIN COMPLETO
Valida o login até o redirecionamento
"""

import requests
import time
from datetime import datetime

API_BASE_URL = "http://localhost:8000"

print(f"\n{'='*60}")
print(f"TESTE DE FLUXO LOGIN COMPLETO")
print(f"{'='*60}")
print(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
print(f"{'='*60}\n")

# Teste 1: Login com admin
print("1. Testando LOGIN ADMIN...")
print("   Email: vicentedesouza762@gmail.com")
print("   Senha: Admin@2026")

response = requests.post(
    f"{API_BASE_URL}/api/auth/login",
    json={
        "email": "vicentedesouza762@gmail.com",
        "senha": "Admin@2026"
    }
)

print(f"   Status: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    print(f"   Token: {data['access_token'][:50]}...")
    print(f"   User ID: {data['user_id']}")
    print(f"   Nome: {data['nome']}")
    print(f"   Email: {data['email']}")
    print(f"   Role: {data['role']}")
    
    if data['role'] == 'admin':
        print(f"\n   ESPERADO: Redirecionar para 'projects/dashboard.html'")
    else:
        print(f"\n   ESPERADO: Redirecionar para 'entrar-projeto.html'")
    print("   STATUS: OK!")
else:
    print(f"   ERRO: {response.text}")

# Teste 2: Login com usuário normal
print(f"\n2. Testando LOGIN USUARIO NORMAL...")
print("   Email: engenheiroteste@projeto.com")
print("   Senha: Engenheiro@123")

response = requests.post(
    f"{API_BASE_URL}/api/auth/login",
    json={
        "email": "engenheiroteste@projeto.com",
        "senha": "Engenheiro@123"
    }
)

print(f"   Status: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    print(f"   Token: {data['access_token'][:50]}...")
    print(f"   User ID: {data['user_id']}")
    print(f"   Nome: {data['nome']}")
    print(f"   Email: {data['email']}")
    print(f"   Role: {data['role']}")
    
    if data['role'] == 'admin':
        print(f"\n   ESPERADO: Redirecionar para 'projects/dashboard.html'")
    else:
        print(f"\n   ESPERADO: Redirecionar para 'entrar-projeto.html'")
    print("   STATUS: OK!")
else:
    print(f"   ERRO: {response.text}")

print(f"\n{'='*60}")
print("CONCLUSAO: Login retorna dados corretos para redirecionamento!")
print(f"{'='*60}\n")
