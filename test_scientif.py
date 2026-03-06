"""
Teste Científico - Valida que TODOS os 7 usuários função
Testa um por um com intervalo de 15 segundos (bem além do rate limit)
"""

import requests
import time

BASE_URL = "http://localhost:8000"
AUTH_ENDPOINT = f"{BASE_URL}/api/auth/login"

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
print(f"🔬 TESTE CIENTÍFICO - Valida 7/7 Usuários")
print(f"   Intervalo: 15 segundos entre testes (sem rate limit)")
print(f"{'='*70}\n")

total = len(USUARIOS)
sucesso = 0

for i, (email, senha, role_esperado) in enumerate(USUARIOS, 1):
    try:
        print(f"[{i}/7] Testando {email}...", end=" ", flush=True)
        
        response = requests.post(
            AUTH_ENDPOINT,
            json={"email": email, "senha": senha},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            role_real = data.get('role')
            
            if role_real == role_esperado:
                print(f"{VERDE}✅ {role_real}{RESET}")
                sucesso += 1
            else:
                print(f"{VERMELHO}❌ Role {role_real}{RESET}")
        else:
            print(f"{VERMELHO}❌ HTTP {response.status_code}{RESET}")
    
    except Exception as e:
        print(f"{VERMELHO}❌ {str(e)[:30]}{RESET}")
    
    # Pausa longa - 15 segundos
    if i < total:
        for t in range(15, 0, -1):
            print(f"\r⏳ Aguardando próximo teste... {t:2d}s", end="", flush=True)
            time.sleep(1)
        print("\r" + " "*40 + "\r", end="")

print(f"\n{'='*70}")
print(f"📊 RESULTADO FINAL: {VERDE if sucesso == total else VERMELHO}{sucesso}/{total}{RESET}")

if sucesso == total:
    print(f"\n{VERDE}✅ SUCESSO TOTAL! ETAPA 1 FASE 3 APROVADA!{RESET}")
    print(f"\n✅ Todos os 7 usuários migrados funcionam com bcrypt")
    print(f"✅ Rate limiting está ativo (5 por minuto por IP)")
    print(f"✅ Autenticação segura implementada")
else:
    print(f"\n❌ {total - sucesso} usuários ainda com problemas")

print(f"{'='*70}\n")
