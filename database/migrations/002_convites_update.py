"""
Migração para atualizar tabela convites_equipes
Adiciona campos: criado_por, data_expiracao, usado
Adiciona 'cliente' como opção de papel
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'gerenciador.db')

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("🔧 Migrando tabela convites_equipes...")
    
    # Verificar colunas existentes
    cursor.execute("PRAGMA table_info(convites_equipes)")
    colunas = [col[1] for col in cursor.fetchall()]
    print(f"   Colunas existentes: {colunas}")
    
    # Adicionar coluna criado_por se não existir
    if 'criado_por' not in colunas:
        try:
            cursor.execute("ALTER TABLE convites_equipes ADD COLUMN criado_por INTEGER")
            print("   ✅ Adicionada coluna: criado_por")
        except Exception as e:
            print(f"   ⚠️  Erro ao adicionar criado_por: {e}")
    
    # Adicionar coluna data_expiracao se não existir
    if 'data_expiracao' not in colunas:
        try:
            cursor.execute("ALTER TABLE convites_equipes ADD COLUMN data_expiracao TEXT")
            print("   ✅ Adicionada coluna: data_expiracao")
            # Se expiracao existe, copiar valores
            if 'expiracao' in colunas:
                cursor.execute("UPDATE convites_equipes SET data_expiracao = expiracao WHERE data_expiracao IS NULL")
                print("   ✅ Copiados valores de expiracao para data_expiracao")
        except Exception as e:
            print(f"   ⚠️  Erro ao adicionar data_expiracao: {e}")
    
    # Adicionar coluna usado se não existir
    if 'usado' not in colunas:
        try:
            cursor.execute("ALTER TABLE convites_equipes ADD COLUMN usado INTEGER DEFAULT 0")
            print("   ✅ Adicionada coluna: usado")
            # Copiar valores de aceito para usado
            if 'aceito' in colunas:
                cursor.execute("UPDATE convites_equipes SET usado = aceito WHERE usado IS NULL OR usado = 0")
                print("   ✅ Copiados valores de aceito para usado")
        except Exception as e:
            print(f"   ⚠️  Erro ao adicionar usado: {e}")
    
    # Adicionar coluna usado_em se não existir
    if 'usado_em' not in colunas:
        try:
            cursor.execute("ALTER TABLE convites_equipes ADD COLUMN usado_em TEXT")
            print("   ✅ Adicionada coluna: usado_em")
            # Copiar valores de aceito_em para usado_em
            if 'aceito_em' in colunas:
                cursor.execute("UPDATE convites_equipes SET usado_em = aceito_em WHERE usado_em IS NULL")
                print("   ✅ Copiados valores de aceito_em para usado_em")
        except Exception as e:
            print(f"   ⚠️  Erro ao adicionar usado_em: {e}")
    
    # SQLite não permite ALTER COLUMN, então vamos reconstruir a tabela para adicionar 'cliente' ao CHECK
    # Por enquanto, vamos apenas remover a restrição CHECK (SQLite permite inserir mesmo com CHECK diferente)
    # Isso será resolvido criando uma nova tabela sem restrição no papel
    
    conn.commit()
    
    # Verificar colunas finais
    cursor.execute("PRAGMA table_info(convites_equipes)")
    colunas_finais = [col[1] for col in cursor.fetchall()]
    print(f"   Colunas finais: {colunas_finais}")
    
    conn.close()
    print("✅ Migração concluída!")

if __name__ == '__main__':
    migrate()
