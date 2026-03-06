"""
Teste Final Robusto - 7 Usuários com Pausas Maiores
Para evitar disparo do rate limit de IP
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
AMARELO = '\033[93m'
RESETS = '\033[0m'

print(f"\n{'='*70}")
print(f"🔐 VALIDAÇÃO FINAL +PAUSAS - 7 USUÁRIOS MIGRADOS")
print(f"{'='*70}\n")

total = len(USUARIOS)
sucesso = 0

for i, (email, senha, role_esperado) in enumerate(USUARIOS, 1):
    try:
        print(f"{AMARELO}[{i}/7] {email:35} ", end="", flush=True)
        
        response = requests.post(
            AUTH_ENDPOINT,
            json={"email": email, "senha": senha},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            role_real = data.get('role')
            
            if role_real == role_esperado:
                print(f"{VERDE}✅ {role_real:10}{RESETS}")
                sucesso += 1
            else:
                print(f"{VERMELHO}❌ Role mismatch{RESETS}")
        else:
            print(f"{VERMELHO}❌ Status {response.status_code}{RESETS}")
    
    except Exception as e:
        print(f"{VERMELHO}❌ {str(e)[:30]}{RESETS}")
    
    # Pausa MAIOR - 2 segundos entre testes
    if i < total:
        time.sleep(2)
        
print(f"\n{'='*70}")
print(f"RESULTADO: {VERDE if sucesso == total else AMARELO}{sucesso}/{total}{RESETS}")
print(f"{'='*70}\n")
