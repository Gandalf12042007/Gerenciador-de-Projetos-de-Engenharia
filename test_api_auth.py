#!/usr/bin/env python
"""Script de teste completo com autenticação"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from fastapi.testclient import TestClient
from backend.app import app

client = TestClient(app)

print("=" * 70)
print("TESTE COMPLETO COM AUTENTICAÇÃO")
print("=" * 70)

# 1. Login para obter token
print("\n1️⃣  Fazendo login...")
login_data = {
    "email": "vicentedesouza@email.com",
    "senha": "Senha123"  
}

response = client.post("/api/auth/login", json=login_data)
print(f"   Status: {response.status_code}")

token = None
if response.status_code == 200:
    data = response.json()
    token = data.get('access_token')
    print(f"   ✅ Login bem-sucedido!")
    print(f"   Token: {token[:30]}..." if token else "   ⚠️  Sem token retornado")
else:
    print(f"   ❌ Erro no login: {response.text[:100]}")
    print(f"   Response: {response.json()}")

# 2. Listar Projetos com autenticação
print("\n2️⃣  Listando Projetos (com autenticação)...")
headers = {}
if token:
    headers = {"Authorization": f"Bearer {token}"}

response = client.get("/api/projetos/", headers=headers)
print(f"   Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    if isinstance(data, list):
        print(f"   ✅ Projetos encontrados: {len(data)}")
        if len(data) > 0:
            print(f"      - {data[0]}" if isinstance(data[0], dict) else f"      - {data[0]}")
    else:
        print(f"   Resposta: {data}")
else:
    print(f"   Resposta: {response.text[:150]}")

# 3. Listar Tarefas
print("\n3️⃣  Listando Tarefas...")
response = client.get("/api/tarefas/", headers=headers)
print(f"   Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    if isinstance(data, list):
        print(f"   ✅ Tarefas encontradas: {len(data)}")
    else:
        print(f"   Resposta: {data}")
else:
    print(f"   Resposta: {response.text[:150]}")

# 4. Listar Equipes
print("\n4️⃣  Listando Equipes...")
response = client.get("/api/equipes/", headers=headers)
print(f"   Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    if isinstance(data, list):
        print(f"   ✅ Equipes encontradas: {len(data)}")
    else:
        print(f"   Resposta: {data}")
else:
    print(f"   Resposta: {response.text[:150]}")

# 5. Listar Documentos
print("\n5️⃣  Listando Documentos...")
response = client.get("/api/documentos/", headers=headers)
print(f"   Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    if isinstance(data, list):
        print(f"   ✅ Documentos encontrados: {len(data)}")
    else:
        print(f"   Resposta: {data}")
else:
    print(f"   Resposta: {response.text[:150]}")

# 6. Listar Materiais
print("\n6️⃣  Listando Materiais...")
response = client.get("/api/materiais/", headers=headers)
print(f"   Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    if isinstance(data, list):
        print(f"   ✅ Materiais encontrados: {len(data)}")
    else:
        print(f"   Resposta: {data}")
else:
    print(f"   Resposta: {response.text[:150]}")

# 7. OpenAPI schema
print("\n7️⃣  Acessando Schema OpenAPI...")
response = client.get("/openapi.json")
print(f"   Status: {response.status_code}")
if response.status_code == 200:
    schema = response.json()
    paths = list(schema.get('paths', {}).keys())
    print(f"   ✅ Schema OpenAPI encontrado!")
    print(f"   Total de paths: {len(paths)}")
    print(f"   Primeiros paths: {paths[:5]}")
else:
    print(f"   ❌ Erro ao acessar schema")

print("\n" + "=" * 70)
print("✅ TESTES CONCLUÍDOS!")
print("=" * 70)
