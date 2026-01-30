"""Script para criar tabela de tokens de reset de senha"""
import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'gerenciador.db')
print(f"Conectando ao banco: {db_path}")

conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Criar tabela de tokens de reset
cur.execute('''
CREATE TABLE IF NOT EXISTS tokens_reset_senha (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    token TEXT UNIQUE NOT NULL,
    expira_em TEXT NOT NULL,
    usado INTEGER DEFAULT 0,
    criado_em TEXT DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
)
''')

# Criar índice para busca rápida por token
cur.execute('CREATE INDEX IF NOT EXISTS idx_token_reset ON tokens_reset_senha(token)')

conn.commit()
print("✅ Tabela tokens_reset_senha criada com sucesso!")

# Verificar tabelas
cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tokens_reset_senha'")
if cur.fetchone():
    print("✅ Tabela confirmada no banco")
else:
    print("❌ Erro: tabela não encontrada")

conn.close()
