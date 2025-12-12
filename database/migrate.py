"""
Sistema de Migrations - Gerenciador de Projetos
Executa migrations SQL de forma versionada e controlada
"""

import os
import sys
from pathlib import Path
import mysql.connector
from mysql.connector import Error
from datetime import datetime
import re
from dotenv import load_dotenv

# Carregar variáveis do .env
load_dotenv()

class MigrationManager:
    def __init__(self, db_config):
        """
        Inicializa o gerenciador de migrations
        
        Args:
            db_config (dict): Configuração do banco de dados
                {
                    'host': 'localhost',
                    'user': 'root',
                    'password': 'senha',
                    'database': 'gerenciador_projetos'
                }
        """
        self.db_config = db_config
        self.migrations_dir = Path(__file__).parent / 'migrations'
        self.connection = None
        
    def connect(self):
        """Conecta ao banco de dados"""
        try:
            self.connection = mysql.connector.connect(**self.db_config)
            if self.connection.is_connected():
                print(f"✓ Conectado ao MySQL - {self.db_config['database']}")
                return True
        except Error as e:
            print(f"✗ Erro ao conectar: {e}")
            return False
    
    def disconnect(self):
        """Desconecta do banco de dados"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("✓ Desconectado do MySQL")
    
    def get_executed_migrations(self):
        """Retorna lista de migrations já executadas"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT versao FROM _migrations ORDER BY versao")
            migrations = [row[0] for row in cursor.fetchall()]
            cursor.close()
            return migrations
        except Error:
            # Tabela _migrations ainda não existe
            return []
    
    def get_pending_migrations(self):
        """Retorna lista de migrations pendentes"""
        executed = self.get_executed_migrations()
        all_migrations = sorted([
            f.name for f in self.migrations_dir.glob('*.sql')
            if re.match(r'^\d{3}_', f.name)
        ])
        
        pending = []
        for migration_file in all_migrations:
            version = migration_file.split('_')[0]
            if version not in executed:
                pending.append(migration_file)
        
        return pending
    
    def execute_migration(self, migration_file):
        """Executa uma migration específica"""
        file_path = self.migrations_dir / migration_file
        
        print(f"\n→ Executando: {migration_file}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                sql_content = f.read()
            
            # Divide em statements individuais
            statements = [s.strip() for s in sql_content.split(';') if s.strip()]
            
            cursor = self.connection.cursor()
            
            for statement in statements:
                if statement:
                    cursor.execute(statement)
            
            self.connection.commit()
            cursor.close()
            
            print(f"  ✓ Migration {migration_file} executada com sucesso!")
            return True
            
        except Error as e:
            print(f"  ✗ Erro ao executar {migration_file}: {e}")
            self.connection.rollback()
            return False
    
    def run_migrations(self):
        """Executa todas as migrations pendentes"""
        if not self.connect():
            return False
        
        pending = self.get_pending_migrations()
        
        if not pending:
            print("\n✓ Nenhuma migration pendente. Banco de dados atualizado!")
            self.disconnect()
            return True
        
        print(f"\n📦 {len(pending)} migration(s) pendente(s):\n")
        for migration in pending:
            print(f"  • {migration}")
        
        print("\n" + "="*60)
        
        success_count = 0
        for migration in pending:
            if self.execute_migration(migration):
                success_count += 1
            else:
                print(f"\n✗ Migration falhou. Processo interrompido.")
                break
        
        print("\n" + "="*60)
        print(f"\n✓ {success_count}/{len(pending)} migration(s) executada(s) com sucesso!")
        
        self.disconnect()
        return success_count == len(pending)
    
    def status(self):
        """Mostra status das migrations"""
        if not self.connect():
            return
        
        executed = self.get_executed_migrations()
        pending = self.get_pending_migrations()
        
        print("\n" + "="*60)
        print("STATUS DAS MIGRATIONS")
        print("="*60)
        
        print(f"\n✓ Executadas: {len(executed)}")
        if executed:
            for version in executed:
                print(f"  • {version}")
        
        print(f"\n⏳ Pendentes: {len(pending)}")
        if pending:
            for migration in pending:
                print(f"  • {migration}")
        else:
            print("  (Nenhuma)")
        
        print("\n" + "="*60 + "\n")
        
        self.disconnect()
    
    def create_database_if_not_exists(self):
        """Cria o banco de dados se não existir"""
        try:
            # Conecta sem especificar database
            temp_config = self.db_config.copy()
            database_name = temp_config.pop('database')
            
            connection = mysql.connector.connect(**temp_config)
            cursor = connection.cursor()
            
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database_name} "
                          "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            
            print(f"✓ Database '{database_name}' verificado/criado")
            
            cursor.close()
            connection.close()
            
            return True
            
        except Error as e:
            print(f"✗ Erro ao criar database: {e}")
            return False


def main():
    """Função principal"""
    # Configuração do banco de dados
    # Pode ser sobrescrito por variáveis de ambiente
    db_config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', ''),
        'database': os.getenv('DB_NAME', 'gerenciador_projetos'),
        'port': int(os.getenv('DB_PORT', 3306))
    }
    
    manager = MigrationManager(db_config)
    
    # Processa argumentos da linha de comando
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'status':
            manager.status()
        elif command == 'run':
            manager.create_database_if_not_exists()
            manager.run_migrations()
        elif command == 'help':
            print("""
Uso: python migrate.py [comando]

Comandos:
  run      - Executa todas as migrations pendentes
  status   - Mostra status das migrations (executadas e pendentes)
  help     - Mostra esta mensagem de ajuda

Variáveis de ambiente:
  DB_HOST     - Host do MySQL (padrão: localhost)
  DB_USER     - Usuário do MySQL (padrão: root)
  DB_PASSWORD - Senha do MySQL (padrão: vazio)
  DB_NAME     - Nome do database (padrão: gerenciador_projetos)
  DB_PORT     - Porta do MySQL (padrão: 3306)

Exemplos:
  python migrate.py run
  python migrate.py status
  
  # Com variáveis de ambiente:
  DB_PASSWORD=minhasenha python migrate.py run
            """)
        else:
            print(f"Comando desconhecido: {command}")
            print("Use 'python migrate.py help' para ver os comandos disponíveis")
    else:
        # Por padrão, executa as migrations
        print("\n" + "="*60)
        print("GERENCIADOR DE MIGRATIONS - Projetos de Engenharia")
        print("="*60)
        
        manager.create_database_if_not_exists()
        manager.run_migrations()


if __name__ == '__main__':
    main()
