#!/usr/bin/env python3
"""
Script de Teste de Contas - Gerenciador de Projetos
Testa todas as credenciais de login
"""

import requests
import json
from datetime import datetime

# URL da API
API_URL = "http://localhost:8000/api/auth/login"

# Contas a testar
CONTAS = [
    {
        "email": "vicentedesouza762@gmail.com",
        "senha": "Admin@2026",
        "cargo": "Administrador",
        "role": "admin"
    },
    {
        "email": "francisco@projeto.com",
        "senha": "Admin@2026",
        "cargo": "Desenvolvedor",
        "role": "admin"
    },
    {
        "email": "professor@projeto.com",
        "senha": "Admin@2026",
        "cargo": "Professor",
        "role": "admin"
    },
    {
        "email": "gerenteteste@projeto.com",
        "senha": "Gerente@123",
        "cargo": "Gerente de Projetos",
        "role": "gerente"
    },
    {
        "email": "engenheiroteste@projeto.com",
        "senha": "Engenheiro@123",
        "cargo": "Engenheiro Civil",
        "role": "engenheiro"
    },
    {
        "email": "tecnicoteste@projeto.com",
        "senha": "Tecnico@123",
        "cargo": "Técnico em Edificações",
        "role": "tecnico"
    },
    {
        "email": "clienteteste@projeto.com",
        "senha": "Cliente@123",
        "cargo": "Cliente",
        "role": "cliente"
    }
]

def testar_conta(email, senha, cargo, role):
    """Testa uma conta de login"""
    try:
        response = requests.post(
            API_URL,
            json={"email": email, "senha": senha},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            return {
                "status": "✅ SUCCESS",
                "usuario": data.get("nome"),
                "role": data.get("role"),
                "token": data.get("access_token")[:20] + "..." if data.get("access_token") else None
            }
        else:
            return {
                "status": f"❌ ERRO {response.status_code}",
                "detalhes": response.json().get("detail", "Erro desconhecido")
            }
    except Exception as e:
        return {
            "status": "❌ CONEXÃO FALHOU",
            "erro": str(e)
        }

def main():
    print("\n" + "="*80)
    print("🧪 TESTE DE CONTAS - Gerenciador de Projetos de Engenharia")
    print("="*80)
    print(f"⏰ Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"🔗 API: {API_URL}\n")
    
    resultados = []
    sucesso = 0
    falha = 0
    
    for i, conta in enumerate(CONTAS, 1):
        print(f"\n[{i}/{len(CONTAS)}] Testando: {conta['email']}")
        print(f"    Cargo: {conta['cargo']}")
        print(f"    Role: {conta['role']}")
        print(f"    Senha: {conta['senha']}")
        
        resultado = testar_conta(conta["email"], conta["senha"], conta["cargo"], conta["role"])
        
        print(f"    Resultado: {resultado['status']}")
        
        if "SUCCESS" in resultado['status']:
            print(f"    ✓ Nome: {resultado['usuario']}")
            print(f"    ✓ Token: {resultado['token']}")
            sucesso += 1
        else:
            if "CONEXÃO" in resultado['status']:
                print(f"    Erro: {resultado['erro']}")
            else:
                print(f"    Erro: {resultado['detalhes']}")
            falha += 1
        
        resultados.append({
            "email": conta["email"],
            "resultado": resultado
        })
    
    # Resumo
    print("\n" + "="*80)
    print("📊 RESUMO DOS TESTES")
    print("="*80)
    print(f"✅ Sucesso: {sucesso}/{len(CONTAS)}")
    print(f"❌ Falhas: {falha}/{len(CONTAS)}")
    print(f"📈 Taxa de Sucesso: {(sucesso/len(CONTAS)*100):.1f}%")
    print("\n" + "="*80 + "\n")
    
    # Exibir dados de todas as contas em JSON para referência
    print("📋 CONTAS DISPONÍVEIS (JSON):\n")
    print(json.dumps(CONTAS, indent=2, ensure_ascii=False))
    print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    main()
