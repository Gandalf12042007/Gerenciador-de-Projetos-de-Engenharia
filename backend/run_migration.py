"""
Script de migração para adicionar código de acesso aos projetos
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'gerenciador.db')

def run_migration():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("Executando migração...")
    
    # Verificar se coluna codigo_acesso já existe
    cursor.execute('PRAGMA table_info(projetos)')
    colunas = [col[1] for col in cursor.fetchall()]
    print(f'Colunas projetos: {colunas}')
    
    if 'codigo_acesso' not in colunas:
        cursor.execute('ALTER TABLE projetos ADD COLUMN codigo_acesso TEXT')
        print('✓ Coluna codigo_acesso adicionada!')
    else:
        print('- Coluna codigo_acesso já existe')
    
    # Verificar se coluna role já existe em usuarios
    cursor.execute('PRAGMA table_info(usuarios)')
    colunas_usuarios = [col[1] for col in cursor.fetchall()]
    print(f'Colunas usuarios: {colunas_usuarios}')
    
    if 'role' not in colunas_usuarios:
        cursor.execute("ALTER TABLE usuarios ADD COLUMN role TEXT DEFAULT 'usuario'")
        print('✓ Coluna role adicionada em usuarios!')
    else:
        print('- Coluna role já existe')
    
    # Verificar se coluna funcao já existe em equipes
    cursor.execute('PRAGMA table_info(equipes)')
    colunas_equipes = [col[1] for col in cursor.fetchall()]
    print(f'Colunas equipes: {colunas_equipes}')
    
    if 'funcao' not in colunas_equipes:
        cursor.execute("ALTER TABLE equipes ADD COLUMN funcao TEXT DEFAULT 'membro'")
        print('✓ Coluna funcao adicionada em equipes!')
    else:
        print('- Coluna funcao já existe')
    
    # Criar índice para codigo_acesso se não existir
    try:
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_projetos_codigo ON projetos(codigo_acesso)')
        print('✓ Índice idx_projetos_codigo criado!')
    except Exception as e:
        print(f'- Índice já existe ou erro: {e}')
    
    conn.commit()
    conn.close()
    print('\n✅ Migração concluída com sucesso!')

if __name__ == "__main__":
    run_migration()
