#!/usr/bin/env python
"""
Script de teste completo da API
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from fastapi.testclient import TestClient
from backend.app import app

# Cliente de teste
client = TestClient(app)

print("=" * 60)
print("TESTANDO API - Gerenciador de Projetos")
print("=" * 60)

# Teste 1: Health check
print("\n1️⃣  Teste: Health Check")
try:
    response = client.get("/health")
    print(f"   Status: {response.status_code}")
    print(f"   Resposta: {response.json()}")
except Exception as e:
    print(f"   ❌ Erro: {e}")

# Teste 2: Docs (Swagger)
print("\n2️⃣  Teste: Documentação Swagger (/docs)")
try:
    response = client.get("/docs")
    print(f"   Status: {response.status_code}")
    print(f"   ✅ Documentação disponível" if response.status_code == 200 else f"   ❌ Erro ao acessar docs")
except Exception as e:
    print(f"   ❌ Erro: {e}")

# Teste 3: Listar Projetos
print("\n3️⃣  Teste: Listar Projetos")
try:
    response = client.get("/api/projetos")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Projetos encontrados: {len(data)}")
    else:
        print(f"   Resposta: {response.json()}")
except Exception as e:
    print(f"   ❌ Erro: {e}")

# Teste 4: Listar Usuários
print("\n4️⃣  Teste: Listar Usuários")
try:
    response = client.get("/api/usuarios")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Usuários encontrados: {len(data) if isinstance(data, list) else 'indefinido'}")
    else:
        print(f"   Resposta: {response.text[:100]}")
except Exception as e:
    print(f"   ❌ Erro: {e}")

# Teste 5: Criar usuário (signup)
print("\n5️⃣  Teste: Criar Usuário")
novo_usuario = {
    "nome": "Usuário Teste",
    "email": f"teste-{os.urandom(4).hex()}@test.com",
    "senha": "SenhaForte123!",
    "telefone": "11999999999",
    "cargo": "Engenheiro"
}
try:
    response = client.post("/api/usuarios", json=novo_usuario)
    print(f"   Status: {response.status_code}")
    print(f"   Email: {novo_usuario['email']}")
    if response.status_code in [200, 201]:
        print(f"   ✅ Usuário criado com sucesso")
    else:
        print(f"   Resposta: {response.json()}")
except Exception as e:
    print(f"   ❌ Erro: {e}")

# Teste 6: Listar Equipes
print("\n6️⃣  Teste: Listar Equipes")
try:
    response = client.get("/api/equipes")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Equipes encontradas: {len(data) if isinstance(data, list) else 'indefinido'}")
    else:
        print(f"   Resposta: {response.text[:100]}")
except Exception as e:
    print(f"   ❌ Erro: {e}")

# Teste 7: Listar Tarefas
print("\n7️⃣  Teste: Listar Tarefas")
try:
    response = client.get("/api/tarefas")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Tarefas encontradas: {len(data) if isinstance(data, list) else 'indefinido'}")
    else:
        print(f"   Resposta: {response.text[:100]}")
except Exception as e:
    print(f"   ❌ Erro: {e}")

# Teste 8: Listar Documentos
print("\n8️⃣  Teste: Listar Documentos")
try:
    response = client.get("/api/documentos")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Documentos encontrados: {len(data) if isinstance(data, list) else 'indefinido'}")
    else:
        print(f"   Resposta: {response.text[:100]}")
except Exception as e:
    print(f"   ❌ Erro: {e}")

print("\n" + "=" * 60)
print("✅ TESTES CONCLUÍDOS!")
print("=" * 60)
