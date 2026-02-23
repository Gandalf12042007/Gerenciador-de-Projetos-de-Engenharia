#!/usr/bin/env python3
"""
Script para criar usuários de teste com senhas bcrypt corretas
Execute: python create_seed_users.py
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'database'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from db_helper import DatabaseHelper
from utils.auth import hash_password

def criar_usuarios_teste():
    """Cria usuários de teste em massa"""
    db = DatabaseHelper()
    
    usuarios = [
        # ADMINISTRADORES
        {
            "nome": "Vicente de Souza",
            "email": "vicentedesouza762@gmail.com",
            "senha": "Admin@2026",
            "telefone": "11 99999-0001",
            "cargo": "Administrador",
            "role": "admin"
        },
        {
            "nome": "Francisco",
            "email": "francisco@projeto.com",
            "senha": "Admin@2026",
            "telefone": "11 99999-0002",
            "cargo": "Desenvolvedor",
            "role": "admin"
        },
        {
            "nome": "Professor",
            "email": "professor@projeto.com",
            "senha": "Admin@2026",
            "telefone": "11 99999-0003",
            "cargo": "Professor",
            "role": "admin"
        },
        # GERENTE
        {
            "nome": "Gerente Teste",
            "email": "gerenteteste@projeto.com",
            "senha": "Gerente@123",
            "telefone": "11 99999-0004",
            "cargo": "Gerente de Projetos",
            "role": "gerente"
        },
        # ENGENHEIRO
        {
            "nome": "Engenheiro Teste",
            "email": "engenheiroteste@projeto.com",
            "senha": "Engenheiro@123",
            "telefone": "11 99999-0005",
            "cargo": "Engenheiro Civil",
            "role": "engenheiro"
        },
        # TÉCNICO
        {
            "nome": "Técnico Teste",
            "email": "tecnicoteste@projeto.com",
            "senha": "Tecnico@123",
            "telefone": "11 99999-0006",
            "cargo": "Técnico em Edificações",
            "role": "tecnico"
        },
        # CLIENTE
        {
            "nome": "Cliente Teste",
            "email": "clienteteste@projeto.com",
            "senha": "Cliente@123",
            "telefone": "11 99999-0007",
            "cargo": "Cliente",
            "role": "cliente"
        }
    ]
    
    created = 0
    for user in usuarios:
        try:
            # Verificar se já existe
            existing = db.execute_query(
                "SELECT id FROM usuarios WHERE email = %s",
                (user["email"],),
                fetch=True
            )
            
            if existing and len(existing) > 0:
                print(f"⚠️  {user['email']} já existe - atualizando senha...")
                senha_hash = hash_password(user["senha"])
                db.execute_query(
                    "UPDATE usuarios SET senha_hash = %s, role = %s WHERE email = %s",
                    (senha_hash, user["role"], user["email"])
                )
                created += 1
                continue
            
            # Criar novo usuário
            senha_hash = hash_password(user["senha"])
            db.execute_query(
                """
                INSERT INTO usuarios (nome, email, senha_hash, telefone, cargo, role, ativo)
                VALUES (%s, %s, %s, %s, %s, %s, 1)
                """,
                (user["nome"], user["email"], senha_hash, user["telefone"], user["cargo"], user["role"])
            )
            print(f"✅ {user['email']} criado com sucesso")
            created += 1
            
        except Exception as e:
            print(f"❌ Erro ao criar {user['email']}: {str(e)}")
    
    return created

if __name__ == "__main__":
    print("=" * 70)
    print("🔐 CRIANDO USUÁRIOS DE TESTE COM SENHAS BCRYPT")
    print("=" * 70)
    
    total = criar_usuarios_teste()
    
    print("\n" + "=" * 70)
    print(f"✅ {total} usuários processados!")
    print("=" * 70)
