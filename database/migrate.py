"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║               SISTEMA DE MIGRATIONS - GERENCIADOR DE PROJETOS                  ║
║                                                                                 ║
║  Descrição: Executa migrations SQL de forma versionada e controlada            ║
║  Autor: Equipe de Desenvolvimento                                              ║
║  Versão: 1.0.0                                                                  ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""

# ══════════════════════════════════════════════════════════════════════════════
# IMPORTS
# ══════════════════════════════════════════════════════════════════════════════

import os
import sys
import re
from pathlib import Path
from datetime import datetime

# Dependências externas
import mysql.connector
from mysql.connector import Error


# ══════════════════════════════════════════════════════════════════════════════
# CLASSE PRINCIPAL: MigrationManager
# ══════════════════════════════════════════════════════════════════════════════

class MigrationManager:
    """
    ┌─────────────────────────────────────────────────────────────────────────┐
    │  Gerenciador de Migrations para banco de dados MySQL                    │
    │                                                                         │
    │  Responsabilidades:                                                     │
    │    • Conexão e desconexão do banco de dados                            │
    │    • Verificação de migrations executadas e pendentes                   │
    │    • Execução de migrations SQL em ordem versionada                     │
    │    • Criação automática do banco de dados                               │
    └─────────────────────────────────────────────────────────────────────────┘
    """
    
    # ──────────────────────────────────────────────────────────────────────────
    # INICIALIZAÇÃO
    # ──────────────────────────────────────────────────────────────────────────
    
    def __init__(self, db_config: dict):
        """
        Inicializa o gerenciador de migrations.
        
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
    
    # ──────────────────────────────────────────────────────────────────────────
    # CONEXÃO COM O BANCO DE DADOS
    # ──────────────────────────────────────────────────────────────────────────
        
    def connect(self) -> bool:
        """
        Estabelece conexão com o banco de dados MySQL.
        
        Returns:
            bool: True se conectou com sucesso, False caso contrário
        """
        try:
            self.connection = mysql.connector.connect(**self.db_config)
            if self.connection.is_connected():
                print(f"    ✅ Conectado ao MySQL - {self.db_config['database']}")
                return True
        except Error as e:
            print(f"    ❌ Erro ao conectar: {e}")
            return False
    
    def disconnect(self) -> None:
        """Encerra a conexão com o banco de dados."""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("    ✅ Desconectado do MySQL")
    
    # ──────────────────────────────────────────────────────────────────────────
    # CONSULTAS DE MIGRATIONS
    # ──────────────────────────────────────────────────────────────────────────
    
    def get_executed_migrations(self) -> list:
        """
        Obtém a lista de migrations já executadas no banco.
        
        Returns:
            list: Lista de versões de migrations executadas
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT versao FROM _migrations ORDER BY versao")
            migrations = [row[0] for row in cursor.fetchall()]
            cursor.close()
            return migrations
        except Error:
            # Tabela _migrations ainda não existe
            return []
    
    def get_pending_migrations(self) -> list:
        """
        Obtém a lista de migrations pendentes de execução.
        
        Returns:
            list: Lista de arquivos de migrations pendentes
        """
        executed = self.get_executed_migrations()
        
        # Lista todos os arquivos SQL que seguem o padrão NNN_nome.sql
        all_migrations = sorted([
            f.name for f in self.migrations_dir.glob('*.sql')
            if re.match(r'^\d{3}_', f.name)
        ])
        
        # Filtra apenas as não executadas
        pending = []
        for migration_file in all_migrations:
            version = migration_file.split('_')[0]
            if version not in executed:
                pending.append(migration_file)
        
        return pending
    
    # ──────────────────────────────────────────────────────────────────────────
    # EXECUÇÃO DE MIGRATIONS
    # ──────────────────────────────────────────────────────────────────────────
    
    def execute_migration(self, migration_file: str) -> bool:
        """
        Executa uma migration específica.
        
        Args:
            migration_file (str): Nome do arquivo de migration
            
        Returns:
            bool: True se executou com sucesso, False caso contrário
        """
        file_path = self.migrations_dir / migration_file
        
        print(f"\n    🔄 Executando: {migration_file}")
        
        try:
            # Lê o conteúdo SQL
            with open(file_path, 'r', encoding='utf-8') as f:
                sql_content = f.read()
            
            # Divide em statements individuais
            statements = [s.strip() for s in sql_content.split(';') if s.strip()]
            
            cursor = self.connection.cursor()
            
            # Executa cada statement
            for statement in statements:
                if statement:
                    cursor.execute(statement)
            
            self.connection.commit()
            cursor.close()
            
            print(f"       ✅ Migration {migration_file} executada com sucesso!")
            return True
            
        except Error as e:
            print(f"       ❌ Erro ao executar {migration_file}: {e}")
            self.connection.rollback()
            return False
    
    def run_migrations(self) -> bool:
        """
        Executa todas as migrations pendentes em ordem.
        
        Returns:
            bool: True se todas foram executadas, False caso alguma falhe
        """
        if not self.connect():
            return False
        
        pending = self.get_pending_migrations()
        
        if not pending:
            print("\n    ✅ Nenhuma migration pendente. Banco de dados atualizado!")
            self.disconnect()
            return True
        
        # Mostra migrations pendentes
        print(f"\n    📦 {len(pending)} migration(s) pendente(s):")
        print("    " + "─" * 50)
        for migration in pending:
            print(f"       • {migration}")
        print("    " + "─" * 50)
        
        # Executa cada migration
        success_count = 0
        for migration in pending:
            if self.execute_migration(migration):
                success_count += 1
            else:
                print(f"\n    ❌ Migration falhou. Processo interrompido.")
                break
        
        # Resultado final
        print("\n    " + "─" * 50)
        if success_count == len(pending):
            print(f"    ✅ {success_count}/{len(pending)} migration(s) executada(s) com sucesso!")
        else:
            print(f"    ⚠️  {success_count}/{len(pending)} migration(s) executada(s)")
        
        self.disconnect()
        return success_count == len(pending)
    
    # ──────────────────────────────────────────────────────────────────────────
    # STATUS E INFORMAÇÕES
    # ──────────────────────────────────────────────────────────────────────────
    
    def status(self) -> None:
        """Exibe o status atual das migrations (executadas e pendentes)."""
        if not self.connect():
            return
        
        executed = self.get_executed_migrations()
        pending = self.get_pending_migrations()
        
        print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                 STATUS DAS MIGRATIONS                     ║
    ╠═══════════════════════════════════════════════════════════╣""")
        
        # Migrations executadas
        print(f"    ║  ✅ EXECUTADAS: {len(executed):>3}                                  ║")
        if executed:
            for version in executed:
                print(f"    ║     • {version:<50} ║")
        
        # Migrations pendentes
        print(f"    ║  ⏳ PENDENTES:  {len(pending):>3}                                  ║")
        if pending:
            for migration in pending:
                nome_curto = migration[:45] + "..." if len(migration) > 48 else migration
                print(f"    ║     • {nome_curto:<50} ║")
        else:
            print("    ║     (Nenhuma)                                           ║")
        
        print("    ╚═══════════════════════════════════════════════════════════╝\n")
        
        self.disconnect()
    
    # ──────────────────────────────────────────────────────────────────────────
    # CRIAÇÃO DO BANCO DE DADOS
    # ──────────────────────────────────────────────────────────────────────────
    
    def create_database_if_not_exists(self) -> bool:
        """
        Cria o banco de dados se ele ainda não existir.
        
        Returns:
            bool: True se criado/verificado com sucesso, False caso contrário
        """
        try:
            # Conecta sem especificar database
            temp_config = self.db_config.copy()
            database_name = temp_config.pop('database')
            
            connection = mysql.connector.connect(**temp_config)
            cursor = connection.cursor()
            
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS {database_name} "
                "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
            
            print(f"    ✅ Database '{database_name}' verificado/criado")
            
            cursor.close()
            connection.close()
            
            return True
            
        except Error as e:
            print(f"    ❌ Erro ao criar database: {e}")
            return False


# ══════════════════════════════════════════════════════════════════════════════
# FUNÇÃO PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════

def print_header() -> None:
    """Exibe o cabeçalho do sistema."""
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║     🔧 GERENCIADOR DE MIGRATIONS - Projetos de Engenharia ║
    ╠═══════════════════════════════════════════════════════════╣
    ║  Sistema de versionamento de banco de dados               ║
    ╚═══════════════════════════════════════════════════════════╝
    """)


