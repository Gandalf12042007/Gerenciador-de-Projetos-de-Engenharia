#!/usr/bin/env python3
"""
Teste simples e direto do dashboard
"""

import requests
import json

BASE_URL = "http://localhost:8000"

print("="*60)
print("TESTE DO DASHBOARD - VERSÃO SIMPLES")
print("="*60)

# Credenciais
email = "vicentedesouza762@gmail.com"
senha = "Admin@2026"

print(f"\n1. Fazendo login com {email}...")

try:
    # Login
    resp = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": email, "senha": senha},
        timeout=10
    )
    
    if resp.status_code != 200:
        print(f"❌ Login falhou: {resp.status_code}")
        print(resp.text[:200])
        exit(1)
    
    data = resp.json()
    token = data['access_token']
    print(f"✅ Login sucesso! Token gerado.")
    
    # Headers com token
    headers = {"Authorization": f"Bearer {token}"}
    
    # Carregar projetos
    print(f"\n2. Carregando projetos...")
    resp = requests.get(f"{BASE_URL}/api/projetos/", headers=headers, timeout=10)
    
    if resp.status_code != 200:
        print(f"❌ Erro: {resp.status_code}")
        exit(1)
    
    projects = resp.json()
    print(f"✅ {len(projects)} projetos carregados")
    
    # Resumo
    print(f"\n" + "="*60)
    print(f"RESUMO:")
    print(f"✅ Login: Funcionando")
    print(f"✅ Projetos: {len(projects)} encontrado(s)")
    
    if len(projects) > 0:
        print(f"✅ API respondendo corretamente")
        print(f"\n✅ DASHBOARD PRONTO PARA USAR!")
        print(f"\nPróximo passo:")
        print(f"1. Abrir: http://localhost:8000/login")
        print(f"2. Login com: {email}")
        print(f"3. Você deve ser redirecionado ao dashboard")
    else:
        print(f"⚠️  Nenhum projeto encontrado (banco pode estar vazio)")
        print(f"⚠️  Execute: python database/seed_sqlite.py")
    
    print(f"="*60)
    
except requests.exceptions.ConnectionError:
    print(f"❌ ERRO: Servidor não está respondendo.")
    print(f"❌ Verifique se http://localhost:8000 está rodando")
except requests.exceptions.Timeout:
    print(f"❌ ERRO: Requisição timeout (servidor muito lento)")
except Exception as e:
    print(f"❌ ERRO: {e}")
