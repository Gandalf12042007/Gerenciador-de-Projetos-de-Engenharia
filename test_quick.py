#!/usr/bin/env python3
import requests
import json

BASE_URL = "http://localhost:8000"
TEST_EMAIL = "vicentedesouza762@gmail.com"
TEST_PASSWORD = "Admin@2026"

# 1. Login
print("🔐 Testando login...")
r = requests.post(f"{BASE_URL}/api/auth/login", 
    json={"email": TEST_EMAIL, "senha": TEST_PASSWORD}, timeout=5)
print(f"Status: {r.status_code}")

if r.status_code == 200:
    token = r.json()['access_token']
    print(f"✅ Token obtido: {token[:30]}...\n")
    
    # 2. Projetos
    print("📋 Testando /api/projetos...")
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(f"{BASE_URL}/api/projetos/", headers=headers, timeout=5)
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"✅ Resposta: {type(data)} com {len(data) if isinstance(data, list) else '?'} itens")
        if isinstance(data, list) and data:
            print(f"   Primeiro item: {data[0]}")
    else:
        print(f"❌ Erro: {r.text[:200]}")
    
    # 3. Dashboard
    print("\n📊 Testando /api/dashboard...")
    r = requests.get(f"{BASE_URL}/api/dashboard", headers=headers, timeout=5)
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"✅ Dashboard retornou:\n{json.dumps(data, indent=2)[:500]}")
    else:
        print(f"⚠️  Status {r.status_code} (endpoint pode não existir)")
else:
    print(f"❌ Login falhou: {r.status_code}")
