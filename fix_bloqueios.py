import sqlite3
from datetime import datetime

DB_PATH = 'database/gerenciador.db'

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Ver tabelas
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tabelas = [r[0] for r in cursor.fetchall()]
print('Tabelas:', tabelas)

# Limpar tabela de tentativas falhadas
if 'failed_login_attempts' in tabelas:
    cursor.execute('SELECT COUNT(*) FROM failed_login_attempts')
    total = cursor.fetchone()[0]
    print(f'Registros antes: {total}')
    
    cursor.execute('DELETE FROM failed_login_attempts')
    conn.commit()
    print(f'Todos os bloqueios removidos!')
else:
    print('Tabela failed_login_attempts NAO encontrada')

# Verificar se existe coluna de bloqueio nos usuarios
cursor.execute("PRAGMA table_info(usuarios_new)")
cols = [r[1] for r in cursor.fetchall()]
print('Colunas usuarios_new:', cols)

conn.close()
print('Pronto - bloqueios limpos!')
