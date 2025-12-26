#!/usr/bin/env python3
"""
Script para criar usuário de teste diretamente no banco de dados
"""

import sys
import os
import hashlib
import mysql.connector
from mysql.connector import Error

# Adicionar path do database
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'database'))

def hash_password(password):
    """Gera hash SHA-256 da senha"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_test_user():
    """Cria usuário de teste"""
    
    # Configuração do banco (ajuste conforme necessário)
    db_config = {
        'host': 'localhost',
        'port': 3306,
        'user': 'root',
        'password': 'root_password_123',  # ou sua senha do MySQL
        'database': 'gerenciador_projetos'
    }
    
    try:
        # Conectar ao banco
        connection = mysql.connector.connect(**db_config)
        
        if connection.is_connected():
            print("✓ Conectado ao MySQL")
            
            cursor = connection.cursor()
            
            # Dados do usuário de teste
            nome = "Vicente de Souza"
            email = "teste01@gmail.com"
            senha = "Teste123@"
            telefone = "11 99999-0001"
            cargo = "Administrador"
            ativo = True
            
            # Hash da senha
            senha_hash = hash_password(senha)
            
            # Verificar se usuário já existe
            cursor.execute("SELECT id FROM usuarios WHERE email = %s", (email,))
            if cursor.fetchone():
                print(f"⚠️  Usuário {email} já existe!")
                return
            
            # Inserir usuário
            cursor.execute("""
                INSERT INTO usuarios (nome, email, senha_hash, telefone, cargo, ativo, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, NOW())
            """, (nome, email, senha_hash, telefone, cargo, ativo))
            
            # Criar usuário para Francisco também
            nome_francisco = "Francisco"
            email_francisco = "francisco@gmail.com"
            telefone_francisco = "11 99999-0002"
            cargo_francisco = "Desenvolvedor"
            
            senha_hash_francisco = hash_password(senha)  # mesma senha
            
            # Verificar se Francisco já existe
            cursor.execute("SELECT id FROM usuarios WHERE email = %s", (email_francisco,))
            if not cursor.fetchone():
                cursor.execute("""
                    INSERT INTO usuarios (nome, email, senha_hash, telefone, cargo, ativo, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, NOW())
                """, (nome_francisco, email_francisco, senha_hash_francisco, telefone_francisco, cargo_francisco, ativo))
                print(f"✓ Usuário criado: {nome_francisco} ({email_francisco})")
            
            connection.commit()
            print(f"✓ Usuário criado: {nome} ({email})")
            print(f"📧 Email: {email}")
            print(f"🔑 Senha: {senha}")
            
            cursor.close()
            
    except Error as e:
        print(f"❌ Erro ao conectar ao banco: {e}")
        print("\n💡 Possíveis soluções:")
        print("1. Verificar se MySQL está rodando")
        print("2. Verificar credenciais do banco")
        print("3. Verificar se database 'gerenciador_projetos' existe")
        
    finally:
        if 'connection' in locals() and connection.is_connected():
            connection.close()
            print("✓ Desconectado do MySQL")

if __name__ == "__main__":
    create_test_user()