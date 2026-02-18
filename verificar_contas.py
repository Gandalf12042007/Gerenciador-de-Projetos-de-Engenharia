#!/usr/bin/env python3
"""
Script para verificar e testar todas as contas do sistema
"""

import requests
import json
from datetime import datetime

# URL da API
API_URL = "http://localhost:8000"
LOGIN_ENDPOINT = f"{API_URL}/auth/login"

# Contas de teste conhecidas
CONTAS_TESTE = [
    {
        "email": "vicentedesouza762@gmail.com",
        "senha": "Abacaxi371",
        "nome": "Vicente de Souza (Admin Principal)",
        "tipo": "Admin"
    },
    {
        "email": "joao@test.com",
        "senha": "senha123",
        "nome": "João Silva",
        "tipo": "Engenheiro Civil"
    },
    {
        "email": "maria@test.com",
        "senha": "senha123",
        "nome": "Maria Santos",
        "tipo": "Gerente de Projetos"
    },
    {
        "email": "pedro@test.com",
        "senha": "senha123",
        "nome": "Pedro Oliveira",
        "tipo": "Técnico em Edificações"
    },
    {
        "email": "ana@test.com",
        "senha": "senha123",
        "nome": "Ana Costa",
        "tipo": "Arquiteta"
    },
    {
        "email": "carlos@test.com",
        "senha": "senha123",
        "nome": "Carlos Souza",
        "tipo": "Engenheiro Estrutural"
    }
]

def testar_conexao_api():
    """Testa se a API está respondendo"""
    print("\n" + "="*70)
    print("🔍 VERIFICANDO CONEXÃO COM A API")
    print("="*70)
    
    try:
        response = requests.get(f"{API_URL}/docs")
        if response.status_code == 200:
            print(f"✅ API respondendo em {API_URL}")
            print(f"   Status: {response.status_code}")
            return True
        else:
            print(f"❌ API não respondeu corretamente")
            print(f"   Status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ Não conseguiu conectar à API em {API_URL}")
        print("   Certifique-se de que o backend está rodando!")
        return False
    except Exception as e:
        print(f"❌ Erro ao conectar: {str(e)}")
        return False

def tentar_login(email, senha):
    """Tenta fazer login com as credenciais fornecidas"""
    try:
        payload = {
            "email": email,
            "senha": senha
        }
        
        response = requests.post(LOGIN_ENDPOINT, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            return True, data.get("access_token", "TOKEN"), data.get("user_id")
        else:
            error_msg = response.json().get("detail", "Erro desconhecido")
            return False, error_msg, None
            
    except requests.exceptions.ConnectionError:
        return False, "API não está respondendo", None
    except Exception as e:
        return False, str(e), None

def verificar_contas():
    """Verifica todas as contas de teste"""
    print("\n" + "="*70)
    print("🧪 VERIFICANDO CONTAS DE ACESSO")
    print("="*70)
    
    total = len(CONTAS_TESTE)
    sucesso = 0
    falha = 0
    
    for idx, conta in enumerate(CONTAS_TESTE, 1):
        email = conta["email"]
        senha = conta["senha"]
        nome = conta["nome"]
        tipo = conta["tipo"]
        
        print(f"\n[{idx}/{total}] Testando: {nome}")
        print(f"     Email: {email}")
        print(f"     Tipo: {tipo}")
        
        login_ok, mensagem, user_id = tentar_login(email, senha)
        
        if login_ok:
            print(f"     ✅ LOGIN SUCESSO")
            print(f"     Token: {mensagem[:30]}...")
            print(f"     User ID: {user_id}")
            sucesso += 1
        else:
            print(f"     ❌ LOGIN FALHOU")
            print(f"     Erro: {mensagem}")
            falha += 1
    
    # Resumo
    print("\n" + "="*70)
    print("📊 RESUMO DOS TESTES")
    print("="*70)
    print(f"Total de contas: {total}")
    print(f"✅ Contas funcionando: {sucesso}")
    print(f"❌ Contas com erro: {falha}")
    print(f"Taxa de sucesso: {(sucesso/total)*100:.1f}%")
    
    if falha > 0:
        print("\n⚠️  AVISO: Algumas contas não funcionam!")
        print("Possíveis motivos:")
        print("  1. Banco de dados não foi populado com seed")
        print("  2. Senhas das contas foram alteradas")
        print("  3. Contas foram deletadas do banco")
        print("\nTente executar o seed do banco:")
        print("  cd database")
        print("  python seed_sqlite.py")

def exibir_relatorio_final():
    """Exibe relatório final com instruções"""
    print("\n" + "="*70)
    print("📋 INSTRUÇÕES PARA USAR O SISTEMA")
    print("="*70)
    
    print("\n🌐 Frontend:")
    print("   http://localhost:3000")
    
    print("\n📚 API Documentação (Swagger):")
    print("   http://localhost:8000/docs")
    
    print("\n🔓 Contas principais:")
    print("   Email: vicentedesouza762@gmail.com")
    print("   Senha: Abacaxi371")
    
    print("\n📊 Banco de dados:")
    print("   Tipo: SQLite (built-in no Python)")
    print("   Local: database/gerenciador.db")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*68 + "║")
    print("║" + "  🔐 VERIFICADOR DE CONTAS - SISTEMA DE GESTÃO DE PROJETOS".center(68) + "║")
    print("║" + " "*68 + "║")
    print("╚" + "="*68 + "╝")
    
    print(f"\nData/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    # Testar conexão
    if not testar_conexao_api():
        print("\n❌ ERRO: Não foi possível conectar à API!")
        print("Execute primeiro: cd backend && python app.py")
        exit(1)
    
    # Verificar contas
    verificar_contas()
    
    # Exibir relatório
    exibir_relatorio_final()
    
    print("\n✅ Verificação concluída!\n")
