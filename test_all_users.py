"""
Teste Rápido - Validar todos os 7 usuários migrando com sucesso
"""

import requests

BASE_URL = "http://localhost:8000"
AUTH_ENDPOINT = f"{BASE_URL}/api/auth/login"

# 7 usuários migrados no BD
USUARIOS = [
    ("vicentedesouza762@gmail.com", "Admin@2026", "admin"),
    ("francisco@projeto.com", "Admin@2026", "admin"),
    ("professor@projeto.com", "Admin@2026", "admin"),
    ("gerenteteste@projeto.com", "Gerente@123", "gerente"),
    ("engenheiroteste@projeto.com", "Engenheiro@123", "engenheiro"),
    ("tecnicoteste@projeto.com", "Tecnico@123", "tecnico"),
    ("clienteteste@projeto.com", "Cliente@123", "cliente"),
]

VERDE = '\033[92m'
VERMELHO = '\033[91m'
RESET = '\033[0m'

print(f"\n{'='*70}")
print(f"🔐 TESTE DE LOGINS - 7 USUÁRIOS MIGRADOS")
print(f"{'='*70}\n")

total = len(USUARIOS)
sucesso = 0

for i, (email, senha, role_esperado) in enumerate(USUARIOS, 1):
    try:
        response = requests.post(
            AUTH_ENDPOINT,
            json={"email": email, "senha": senha},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            role_real = data.get('role')
            check = "✓" if role_real == role_esperado else "⚠"
            
            print(f"{VERDE}✅ {i}. {email}{RESET}")
            print(f"   Role: {role_real} {check}")
            print(f"   Token: {data.get('access_token', 'N/A')[:40]}...\n")
            sucesso += 1
        else:
            print(f"{VERMELHO}❌ {i}. {email}{RESET}")
            print(f"   Status: {response.status_code}\n")
    
    except Exception as e:
        print(f"{VERMELHO}❌ {i}. {email}{RESET}")
        print(f"   Erro: {str(e)}\n")

print(f"{'='*70}")
print(f"📊 RESULTADO: {sucesso}/{total} usuários com login bem-sucedido")
print(f"{'='*70}\n")

if sucesso == total:
    print(f"{VERDE}✅ ETAPA 1 FASE 3 CONCLUÍDA COM SUCESSO!{RESET}")
    print(f"\n🎯 Próximo passo: Implementar controle de acesso (RBAC)")
    print(f"                 Etapa 2: Autorização por Role/Função\n")
else:
    print(f"{VERMELHO}⚠️  {total - sucesso} usuários com problema no login{RESET}\n")
