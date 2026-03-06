#!/usr/bin/env python3
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'database', 'gerenciador.db')
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

print("=== TABELAS NO BANCO ===")
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in c.fetchall()]
print(tables)

print("\n=== USUARIOS TABELA usuarios ===")
try:
    c.execute("SELECT id, nome, email FROM usuarios LIMIT 3")
    for r in c.fetchall():
        print(f"  {r}")
except Exception as e:
    print(f"  ERRO: {e}")

print("\n=== USUARIOS TABELA usuarios_new ===")
try:
    c.execute("SELECT id, nome, email FROM usuarios_new LIMIT 3")
    for r in c.fetchall():
        print(f"  {r}")
except Exception as e:
    print(f"  ERRO: {e}")

conn.close()
