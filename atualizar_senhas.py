#!/usr/bin/env python3
"""
Script para atualizar senhas das contas
"""

import sys
import os
import sqlite3

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

try:
    import bcrypt
    
    def hash_password(password: str) -> str:
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')
except ImportError:
    import hashlib
    def hash_password(password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

DB_PATH = os.path.join(os.path.dirname(__file__), 'database', 'gerenciador.db')

SENHAS = {
    'vicentedesouza762@gmail.com': 'Admin@2026',
    'francisco@projeto.com': 'Admin@2026',
    'professor@projeto.com': 'Admin@2026',
    'gerenteteste@projeto.com': 'Gerente@123',
    'engenheiroteste@projeto.com': 'Engenheiro@123',
    'tecnicoteste@projeto.com': 'Tecnico@123',
    'clienteteste@projeto.com': 'Cliente@123'
}

def atualizar_senhas():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("\n🔐 Atualizando senhas...")
    
    for email, senha in SENHAS.items():
        senha_hash = hash_password(senha)
        cursor.execute("UPDATE usuarios SET senha_hash = ? WHERE email = ?", (senha_hash, email))
        if cursor.rowcount > 0:
            print(f"   ✅ {email}: senha atualizada")
        else:
            print(f"   ⚠️  {email}: usuário não encontrado")
    
    conn.commit()
    conn.close()
    
    print("\n📋 CREDENCIAIS DE ACESSO:")
    print("-"*60)
    for email, senha in SENHAS.items():
        print(f"   {email}  →  {senha}")
    print("-"*60)

if __name__ == '__main__':
    atualizar_senhas()