def print_help() -> None:
    """Exibe a mensagem de ajuda do sistema."""
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                    📖 AJUDA - MIGRATE.PY                   ║
    ╠═══════════════════════════════════════════════════════════╣
    ║  USO: python migrate.py [comando]                         ║
    ╠═══════════════════════════════════════════════════════════╣
    ║                                                           ║
    ║  📌 COMANDOS DISPONÍVEIS:                                  ║
    ║  ─────────────────────────────────────────────────────────║
    ║   run       Executa todas as migrations pendentes         ║
    ║   status    Mostra status das migrations                  ║
    ║   help      Mostra esta mensagem de ajuda                 ║
    ║                                                           ║
    ╠═══════════════════════════════════════════════════════════╣
    ║  🔧 VARIÁVEIS DE AMBIENTE:                                 ║
    ║  ─────────────────────────────────────────────────────────║
    ║   DB_HOST      Host do MySQL       (padrão: localhost)    ║
    ║   DB_USER      Usuário do MySQL    (padrão: root)         ║
    ║   DB_PASSWORD  Senha do MySQL      (padrão: vazio)        ║
    ║   DB_NAME      Nome do database    (padrão: gerenciador)  ║
    ║   DB_PORT      Porta do MySQL      (padrão: 3306)         ║
    ║                                                           ║
    ╠═══════════════════════════════════════════════════════════╣
    ║  💡 EXEMPLOS:                                              ║
    ║  ─────────────────────────────────────────────────────────║
    ║   python migrate.py run                                   ║
    ║   python migrate.py status                                ║
    ║   DB_PASSWORD=senha python migrate.py run                 ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """)


def main() -> None:
    """
    Função principal - ponto de entrada do sistema.
    Processa argumentos da linha de comando e executa ações.
    """
    
    # ──────────────────────────────────────────────────────────────────────────
    # CONFIGURAÇÃO DO BANCO DE DADOS
    # ──────────────────────────────────────────────────────────────────────────
    
    db_config = {
        'host':     os.getenv('DB_HOST', 'localhost'),
        'user':     os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', ''),
        'database': os.getenv('DB_NAME', 'gerenciador_projetos'),
        'port':     int(os.getenv('DB_PORT', 3306))
    }
    
    manager = MigrationManager(db_config)
    
    # ──────────────────────────────────────────────────────────────────────────
    # PROCESSAMENTO DE COMANDOS
    # ──────────────────────────────────────────────────────────────────────────
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        # Dicionário de comandos disponíveis
        commands = {
            'status': lambda: manager.status(),
            'run': lambda: (manager.create_database_if_not_exists(), manager.run_migrations()),
            'help': lambda: print_help(),
            '--help': lambda: print_help(),
            '-h': lambda: print_help(),
        }
        
        if command in commands:
            commands[command]()
        else:
            print(f"\n    ⚠️  Comando desconhecido: '{command}'")
            print("    💡 Use 'python migrate.py help' para ver os comandos disponíveis\n")
    else:
        # Comportamento padrão: mostra header e executa migrations
        print_header()
        manager.create_database_if_not_exists()
        manager.run_migrations()


# ══════════════════════════════════════════════════════════════════════════════
# PONTO DE ENTRADA
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    main()
