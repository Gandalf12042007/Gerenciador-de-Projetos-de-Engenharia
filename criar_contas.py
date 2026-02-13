#!/usr/bin/env python3
"""
Script para criar contas de usuário no sistema
"""

import sys
import os
import sqlite3

# Adicionar paths
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'database'))

# Import bcrypt para hash de senha
try:
    import bcrypt
    
    def hash_password(password: str) -> str:
        """Gera hash bcrypt da senha"""
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')
except ImportError:
    import hashlib
    print("⚠️  bcrypt não instalado, usando SHA-256")
    
    def hash_password(password: str) -> str:
        """Gera hash SHA-256 da senha (fallback)"""
        return hashlib.sha256(password.encode()).hexdigest()

# Caminho do banco SQLite
DB_PATH = os.path.join(os.path.dirname(__file__), 'database', 'gerenciador.db')

# Contas a serem criadas
CONTAS = [
    # Administradores
    {
        'nome': 'Vicente de Souza',
        'email': 'vicentedesouza762@gmail.com',
        'senha': 'Admin@2026',
        'telefone': '(11) 99999-0001',
        'cargo': 'admin'
    },
    {
        'nome': 'Francisco',
        'email': 'francisco@projeto.com',
        'senha': 'Admin@2026',
        'telefone': '(11) 99999-0002',
        'cargo': 'admin'
    },
    {
        'nome': 'Professor',
        'email': 'professor@projeto.com',
        'senha': 'Admin@2026',
        'telefone': '(11) 99999-0003',
        'cargo': 'admin'
    },
    # Gerente de teste
    {
        'nome': 'Gerente Teste',
        'email': 'gerenteteste@projeto.com',
        'senha': 'Gerente@123',
        'telefone': '(11) 98888-0001',
        'cargo': 'gerente'
    },
    # Engenheiro de teste
    {
        'nome': 'Engenheiro Teste',
        'email': 'engenheiroteste@projeto.com',
        'senha': 'Engenheiro@123',
        'telefone': '(11) 97777-0001',
        'cargo': 'engenheiro'
    },
    # Técnico de teste
    {
        'nome': 'Técnico Teste',
        'email': 'tecnicoteste@projeto.com',
        'senha': 'Tecnico@123',
        'telefone': '(11) 96666-0001',
        'cargo': 'tecnico'
    },
    # Cliente de teste
    {
        'nome': 'Cliente Teste',
        'email': 'clienteteste@projeto.com',
        'senha': 'Cliente@123',
        'telefone': '(11) 95555-0001',
        'cargo': 'cliente'
    }
]

def criar_contas():
    """Cria as contas no banco de dados"""
    
    print(f"\n📁 Banco de dados: {DB_PATH}")
    
    if not os.path.exists(DB_PATH):
        print("❌ Banco de dados não encontrado!")
        print("   Execute primeiro o sistema para criar o banco.")
        return False
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("\n" + "="*60)
    print("🔧 CRIANDO CONTAS DE USUÁRIO")
    print("="*60 + "\n")
    
    criados = 0
    existentes = 0
    
    for conta in CONTAS:
        # Verificar se já existe
        cursor.execute("SELECT id FROM usuarios WHERE email = ?", (conta['email'],))
        existente = cursor.fetchone()
        
        if existente:
            print(f"⚠️  {conta['nome']} ({conta['email']}) - JÁ EXISTE (ID: {existente[0]})")
            existentes += 1
            continue
        
        # Criar hash da senha
        senha_hash = hash_password(conta['senha'])
        
        # Inserir usuário
        try:
            cursor.execute("""
                INSERT INTO usuarios (nome, email, senha_hash, telefone, cargo, ativo)
                VALUES (?, ?, ?, ?, ?, 1)
            """, (conta['nome'], conta['email'], senha_hash, conta['telefone'], conta['cargo']))
            
            user_id = cursor.lastrowid
            print(f"✅ {conta['nome']} ({conta['email']}) - CRIADO (ID: {user_id})")
            print(f"   📧 Email: {conta['email']}")
            print(f"   🔑 Senha: {conta['senha']}")
            print(f"   👤 Cargo: {conta['cargo']}")
            print()
            criados += 1
            
        except Exception as e:
            print(f"❌ Erro ao criar {conta['nome']}: {e}")
    
    conn.commit()
    conn.close()
    
    print("\n" + "="*60)
    print(f"📊 RESUMO: {criados} criados, {existentes} já existentes")
    print("="*60)
    
    # Mostrar resumo de logins
    print("\n📋 CREDENCIAIS DE ACESSO:")
    print("-"*60)
    print(f"{'Email':<35} {'Senha':<20} {'Cargo':<12}")
    print("-"*60)
    for conta in CONTAS:
        print(f"{conta['email']:<35} {conta['senha']:<20} {conta['cargo']:<12}")
    print("-"*60)
    
    return True

if __name__ == '__main__':
    criar_contas()
