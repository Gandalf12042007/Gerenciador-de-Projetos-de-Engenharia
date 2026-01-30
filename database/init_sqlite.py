"""
Script para inicializar o banco de dados SQLite
Executa o schema e cria tabelas necessárias
"""

import os
import sys
import sqlite3

# Adicionar path do backend
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

def init_sqlite_database():
    """Inicializa o banco de dados SQLite com o schema"""
    
    # Caminho do banco
    db_path = os.getenv('SQLITE_PATH', os.path.join(os.path.dirname(__file__), 'gerenciador.db'))
    schema_path = os.path.join(os.path.dirname(__file__), 'schema_sqlite.sql')
    
    print(f"\n{'='*60}")
    print("INICIALIZANDO BANCO DE DADOS SQLite")
    print(f"{'='*60}\n")
    
    print(f"📁 Banco de dados: {db_path}")
    print(f"📄 Schema: {schema_path}")
    
    # Verificar se schema existe
    if not os.path.exists(schema_path):
        print(f"\n❌ Erro: Schema não encontrado: {schema_path}")
        return False
    
    # Ler schema
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
    
    # Conectar e executar
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Habilitar foreign keys
        cursor.execute("PRAGMA foreign_keys = ON;")
        
        # Executar schema
        cursor.executescript(schema_sql)
        conn.commit()
        
        print("\n✅ Schema executado com sucesso!")
        
        # Verificar tabelas criadas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
        tables = cursor.fetchall()
        
        print(f"\n📊 Tabelas criadas ({len(tables)}):")
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
            count = cursor.fetchone()[0]
            print(f"   • {table[0]}: {count} registros")
        
        conn.close()
        
        print(f"\n✅ Banco de dados inicializado com sucesso!")
        print(f"   Caminho: {os.path.abspath(db_path)}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erro ao inicializar banco: {e}")
        return False


def test_connection():
    """Testa a conexão com o banco"""
    from db_helper import DatabaseHelper
    
    print(f"\n{'='*60}")
    print("TESTANDO CONEXÃO")
    print(f"{'='*60}\n")
    
    try:
        db = DatabaseHelper()
        
        if db.test_connection():
            print("✅ Conexão OK!")
            
            # Testar query
            result = db.execute_query("SELECT COUNT(*) as total FROM usuarios", fetch=True)
            if result:
                print(f"✅ Total de usuários: {result[0]['total']}")
            
            return True
        else:
            print("❌ Falha na conexão")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False


if __name__ == '__main__':
    # Definir DB_TYPE como sqlite
    os.environ['DB_TYPE'] = 'sqlite'
    
    # Inicializar banco
    if init_sqlite_database():
        # Testar conexão
        test_connection()
    
    print(f"\n{'='*60}")
    print("Concluído!")
    print(f"{'='*60}\n")
