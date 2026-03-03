#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TESTE DE FLUXO COMPLETO: LOGIN → DASHBOARD
Simula o fluxo completo do usuário
"""

import subprocess
import time
import webbrowser
from datetime import datetime

print(f"\n{'='*60}")
print(f"TESTE COMPLETO: LOGIN -> DASHBOARD")
print(f"{'='*60}")
print(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
print(f"{'='*60}\n")

print("1. Abrindo navegador com página de login...")
webbrowser.open('http://localhost:8000/login')

print("\n2. Instruções:")
print("   Email: vicentedesouza762@gmail.com")
print("   Senha: Admin@2026")
print("   Clique em LOGIN")

print("\n3. Aguarde o redirecionamento para o Dashboard...")
print("   Esperando 5 segundos antes de abrir...")\

time.sleep(5)

print("\n4. Abrindo Dashboard...")
webbrowser.open('http://localhost:8000/projects/dashboard.html')

print("\n5. Se a página carregar sem erros, o problema foi resolvido!")
print(f"\n{'='*60}")
print("Verifique o Console (F12) para ver detalhes!") 
print(f"{'='*60}\n")
