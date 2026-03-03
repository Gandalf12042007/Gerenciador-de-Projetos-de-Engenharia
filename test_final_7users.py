"""
Teste Completo - Todos os 7 Usuários Migrados
Com pausas para evitar rate limit
"""

import requests
import time

BASE_URL = "http://localhost:8000"
AUTH_ENDPOINT = f"{BASE_URL}/api/auth/login"

# 7 usuários migrados
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
AMARELO = '\033[93m'
RESET = '\033[0m'

print(f"\n{'='*70}")
print(f"🔐 VALIDAÇÃO FINAL - 7 USUÁRIOS MIGRADOS")
print(f"{'='*70}\n")

total = len(USUARIOS)
sucesso = 0
tokens = []

for i, (email, senha, role_esperado) in enumerate(USUARIOS, 1):
    try:
        print(f"{AMARELO}[{i}/7] Testando: {email}...{RESET}", end=" ")
        
        response = requests.post(
            AUTH_ENDPOINT,
            json={"email": email, "senha": senha},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            role_real = data.get('role')
            token = data.get('access_token')
            
            # Validar role
            if role_real == role_esperado:
                print(f"{VERDE}✅ OK (role: {role_real}){RESET}")
                sucesso += 1
                tokens.append(token)
            else:
                print(f"{VERMELHO}❌ ERRO Role (esperado: {role_esperado}, recebido: {role_real}){RESET}")
        else:
            print(f"{VERMELHO}❌ Status {response.status_code}{RESET}")
    
    except Exception as e:
        print(f"{VERMELHO}❌ Erro: {str(e)[:40]}{RESET}")
    
    # Pausa entre testes para não disparar rate limit
    if i < total:
        time.sleep(0.5)

print(f"\n{'='*70}")
print(f"📊 RESULTADO FINAL")
print(f"{'='*70}\n")

if sucesso == total:
    print(f"{VERDE}✅ SUCESSO! {sucesso}/{total} usuários validados!{RESET}\n")
    print(f"💾 Tokens obtidos: {len(tokens)}")
    print(f"\n🎯 ETAPA 1 FASE 3 CONCLUÍDA!")
    print(f"   Todos os 7 usuários migrados funcionando com bcrypt\n")
else:
    print(f"{AMARELO}⚠️  {sucesso}/{total} usuários com sucesso{RESET}")
    print(f"   {total - sucesso} usuários com problema\n")

print(f"{'='*70}\n")
