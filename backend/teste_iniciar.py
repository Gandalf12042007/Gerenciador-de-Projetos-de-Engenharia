# -*- coding: utf-8 -*-
"""
Script de teste para verificar problemas ao iniciar o sistema
"""

import sys
import os

print("="*60)
print("DIAGNOSTICO DO SISTEMA")
print("="*60)

# 1. Verificar Python
print(f"\nPython: {sys.version}")

# 2. Verificar modulos
print("\nVerificando modulos...")
modulos = ['fastapi', 'uvicorn', 'pydantic', 'passlib', 'jose', 'dotenv']
for modulo in modulos:
    try:
        __import__(modulo if modulo != 'jose' else 'jose')
        print(f"  OK - {modulo}")
    except ImportError:
        print(f"  ERRO - {modulo} - NAO INSTALADO!")

# 3. Verificar banco de dados
print("\nVerificando banco de dados...")
db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database", "gerenciador.db")
if os.path.exists(db_path):
    print(f"  OK - Banco encontrado: {db_path}")
    size = os.path.getsize(db_path) / 1024
    print(f"  Tamanho: {size:.2f} KB")
else:
    print(f"  ERRO - Banco NAO encontrado: {db_path}")

# 4. Verificar pasta web
print("\nVerificando frontend...")
web_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "web")
if os.path.exists(web_path):
    print(f"  OK - Pasta web: {web_path}")
    login_file = os.path.join(web_path, "login.html")
    if os.path.exists(login_file):
        print(f"  OK - login.html encontrado")
    else:
        print(f"  ERRO - login.html NAO encontrado")
else:
    print(f"  ERRO - Pasta web NAO encontrada: {web_path}")

# 5. Tentar importar rotas
print("\nVerificando rotas...")
try:
    from routes import auth, projetos, tarefas, equipes
    print("  OK - Rotas importadas com sucesso")
except Exception as e:
    print(f"  ERRO ao importar rotas: {e}")

# 6. Tentar iniciar FastAPI
print("\nTentando iniciar FastAPI...")
try:
    from fastapi import FastAPI
    app = FastAPI()
    
    @app.get("/")
    def root():
        return {"message": "Funcionando!"}
    
    print("  OK - FastAPI inicializado com sucesso!")
    print("\n" + "="*60)
    print("SISTEMA PRONTO PARA RODAR!")
    print("="*60)
    print("\nExecute: python app.py")
    
except Exception as e:
    print(f"  ERRO: {e}")
    import traceback
    traceback.print_exc()

print("\n")
