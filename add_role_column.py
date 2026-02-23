#!/usr/bin/env python3
import sqlite3

conn = sqlite3.connect('database/gerenciador.db')
c = conn.cursor()
try:
    c.execute('ALTER TABLE usuarios ADD COLUMN role TEXT DEFAULT "colaborador"')
    conn.commit()
    print('✅ Coluna role adicionada com sucesso!')
except sqlite3.OperationalError as e:
    if 'already exists' in str(e):
        print('✅ Coluna role já existe')
    else:
        print(f'❌ Erro: {e}')
finally:
    conn.close()
