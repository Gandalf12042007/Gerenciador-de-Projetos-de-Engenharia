#!/usr/bin/env python3
"""
Script de Migração: Usuários Hardcoded → Banco SQLite com Bcrypt
Etapa 1: Estabilidade Absoluta
"""

import sqlite3
import os
import sys
import bcrypt
from datetime import datetime

# Funções de hashing
def hash_password(password: str) -> str:
    """Hash bcrypt de senha com até 72 bytes"""
    password_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

def verify_password(plain: str, hashed: str) -> bool:
    """Verifica senha contra hash bcrypt"""
    try:
        password_bytes = plain.encode('utf-8')[:72]
        hashed_bytes = hashed.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except:
        return False

# Usuários para migrar
USUARIOS_PARA_MIGRAR = {
    "vicentedesouza762@gmail.com": {
        "nome": "Vicente de Souza",
        "senha": "Admin@2026",
        "telefone": "11 99999-0001",
        "cargo": "Administrador",
        "role": "admin"
    },
    "francisco@projeto.com": {
        "nome": "Francisco",
        "senha": "Admin@2026",
        "telefone": "11 99999-0002",
        "cargo": "Desenvolvedor",
        "role": "admin"
    },
    "professor@projeto.com": {
        "nome": "Professor",
        "senha": "Admin@2026",
        "telefone": "11 99999-0003",
        "cargo": "Professor",
        "role": "admin"
    },
    "gerenteteste@projeto.com": {
        "nome": "Gerente Teste",
        "senha": "Gerente@123",
        "telefone": "11 99999-0004",
        "cargo": "Gerente de Projetos",
        "role": "gerente"
    },
    "engenheiroteste@projeto.com": {
        "nome": "Engenheiro Teste",
        "senha": "Engenheiro@123",
        "telefone": "11 99999-0005",
        "cargo": "Engenheiro Civil",
        "role": "engenheiro"
    },
    "tecnicoteste@projeto.com": {
        "nome": "Técnico Teste",
        "senha": "Tecnico@123",
        "telefone": "11 99999-0006",
        "cargo": "Técnico em Edificações",
        "role": "tecnico"
    },
    "clienteteste@projeto.com": {
        "nome": "Cliente Teste",
        "senha": "Cliente@123",
        "telefone": "11 99999-0007",
        "cargo": "Cliente",
        "role": "cliente"
    }
}

def get_db_path():
    return os.path.join(os.path.dirname(__file__), 'gerenciador.db')

def backup_database(db_path):
    if os.path.exists(db_path):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = f"{db_path}.backup_{timestamp}"
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"✅ Backup criado: {backup_path}")
        return backup_path
    return None

def create_auth_tables(conn):
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            senha_hash TEXT NOT NULL,
            telefone TEXT,
            cargo TEXT,
            role TEXT DEFAULT 'usuario',
            ativo BOOLEAN DEFAULT TRUE,
            criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
            ultimo_login DATETIME,
            atualizado_em DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS auth_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            acao TEXT NOT NULL,
            ip_address TEXT,
            sucesso BOOLEAN,
            motivo TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS failed_login_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            ip_address TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            bloqueado_ate DATETIME
        )
    ''')
    
    conn.commit()
    print("✅ Tabelas criadas com sucesso")

def migrate_users(conn):
    cursor = conn.cursor()
    migrados = 0
    erros = []
    
    print("\n📝 Migrando usuários...\n")
    
    for email, user_data in USUARIOS_PARA_MIGRAR.items():
        try:
            email_normalized = email.lower()
            senha_hash = hash_password(user_data["senha"])
            
            cursor.execute('''
                INSERT INTO usuarios_new (nome, email, senha_hash, telefone, cargo, role, ativo)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_data["nome"],
                email_normalized,
                senha_hash,
                user_data["telefone"],
                user_data["cargo"],
                user_data["role"],
                True
            ))
            
            migrados += 1
            print(f"✅ {user_data['nome']:30} ({user_data['role']:12}) - Senha: {user_data['senha']}")
            
        except sqlite3.IntegrityError as e:
            erros.append(f"❌ {email}: Duplicado")
        except Exception as e:
            erros.append(f"❌ {email}: {str(e)}")
    
    conn.commit()
    
    print(f"\n📊 Resultado da Migração:")
    print(f"   ✅ Migrados: {migrados}")
    print(f"   ❌ Erros: {len(erros)}")
    
    if erros:
        print("\n⚠️  Erros encontrados:")
        for erro in erros:
            print(f"   {erro}")
    
    return migrados, erros

