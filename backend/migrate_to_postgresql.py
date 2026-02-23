#!/usr/bin/env python3
"""
Script de Migração para PostgreSQL
Migra dados de SQLite para PostgreSQL de forma segura
Mantém backup automático do SQLite original
"""

import os
import sys
import shutil
import sqlite3
import logging
from datetime import datetime

# Importar config
sys.path.insert(0, os.path.dirname(__file__))
from config import settings

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)-8s %(message)s'
)
logger = logging.getLogger(__name__)

class PostgreSQLMigration:
    """Migra dados de SQLite para PostgreSQL"""
    
    def __init__(self):
        self.sqlite_path = settings.SQLITE_PATH
        self.backup_path = f"{self.sqlite_path}.backup-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    
    def requires_postgresql(self):
        """Verifica se PostgreSQL está disponível"""
        try:
            import psycopg2
            return True
        except ImportError:
            logger.error("❌ psycopg2 não instalado!")
            logger.info("💡 Execute: pip install psycopg2-binary")
            return False
    
    def backup_sqlite(self):
        """Cria backup do SQLite"""
        try:
            logger.info(f"📦 Criando backup de {self.sqlite_path}...")
            shutil.copy2(self.sqlite_path, self.backup_path)
            logger.info(f"✅ Backup criado: {self.backup_path}")
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao fazer backup: {e}")
            return False
    
    def migrate_schema(self):
        """Migra o schema (tabelas) para PostgreSQL"""
        try:
            import psycopg2
            
            logger.info("🔄 Migrando schema SQL...")
            
            # Conectar PostgreSQL
            conn = psycopg2.connect(
                host=settings.POSTGRES_HOST,
                user=settings.POSTGRES_USER,
                password=settings.POSTGRES_PASSWORD,
                database=settings.POSTGRES_DB
            )
            cursor = conn.cursor()
            
            # Ler schema do arquivo
            schema_path = os.path.join(
                os.path.dirname(__file__), '..', 'database', 'schema_completo.sql'
            )
            
            if not os.path.exists(schema_path):
                logger.error(f"❌ Schema não encontrado: {schema_path}")
                return False
            
            with open(schema_path, 'r', encoding='utf-8') as f:
                schema_sql = f.read()
            
            # Executar schema
            cursor.execute(schema_sql)
            conn.commit()
            
            logger.info("✅ Schema criado em PostgreSQL")
            cursor.close()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao migrar schema: {e}")
            return False
    
    def migrate_data(self):
        """Migra os dados de SQLite para PostgreSQL"""
        try:
            import psycopg2
            
            logger.info("📊 Migrando dados...")
            
            # Conectar ao SQLite
            sqlite_conn = sqlite3.connect(self.sqlite_path)
            sqlite_conn.row_factory = sqlite3.Row
            sqlite_cursor = sqlite_conn.cursor()
            
            # Conectar ao PostgreSQL
            postgres_conn = psycopg2.connect(
                host=settings.POSTGRES_HOST,
                user=settings.POSTGRES_USER,
                password=settings.POSTGRES_PASSWORD,
                database=settings.POSTGRES_DB
            )
            postgres_cursor = postgres_conn.cursor()
            
            # Tabelas a migrar (ordem importante para FKs)
            tables = [
                'usuarios',
                'permissoes',
                'projetos',
                'usuario_permissoes',
                'equipes',
                'tarefas',
                'tarefa_dependencias',
                'comentarios_tarefa',
                'documentos',
                'versoes_documento',
                'materiais',
                'orcamentos',
                'chats',
                'chat_participantes',
                'mensagens',
                'notificacoes',
                'metricas_projeto',
                'audit_trail'
            ]
            
            for table in tables:
                try:
                    # Pegar dados do SQLite
                    sqlite_cursor.execute(f"SELECT * FROM {table}")
                    rows = sqlite_cursor.fetchall()
                    
                    if not rows:
                        logger.info(f"  ⏭️  {table}: vazio")
                        continue
                    
                    columns = [description[0] for description in sqlite_cursor.description]
                    
                    # Inserir no PostgreSQL
                    placeholders = ','.join(['%s'] * len(columns))
                    insert_sql = f"INSERT INTO {table} ({','.join(columns)}) VALUES ({placeholders})"
                    
                    for row in rows:
                        postgres_cursor.execute(insert_sql, tuple(row))
                    
                    postgres_conn.commit()
                    logger.info(f"  ✅ {table}: {len(rows)} registros")
                    
                except Exception as e:
                    logger.warning(f"  ⚠️  {table}: {e}")
                    postgres_conn.rollback()
            
            sqlite_cursor.close()
            sqlite_conn.close()
            postgres_cursor.close()
            postgres_conn.close()
            
            logger.info("✅ Dados migrados com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao migrar dados: {e}")
            return False
    
    def run(self):
        """Executa a migração completa"""
        logger.info("=" * 60)
        logger.info("🚀 MIGRAÇÃO SQLITE → POSTGRESQL")
        logger.info("=" * 60)
        
        if not self.requires_postgresql():
            return False
        
        if not self.backup_sqlite():
            return False
        
        if not self.migrate_schema():
            return False
        
        if not self.migrate_data():
            logger.warning("⚠️  Dados não foram migrados completamente")
            logger.info("💡 Você pode reverter para o backup:")
            logger.info(f"   cp {self.backup_path} {self.sqlite_path}")
            return False
        
        logger.info("")
        logger.info("=" * 60)
        logger.info("✅ MIGRAÇÃO COMPLETA COM SUCESSO!")
        logger.info("=" * 60)
        logger.info("")
        logger.info("📝 Próximas passos:")
        logger.info("  1. Adicione ao .env: DB_TYPE=postgresql")
        logger.info("  2. Configure as credenciais PostgreSQL no .env")
        logger.info("  3. Reinicie o servidor: python app.py")
        logger.info("")
        logger.info(f"💾 Backup criado em: {self.backup_path}")
        logger.info("")
        return True


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Migrar SQLite para PostgreSQL')
    parser.add_argument('--backup-only', action='store_true', help='Apenas criar backup')
    parser.add_argument('--restore', help='Restaurar de um backup', metavar='PATH')
    
    args = parser.parse_args()
    
    if args.restore:
        logger.info(f"📦 Restaurando do backup: {args.restore}")
        if os.path.exists(args.restore):
            shutil.copy2(args.restore, settings.SQLITE_PATH)
            logger.info(f"✅ Restaurado para: {settings.SQLITE_PATH}")
        else:
            logger.error(f"❌ Arquivo não encontrado: {args.restore}")
    elif args.backup_only:
        migration = PostgreSQLMigration()
        migration.backup_sqlite()
    else:
        migration = PostgreSQLMigration()
        success = migration.run()
        sys.exit(0 if success else 1)
