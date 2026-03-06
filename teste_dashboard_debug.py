#!/usr/bin/env python3
"""
Script para testar o fluxo completo: Login -> Dashboard
Valida se todos os dados necessários estão sendo retornados
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_login():
    """Testa login e retorna token"""
    print("\n" + "="*50)
    print("1. TESTANDO LOGIN")
    print("="*50)
    
    # Tentar diferentes credenciais
    credentials_list = [
        {"email": "vicentedesouza762@gmail.com", "senha": "Admin@2026"},
        {"email": "francisco@projeto.com", "senha": "Admin@2026"},
        {"email": "professor@projeto.com", "senha": "Admin@2026"},
        {"email": "gerenteteste@projeto.com", "senha": "Gerente@123"},
        {"email": "engenheiroteste@projeto.com", "senha": "Engenheiro@123"},
    ]
    
    for login_data in credentials_list:
        print(f"\nTentando: {login_data['email']}")
        try:
            response = requests.post(
                f"{BASE_URL}/api/auth/login",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"✅ Login bem-sucedido com {login_data['email']}!")
                print(f"Response: {json.dumps(response.json(), indent=2)}")
                return response.json().get('access_token')
        except Exception as e:
            print(f"  Erro: {e}")
    
    return None

def test_projetos(token):
    """Testa carregamento de projetos"""
    print("\n" + "="*50)
    print("2. TESTANDO /api/projetos/")
    print("="*50)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/projetos/",
            headers=headers
        )
        
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Retornado: {len(data) if isinstance(data, list) else 1} projeto(s)")
        
        if isinstance(data, list) and len(data) > 0:
            print(f"\nPrimeiro projeto: {json.dumps(data[0], indent=2)[:200]}...")
        
        return data if isinstance(data, list) else []
        
    except Exception as e:
        print(f"❌ Erro ao carregar projetos: {e}")
        return []

def test_tarefas_projeto(token, projeto_id):
    """Testa carregamento de tarefas por projeto"""
    print(f"\n" + "="*50)
    print(f"3. TESTANDO /api/tarefas/projeto/{projeto_id}")
    print("="*50)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/tarefas/projeto/{projeto_id}",
            headers=headers
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Retornado: {len(data) if isinstance(data, list) else 1} tarefa(s)")
            
            if isinstance(data, list) and len(data) > 0:
                print(f"\nPrimeira tarefa: {json.dumps(data[0], indent=2)[:200]}...")
            
            return data
        else:
            print(f"Response: {response.text}")
            return []
        
    except Exception as e:
        print(f"❌ Erro ao carregar tarefas: {e}")
        return []

def test_tarefas_all(token):
    """Testa o endpoint GET /api/tarefas/"""
    print(f"\n" + "="*50)
    print(f"4. TESTANDO GET /api/tarefas/")
    print("="*50)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/tarefas/",
            headers=headers
        )
        
        print(f"Status: {response.status_code}")
        print(f"Method: GET")
        
        if response.status_code == 405:
            print(f"❌ Método GET não permitido em /api/tarefas/")
            print(f"   Isso é esperado se só POST está implementado")
        elif response.status_code == 200:
            data = response.json()
            print(f"✅ GET /api/tarefas/ funcionando")
            print(f"   Retornado: {len(data) if isinstance(data, list) else 1} tarefa(s)")
        else:
            print(f"Response: {response.text[:200]}")
        
        return response.status_code
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return None

def main():
    print("\n" + "="*60)
    print("TESTE COMPLETO DO FLUXO: LOGIN -> DASHBOARD")
    print("="*60)
    
    # 1. Login
    token = test_login()
    if not token:
        print("\n❌ Não conseguiu fazer login. Aborting...")
        return
    
    # 2. Projetos
    projetos = test_projetos(token)
    
    # 3. Tarefas por projeto
    if projetos:
        for projeto in projetos[:2]:  # Testa primeiros 2 projetos
            test_tarefas_projeto(token, projeto['id'])
    
    # 4. Tarefas geral
    test_tarefas_all(token)
    
    # Resumo
    print("\n" + "="*60)
    print("RESUMO DO TESTE")
    print("="*60)
    print(f"✅ Login: Sucesso")
    print(f"✅ Projetos: {len(projetos)} encontrado(s)")
    print(f"⚠️  Verifique os logs acima para tarefas")
    print("\nPróxima ação:")
    print("1. Abrir http://localhost:8000/login")
    print("2. Fazer login com admin@test.com / admin123")
    print("3. Verificar console do browser (F12) para erros")
    print("="*60)

if __name__ == "__main__":
    main()