def validate_migration(conn):
    cursor = conn.cursor()
    
    print("\n🔍 Validando migração...\n")
    
    cursor.execute("SELECT COUNT(*) FROM usuarios_new")
    count = cursor.fetchone()[0]
    print(f"   Total de usuários: {count}")
    
    cursor.execute("SELECT email, role, LENGTH(senha_hash) FROM usuarios_new")
    for email, role, hash_len in cursor.fetchall():
        print(f"   {email:35} | {role:12} | Hash: {hash_len} chars")
    
    print("\n✅ Testando bcrypt verify...")
    
    cursor.execute("SELECT email, senha_hash FROM usuarios_new LIMIT 1")
    result = cursor.fetchone()
    
    if result:
        email, hash_val = result
        senha_original = USUARIOS_PARA_MIGRAR[email.lower()]["senha"]
        
        if verify_password(senha_original, hash_val):
            print(f"   ✅ Hash verificado para {email}")
            print(f"   Senha original: {senha_original}")
            print(f"   Hash: {hash_val[:20]}...")
            return True
        else:
            print(f"   ❌ Erro ao verificar hash!")
            return False
    
    return True

def print_credentials(conn):
    cursor = conn.cursor()
    
    print("\n" + "="*70)
    print("CREDENCIAIS PARA TESTE (após migração)")
    print("="*70)
    
    cursor.execute('''
        SELECT email, role, nome FROM usuarios_new ORDER BY role DESC
    ''')
    
    for email, role, nome in cursor.fetchall():
        senha = USUARIOS_PARA_MIGRAR[email.lower()]["senha"]
        print(f"\nUsuário: {nome}")
        print(f"  Email:  {email}")
        print(f"  Senha:  {senha}")
        print(f"  Papel:  {role}")
    
    print("\n" + "="*70)

def main():
    db_path = get_db_path()
    
    print("\n" + "="*70)
    print("🔄 MIGRAÇÃO: USUÁRIOS → SQLITE COM BCRYPT")
    print("="*70)
    print(f"\nBanco de dados: {db_path}\n")
    
    if not os.path.exists(db_path):
        print(f"❌ Erro: Banco não encontrado em {db_path}")
        sys.exit(1)
    
    # 1. Backup
    print("1️⃣ Criando backup...\n")
    backup_path = backup_database(db_path)
    
    # 2. Conectar
    print("2️⃣ Conectando ao banco...\n")
    conn = sqlite3.connect(db_path)
    
    try:
        # 3. Criar tabelas
        print("3️⃣ Criando novas tabelas...\n")
        create_auth_tables(conn)
        
        # 4. Migrar usuários
        print("4️⃣ Migrando usuários...\n")
        migrados, erros = migrate_users(conn)
        
        # 5. Validar
        print("\n5️⃣ Validando migração...\n")
        if not validate_migration(conn):
            print("❌ Validação falhou!")
            sys.exit(1)
        
        # 6. Exibir credenciais
        print_credentials(conn)
        
        print("\n✅ MIGRAÇÃO CONCLUÍDA COM SUCESSO!\n")
        print("📝 Próximos passos:")
        print("   1. Atualizar backend/routes/auth.py para usar banco")
        print("   2. Testar login com as credenciais acima")
        print("   3. Verificar logs em auth_logs\n")
        
    except Exception as e:
        print(f"\n❌ Erro durante migração: {e}")
        print(f"📍 Backup está em: {backup_path}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        conn.close()

if __name__ == "__main__":
    main()
