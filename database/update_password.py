import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'gerenciador.db')
NEW_HASH = "$2a$12$s6EgeoOjrce4Crmms4uM2OWMw.59gFDx3xzbUm4dbd6lPWDvzvjA6"
USER_ID = 1

print(f"Atualizando senha do usuário id={USER_ID} em: {DB_PATH}")

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Verificar existência do usuário
cur.execute('SELECT id, email, senha_hash FROM usuarios WHERE id = ?', (USER_ID,))
row = cur.fetchone()
if not row:
    print(f"Usuário id={USER_ID} não encontrado.")
    conn.close()
    raise SystemExit(1)

old_hash = row[2]
print(f"Hash anterior: {old_hash}")

cur.execute('UPDATE usuarios SET senha_hash = ? WHERE id = ?', (NEW_HASH, USER_ID))
conn.commit()
print(f"Linhas afetadas: {cur.rowcount}")

# Verificar atualização
cur.execute('SELECT senha_hash FROM usuarios WHERE id = ?', (USER_ID,))
print('Hash atual:', cur.fetchone()[0])

conn.close()
print('Concluído.')
