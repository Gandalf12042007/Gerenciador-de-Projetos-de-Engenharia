#!/usr/bin/env python
"""
Script para criar/resetar senha de usuário admin no SQLite
"""

import sqlite3
import bcrypt

def hash_password(password: str) -> str:
    """Cria hash bcrypt da senha"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()

def verify_password(password: str, password_hash: str) -> bool:
    """Verifica senha contra hash"""
    try:
        return bcrypt.checkpw(password.encode(), password_hash.encode())
    except:
        return False

def main():
    conn = sqlite3.connect('database/gerenciador.db')
    cursor = conn.cursor()
    
    # Verificar usuários existentes em usuarios_new (tabela usada pelo login)
    print("\n📊 USUÁRIOS NA TABELA usuarios_new:")
    cursor.execute("SELECT id, nome, email, role FROM usuarios_new")
    for u in cursor.fetchall():
        print(f"  ID {u[0]}: {u[1]} ({u[2]}) - role: {u[3]}")
    
    # Criar/atualizar usuário admin de teste na tabela usuarios_new
    admin_email = "admin@sistema.com"
    admin_senha = "Admin123!"
    admin_hash = hash_password(admin_senha)
    
    # Verificar se existe em usuarios_new
    cursor.execute("SELECT id FROM usuarios_new WHERE email = ?", (admin_email,))
    existing = cursor.fetchone()
    
    if existing:
        # Atualizar senha
        cursor.execute(
            "UPDATE usuarios_new SET senha_hash = ?, role = 'admin' WHERE email = ?",
            (admin_hash, admin_email)
        )
        print(f"\n✅ Senha atualizada para: {admin_email}")
    else:
        # Criar novo em usuarios_new
        cursor.execute("""
            INSERT INTO usuarios_new (nome, email, senha_hash, cargo, role, ativo, criado_em, atualizado_em)
            VALUES (?, ?, ?, ?, ?, 1, datetime('now'), datetime('now'))
        """, ("Administrador Sistema", admin_email, admin_hash, "Administrador", "admin"))
        print(f"\n✅ Usuário admin criado em usuarios_new: {admin_email}")
    
    conn.commit()
    
    # Verificar se a senha funciona
    cursor.execute("SELECT senha_hash FROM usuarios_new WHERE email = ?", (admin_email,))
    row = cursor.fetchone()
    if row:
        is_valid = verify_password(admin_senha, row[0])
        print(f"\n🔐 Verificação de senha: {'✅ OK' if is_valid else '❌ FALHOU'}")
    
    print("\n📋 CREDENCIAIS DE ACESSO:")
    print(f"   Email: {admin_email}")
    print(f"   Senha: {admin_senha}")
    
    conn.close()

if __name__ == "__main__":
    main()
