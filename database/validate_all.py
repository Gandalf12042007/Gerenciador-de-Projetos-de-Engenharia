#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de Validação Completa - Banco de Dados
Testa todas as funcionalidades: conexão, migrations, seeds, queries, triggers e performance
"""

import os
import sys
import time
from datetime import datetime
import mysql.connector
from mysql.connector import Error

class DatabaseValidator:
    """Validador completo do banco de dados"""
    
    def __init__(self):
        """Inicializa o validador"""
        self.config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'user': os.getenv('DB_USER', 'root'),
            'password': os.getenv('DB_PASSWORD', ''),
            'database': os.getenv('DB_NAME', 'gerenciador_projetos'),
            'port': int(os.getenv('DB_PORT', 3306))
        }
        self.connection = None
        self.tests_passed = 0
        self.tests_failed = 0
        self.warnings = 0
    
    def print_header(self, title):
        """Imprime cabeçalho de seção"""
        print("\n" + "="*70)
        print(f"  {title}")
        print("="*70)
    
    def print_test(self, name, status, message=""):
        """Imprime resultado de um teste"""
        symbols = {"PASS": "✓", "FAIL": "✗", "WARN": "⚠️"}
        colors = {"PASS": "", "FAIL": "", "WARN": ""}  # Poderia adicionar cores ANSI
        
        symbol = symbols.get(status, "?")
        print(f"  {symbol} {name:50} [{status}]")
        
        if message:
            print(f"     └─ {message}")
        
        if status == "PASS":
            self.tests_passed += 1
        elif status == "FAIL":
            self.tests_failed += 1
        elif status == "WARN":
            self.warnings += 1
    
    def connect(self):
        """Testa conexão com o banco"""
        try:
            self.connection = mysql.connector.connect(**self.config)
            if self.connection.is_connected():
                return True
        except Error as e:
            print(f"Erro: {e}")
            return False
        return False
    
    def disconnect(self):
        """Desconecta do banco"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
    
    def test_connection(self):
        """Teste 1: Conectividade"""
        self.print_header("TESTE 1: CONECTIVIDADE")
        
        # Teste de conexão
        if self.connect():
            db_info = self.connection.get_server_info()
            self.print_test("Conexão com MySQL", "PASS", f"MySQL {db_info}")
        else:
            self.print_test("Conexão com MySQL", "FAIL", "Não foi possível conectar")
            return False
        
        # Teste de banco de dados
        cursor = self.connection.cursor()
        try:
            cursor.execute("SELECT DATABASE()")
            db_name = cursor.fetchone()[0]
            self.print_test("Banco de dados selecionado", "PASS", f"Database: {db_name}")
        except Error as e:
            self.print_test("Banco de dados selecionado", "FAIL", str(e))
        finally:
            cursor.close()
        
        return True
    
    def test_tables(self):
        """Teste 2: Estrutura de Tabelas"""
        self.print_header("TESTE 2: ESTRUTURA DE TABELAS")
        
        expected_tables = [
            'usuarios', 'permissoes', 'usuario_permissoes',
            'projetos', 'equipes', 'tarefas', 'tarefa_dependencias',
            'comentarios_tarefa', 'documentos', 'versoes_documento',
            'chats', 'chat_participantes', 'mensagens',
            'materiais', 'orcamentos', 'metricas_projeto', 'notificacoes',
            '_migrations'
        ]
        
        cursor = self.connection.cursor()
        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]
        cursor.close()
        
        for table in expected_tables:
            if table in tables:
                self.print_test(f"Tabela: {table}", "PASS")
            else:
                self.print_test(f"Tabela: {table}", "FAIL", "Tabela não encontrada")
        
        # Tabelas extras
        extra_tables = set(tables) - set(expected_tables)
        if extra_tables:
            self.print_test("Tabelas extras", "WARN", f"Encontradas: {', '.join(extra_tables)}")
        
        return len(expected_tables) == len([t for t in expected_tables if t in tables])
    
    def test_migrations(self):
        """Teste 3: Migrations Executadas"""
        self.print_header("TESTE 3: MIGRATIONS EXECUTADAS")
        
        cursor = self.connection.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM _migrations ORDER BY versao")
            migrations = cursor.fetchall()
            
            if migrations:
                for mig in migrations:
                    self.print_test(
                        f"Migration {mig['versao']}: {mig['nome']}", 
                        "PASS",
                        f"Executada em {mig['executado_em']}"
                    )
            else:
                self.print_test("Migrations", "WARN", "Nenhuma migration executada")
        except Error as e:
            self.print_test("Verificação de migrations", "FAIL", str(e))
        finally:
            cursor.close()
    
    def test_data(self):
        """Teste 4: Dados Populados"""
        self.print_header("TESTE 4: DADOS POPULADOS (SEEDS)")
        
        tables_to_check = {
            'usuarios': 'Usuários',
            'permissoes': 'Permissões',
            'projetos': 'Projetos',
            'equipes': 'Membros de Equipe',
            'tarefas': 'Tarefas',
            'materiais': 'Materiais',
            'orcamentos': 'Orçamentos',
            'documentos': 'Documentos',
            'chats': 'Chats',
            'mensagens': 'Mensagens',
            'metricas_projeto': 'Métricas'
        }
        
        cursor = self.connection.cursor()
        
        for table, label in tables_to_check.items():
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                
                if count > 0:
                    self.print_test(label, "PASS", f"{count} registro(s)")
                else:
                    self.print_test(label, "WARN", "Sem dados (rode o seed.py)")
            except Error as e:
                self.print_test(label, "FAIL", str(e))
        
        cursor.close()
    
    def test_relationships(self):
        """Teste 5: Relacionamentos e Foreign Keys"""
        self.print_header("TESTE 5: RELACIONAMENTOS (FOREIGN KEYS)")
        
        cursor = self.connection.cursor(dictionary=True)
        
        try:
            cursor.execute("""
                SELECT 
                    TABLE_NAME,
                    CONSTRAINT_NAME,
                    REFERENCED_TABLE_NAME
                FROM information_schema.KEY_COLUMN_USAGE
                WHERE TABLE_SCHEMA = %s
                    AND REFERENCED_TABLE_NAME IS NOT NULL
                ORDER BY TABLE_NAME
            """, (self.config['database'],))
            
            fks = cursor.fetchall()
            
            if fks:
                # Agrupar por tabela
                fk_by_table = {}
                for fk in fks:
                    table = fk['TABLE_NAME']
                    if table not in fk_by_table:
                        fk_by_table[table] = []
                    fk_by_table[table].append(fk['REFERENCED_TABLE_NAME'])
                
                for table, refs in fk_by_table.items():
                    self.print_test(
                        f"FK em {table}", 
                        "PASS",
                        f"Referencia: {', '.join(set(refs))}"
                    )
            else:
                self.print_test("Foreign Keys", "WARN", "Nenhuma FK encontrada")
                
        except Error as e:
            self.print_test("Verificação de FKs", "FAIL", str(e))
        finally:
            cursor.close()
    
    def test_indexes(self):
        """Teste 6: Índices"""
        self.print_header("TESTE 6: ÍNDICES DE PERFORMANCE")
        
        cursor = self.connection.cursor(dictionary=True)
        
        try:
            cursor.execute("""
                SELECT 
                    TABLE_NAME,
                    COUNT(DISTINCT INDEX_NAME) as num_indices
                FROM information_schema.STATISTICS
                WHERE TABLE_SCHEMA = %s
                    AND TABLE_NAME != '_migrations'
                GROUP BY TABLE_NAME
                ORDER BY num_indices DESC
            """, (self.config['database'],))
            
            tables_with_indexes = cursor.fetchall()
            
            for table in tables_with_indexes:
                num = table['num_indices']
                status = "PASS" if num >= 2 else "WARN"
                self.print_test(
                    f"Índices em {table['TABLE_NAME']}", 
                    status,
                    f"{num} índice(s)"
                )
                
        except Error as e:
            self.print_test("Verificação de índices", "FAIL", str(e))
        finally:
            cursor.close()
    
    def test_triggers(self):
        """Teste 7: Triggers"""
        self.print_header("TESTE 7: TRIGGERS AUTOMÁTICOS")
        
        cursor = self.connection.cursor(dictionary=True)
        
        try:
            cursor.execute("""
                SELECT 
                    TRIGGER_NAME,
                    EVENT_MANIPULATION,
                    EVENT_OBJECT_TABLE,
                    ACTION_TIMING
                FROM information_schema.TRIGGERS
                WHERE TRIGGER_SCHEMA = %s
                ORDER BY EVENT_OBJECT_TABLE, ACTION_TIMING
            """, (self.config['database'],))
            
            triggers = cursor.fetchall()
            
            if triggers:
                for trigger in triggers:
                    self.print_test(
                        f"Trigger: {trigger['TRIGGER_NAME']}", 
                        "PASS",
                        f"{trigger['ACTION_TIMING']} {trigger['EVENT_MANIPULATION']} on {trigger['EVENT_OBJECT_TABLE']}"
                    )
            else:
                self.print_test("Triggers", "WARN", "Nenhum trigger encontrado (execute migration 002)")
                
        except Error as e:
            self.print_test("Verificação de triggers", "FAIL", str(e))
        finally:
            cursor.close()
    
    def test_views(self):
        """Teste 8: Views"""
        self.print_header("TESTE 8: VIEWS E CONSULTAS")
        
        views_to_test = [
            'vw_projetos_completo',
            'vw_tarefas_usuario',
            'vw_orcamento_projeto',
            'vw_chats_resumo'
        ]
        
        cursor = self.connection.cursor()
        
        for view in views_to_test:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {view}")
                count = cursor.fetchone()[0]
                self.print_test(f"View: {view}", "PASS", f"{count} registro(s)")
            except Error as e:
                self.print_test(f"View: {view}", "WARN", f"Não existe (execute queries_uteis.sql)")
        
        cursor.close()
    
    def test_procedures(self):
        """Teste 9: Stored Procedures"""
        self.print_header("TESTE 9: STORED PROCEDURES")
        
        cursor = self.connection.cursor(dictionary=True)
        
        try:
            cursor.execute("""
                SELECT 
                    ROUTINE_NAME,
                    ROUTINE_TYPE
                FROM information_schema.ROUTINES
                WHERE ROUTINE_SCHEMA = %s
                ORDER BY ROUTINE_TYPE, ROUTINE_NAME
            """, (self.config['database'],))
            
            routines = cursor.fetchall()
            
            if routines:
                for routine in routines:
                    self.print_test(
                        f"{routine['ROUTINE_TYPE']}: {routine['ROUTINE_NAME']}", 
                        "PASS"
                    )
            else:
                self.print_test("Procedures/Functions", "WARN", "Nenhuma encontrada (execute queries_uteis.sql)")
                
        except Error as e:
            self.print_test("Verificação de procedures", "FAIL", str(e))
        finally:
            cursor.close()
    
    def test_performance(self):
        """Teste 10: Performance de Queries"""
        self.print_header("TESTE 10: PERFORMANCE DE QUERIES")
        
        queries = [
            ("SELECT COUNT(*) FROM projetos", "Contar projetos"),
            ("SELECT * FROM vw_projetos_completo LIMIT 10", "View de projetos"),
            ("SELECT * FROM tarefas WHERE projeto_id = 1", "Tarefas por projeto"),
            ("SELECT * FROM mensagens WHERE chat_id = 1 ORDER BY criado_em DESC LIMIT 20", "Mensagens do chat"),
        ]
        
        cursor = self.connection.cursor()
        
        for query, description in queries:
            try:
                start_time = time.time()
                cursor.execute(query)
                cursor.fetchall()
                elapsed = (time.time() - start_time) * 1000  # ms
                
                status = "PASS" if elapsed < 100 else "WARN"
                self.print_test(description, status, f"{elapsed:.2f}ms")
            except Error as e:
                self.print_test(description, "FAIL", str(e))
        
        cursor.close()
    
    def test_data_integrity(self):
        """Teste 11: Integridade de Dados"""
        self.print_header("TESTE 11: INTEGRIDADE DE DADOS")
        
        cursor = self.connection.cursor()
        
        # Teste 1: Projetos sem tarefas órfãs
        try:
            cursor.execute("""
                SELECT COUNT(*) FROM tarefas t
                LEFT JOIN projetos p ON t.projeto_id = p.id
                WHERE p.id IS NULL
            """)
            orphans = cursor.fetchone()[0]
            
            if orphans == 0:
                self.print_test("Tarefas órfãs", "PASS", "Nenhuma tarefa sem projeto")
            else:
                self.print_test("Tarefas órfãs", "FAIL", f"{orphans} tarefa(s) sem projeto válido")
        except Error as e:
            self.print_test("Tarefas órfãs", "FAIL", str(e))
        
        # Teste 2: Usuários sem email duplicado
        try:
            cursor.execute("""
                SELECT email, COUNT(*) as count
                FROM usuarios
                GROUP BY email
                HAVING count > 1
            """)
            duplicates = cursor.fetchall()
            
            if not duplicates:
                self.print_test("Emails únicos", "PASS", "Sem duplicatas")
            else:
                self.print_test("Emails únicos", "FAIL", f"{len(duplicates)} email(s) duplicado(s)")
        except Error as e:
            self.print_test("Emails únicos", "FAIL", str(e))
        
        # Teste 3: Progresso entre 0 e 100
        try:
            cursor.execute("""
                SELECT COUNT(*) FROM projetos
                WHERE progresso_percentual < 0 OR progresso_percentual > 100
            """)
            invalid = cursor.fetchone()[0]
            
            if invalid == 0:
                self.print_test("Progresso válido", "PASS", "Todos entre 0-100%")
            else:
                self.print_test("Progresso válido", "FAIL", f"{invalid} projeto(s) com progresso inválido")
        except Error as e:
            self.print_test("Progresso válido", "FAIL", str(e))
        
        cursor.close()
    
    def run_all_tests(self):
        """Executa todos os testes"""
        print("\n" + "="*70)
        print("  VALIDAÇÃO COMPLETA DO BANCO DE DADOS")
        print("  Gerenciador de Projetos de Engenharia")
        print("="*70)
        print(f"\n  Database: {self.config['database']}")
        print(f"  Host: {self.config['host']}:{self.config['port']}")
        print(f"  Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Executar testes
        if not self.test_connection():
            print("\n❌ Falha na conexão. Verifique as configurações e tente novamente.")
            return False
        
        self.test_tables()
        self.test_migrations()
        self.test_data()
        self.test_relationships()
        self.test_indexes()
        self.test_triggers()
        self.test_views()
        self.test_procedures()
        self.test_performance()
        self.test_data_integrity()
        
        # Resumo final
        self.print_header("RESUMO DOS TESTES")
        
        total = self.tests_passed + self.tests_failed + self.warnings
        
        print(f"\n  ✓ Testes aprovados:  {self.tests_passed}/{total}")
        print(f"  ✗ Testes falhados:   {self.tests_failed}/{total}")
        print(f"  ⚠️  Avisos:            {self.warnings}/{total}")
        
        if self.tests_failed == 0:
            print("\n  🎉 TODOS OS TESTES CRÍTICOS PASSARAM!")
            if self.warnings > 0:
                print(f"  💡 Há {self.warnings} aviso(s) - verifique as recomendações acima.")
        else:
            print(f"\n  ❌ {self.tests_failed} teste(s) falharam. Corrija os erros acima.")
        
        print("\n" + "="*70 + "\n")
        
        return self.tests_failed == 0


def main():
    """Função principal"""
    validator = DatabaseValidator()
    
    try:
        success = validator.run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Validação interrompida pelo usuário.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Erro inesperado: {e}")
        sys.exit(1)
    finally:
        validator.disconnect()


if __name__ == '__main__':
    main()
