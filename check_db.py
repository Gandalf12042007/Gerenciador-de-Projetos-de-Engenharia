#!/usr/bin/env python
"""Script para verificar estado do banco de dados"""
import sqlite3

def main():
    conn = sqlite3.connect('database/gerenciador.db')
    cursor = conn.cursor()
    
    # Listar tabelas
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [t[0] for t in cursor.fetchall()]
    print("📊 TABELAS NO BANCO:")
    for t in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {t}")
        count = cursor.fetchone()[0]
        print(f"  - {t}: {count} registros")
    
    # Verificar estrutura da tabela usuarios
    print("\n🔍 COLUNAS DA TABELA USUARIOS:")
    cursor.execute("PRAGMA table_info(usuarios)")
    cols = cursor.fetchall()
    for c in cols:
        print(f"  - {c[1]} ({c[2]})")
    
    # Verificar usuários
    print("\n👥 USUÁRIOS CADASTRADOS:")
    cursor.execute("SELECT id, nome, email, cargo FROM usuarios LIMIT 10")
    users = cursor.fetchall()
    for u in users:
        print(f"  - ID {u[0]}: {u[1]} ({u[2]}) - {u[3] or 'sem cargo'}")
    
    # Verificar projetos
    print("\n📁 PROJETOS:")
    cursor.execute("SELECT id, nome, status FROM projetos LIMIT 5")
    projs = cursor.fetchall()
    for p in projs:
        print(f"  - ID {p[0]}: {p[1]} ({p[2]})")
    
    conn.close()

if __name__ == "__main__":
    main()
