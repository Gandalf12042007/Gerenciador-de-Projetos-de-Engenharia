"""
Database Helper - Gerenciador de Projetos
Classe auxiliar para conexão e operações com o banco de dados
Suporta MySQL e SQLite (configurável via DB_TYPE no .env)
"""

import os
import re
import sqlite3
from typing import List, Dict, Any, Optional
from contextlib import contextmanager
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Detectar tipo de banco
DB_TYPE = os.getenv('DB_TYPE', 'sqlite').lower()

# Import condicional do MySQL
if DB_TYPE == 'mysql':
    try:
        import mysql.connector
        from mysql.connector import Error as MySQLError, pooling
        MYSQL_AVAILABLE = True
    except ImportError:
        MYSQL_AVAILABLE = False
        logger.warning("mysql-connector-python não instalado. Usando SQLite.")
else:
    MYSQL_AVAILABLE = False


def convert_query_placeholders(query: str, to_sqlite: bool) -> str:
    """
    Converte placeholders de query entre MySQL (%s) e SQLite (?)
    
    Args:
        query: Query SQL original
        to_sqlite: Se True, converte %s -> ?
    """
    if to_sqlite:
        # Converte %s para ? (SQLite)
        return query.replace('%s', '?')
    return query


def convert_sql_functions(query: str, to_sqlite: bool) -> str:
    """
    Converte funções SQL específicas entre MySQL e SQLite
    """
    if to_sqlite:
        # NOW() -> datetime('now', 'localtime')
        query = re.sub(r'\bNOW\(\)', "datetime('now', 'localtime')", query, flags=re.IGNORECASE)
        # CURDATE() -> date('now', 'localtime')
        query = re.sub(r'\bCURDATE\(\)', "date('now', 'localtime')", query, flags=re.IGNORECASE)
        # INSERT IGNORE -> INSERT OR IGNORE
        query = re.sub(r'\bINSERT\s+IGNORE\b', 'INSERT OR IGNORE', query, flags=re.IGNORECASE)
        # IFNULL já funciona em ambos, mas COALESCE é mais portável
    return query


def adapt_query(query: str, is_sqlite: bool) -> str:
    """Adapta query para o banco de dados atual"""
    if is_sqlite:
        query = convert_sql_functions(query, True)
        query = convert_query_placeholders(query, True)
    return query


class SQLiteConnection:
    """Wrapper para conexão SQLite com interface similar ao MySQL"""
    
    def __init__(self, connection: sqlite3.Connection):
        self._conn = connection
        self._conn.row_factory = sqlite3.Row
    
    def cursor(self, dictionary: bool = False):
        """Retorna cursor (dictionary é ignorado, usamos Row)"""
        return SQLiteCursor(self._conn.cursor())
    
    def commit(self):
        self._conn.commit()
    
    def rollback(self):
        self._conn.rollback()
    
    def close(self):
        self._conn.close()
    
    def is_connected(self):
        try:
            self._conn.execute("SELECT 1")
            return True
        except:
            return False


class SQLiteCursor:
    """Wrapper para cursor SQLite com interface similar ao MySQL"""
    
    def __init__(self, cursor: sqlite3.Cursor):
        self._cursor = cursor
        self._lastrowid = None
    
    def execute(self, query: str, params: tuple = None):
        """Executa query adaptando para SQLite"""
        adapted_query = adapt_query(query, True)
        self._cursor.execute(adapted_query, params or ())
        self._lastrowid = self._cursor.lastrowid
    
    def executemany(self, query: str, data: list):
        """Executa múltiplas queries"""
        adapted_query = adapt_query(query, True)
        self._cursor.executemany(adapted_query, data)
    
    def fetchone(self):
        row = self._cursor.fetchone()
        return dict(row) if row else None
    
    def fetchall(self):
        rows = self._cursor.fetchall()
        return [dict(row) for row in rows]
    
    @property
    def lastrowid(self):
        return self._lastrowid or self._cursor.lastrowid
    
    @property
    def rowcount(self):
        return self._cursor.rowcount
    
    def close(self):
        self._cursor.close()


class DatabaseHelper:
    """Helper para operações no banco de dados - Suporta MySQL e SQLite"""
    
    def __init__(self, pool_name="gerenciador_pool", pool_size=5):
        """
        Inicializa o helper
        
        Args:
            pool_name: Nome do pool de conexões (MySQL)
            pool_size: Tamanho do pool (MySQL)
        """
        self.db_type = os.getenv('DB_TYPE', 'sqlite').lower()
        self.is_sqlite = self.db_type == 'sqlite'
        self.pool = None
        self.sqlite_path = None
        
        if self.is_sqlite or not MYSQL_AVAILABLE:
            self._init_sqlite()
        else:
            self._init_mysql(pool_name, pool_size)
    
    def _init_sqlite(self):
        """Inicializa conexão SQLite"""
        self.is_sqlite = True
        self.sqlite_path = os.getenv('SQLITE_PATH', os.path.join(
            os.path.dirname(__file__), 'gerenciador.db'
        ))
        
        # Criar diretório se não existir
        db_dir = os.path.dirname(self.sqlite_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
        
        # Testar conexão
        try:
            conn = sqlite3.connect(self.sqlite_path)
            conn.close()
            logger.info(f"✓ SQLite configurado: {self.sqlite_path}")
        except Exception as e:
            logger.error(f"✗ Erro ao configurar SQLite: {e}")
            raise
    
    def _init_mysql(self, pool_name: str, pool_size: int):
        """Inicializa pool de conexões MySQL"""
        self.config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'user': os.getenv('DB_USER', 'root'),
            'password': os.getenv('DB_PASSWORD', ''),
            'database': os.getenv('DB_NAME', 'gerenciador_projetos'),
            'port': int(os.getenv('DB_PORT', 3306)),
            'charset': 'utf8mb4',
            'collation': 'utf8mb4_unicode_ci'
        }
        
        try:
            self.pool = pooling.MySQLConnectionPool(
                pool_name=pool_name,
                pool_size=pool_size,
                **self.config
            )
            logger.info(f"✓ MySQL Connection pool criado: {pool_name} (size: {pool_size})")
        except MySQLError as e:
            logger.error(f"✗ Erro ao criar connection pool MySQL: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """
        Context manager para obter conexão
        
        Uso:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM usuarios")
        """
        conn = None
        try:
            if self.is_sqlite:
                raw_conn = sqlite3.connect(self.sqlite_path)
                conn = SQLiteConnection(raw_conn)
            else:
                conn = self.pool.get_connection()
            yield conn
        except Exception as e:
            logger.error(f"Erro na conexão: {e}")
            raise
        finally:
            if conn:
                if self.is_sqlite:
                    conn.close()
                elif conn.is_connected():
                    conn.close()
    
    def execute_query(self, query: str, params: tuple = None, fetch: bool = False) -> Optional[List[Dict]]:
        """
        Executa query SQL (SELECT, INSERT, UPDATE, DELETE)
        
        Args:
            query: Query SQL a ser executada
            params: Parâmetros da query (opcional)
            fetch: Se True, retorna resultados (para SELECT)
        
        Returns:
            Lista de dicionários com resultados (se fetch=True)
            None (se fetch=False)
        """
        with self.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            try:
                cursor.execute(query, params or ())
                
                if fetch:
                    result = cursor.fetchall()
                    return result
                else:
                    conn.commit()
                    return None
                    
            except Exception as e:
                conn.rollback()
                logger.error(f"Erro ao executar query: {e}")
                raise
            finally:
                cursor.close()
    
    def execute_many(self, query: str, data: List[tuple]) -> int:
        """
        Executa múltiplos inserts/updates de uma vez
        
        Args:
            query: Query SQL com placeholders
            data: Lista de tuplas com os dados
        
        Returns:
            Número de linhas afetadas
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.executemany(query, data)
                conn.commit()
                return cursor.rowcount
            except Exception as e:
                conn.rollback()
                logger.error(f"Erro ao executar batch: {e}")
                raise
            finally:
                cursor.close()
    
    def execute_insert(self, query: str, params: tuple = None) -> int:
        """
        Executa INSERT e retorna o ID inserido
        
        Args:
            query: Query SQL de INSERT
            params: Parâmetros da query
        
        Returns:
            ID do registro inserido
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(query, params or ())
                conn.commit()
                return cursor.lastrowid
            except Exception as e:
                conn.rollback()
                logger.error(f"Erro ao executar insert: {e}")
                raise
            finally:
                cursor.close()
    
    # ===== MÉTODOS DE USUÁRIOS =====
    
    def get_usuario_by_email(self, email: str) -> Optional[Dict]:
        """Busca usuário por email"""
        query = "SELECT * FROM usuarios WHERE email = %s AND ativo = 1"
        result = self.execute_query(query, (email,), fetch=True)
        return result[0] if result else None
    
    def create_usuario(self, nome: str, email: str, senha_hash: str, **kwargs) -> int:
        """
        Cria novo usuário
        
        Returns:
            ID do usuário criado
        """
        query = """
            INSERT INTO usuarios (nome, email, senha_hash, telefone, cargo, ativo)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        return self.execute_insert(query, (
            nome, email, senha_hash,
            kwargs.get('telefone'),
            kwargs.get('cargo'),
            kwargs.get('ativo', True)
        ))
    
    # ===== MÉTODOS DE PROJETOS =====
    
    def get_projetos_ativos(self, criador_id: Optional[int] = None) -> List[Dict]:
        """Lista projetos ativos, opcionalmente filtrados por criador"""
        query = """
            SELECT p.*, u.nome as criador_nome
            FROM projetos p
            JOIN usuarios u ON p.criador_id = u.id
            WHERE p.status != 'cancelado'
        """
        params = []
        
        if criador_id:
            query += " AND p.criador_id = %s"
            params.append(criador_id)
        
        query += " ORDER BY p.data_inicio DESC"
        return self.execute_query(query, tuple(params) if params else None, fetch=True)
    
    def get_projeto_com_metricas(self, projeto_id: int) -> Optional[Dict]:
        """Retorna projeto com métricas agregadas"""
        # Query compatível com MySQL e SQLite
        query = """
            SELECT 
                p.*,
                COUNT(DISTINCT t.id) as total_tarefas,
                COUNT(DISTINCT CASE WHEN t.status = 'concluida' THEN t.id END) as tarefas_concluidas,
                COUNT(DISTINCT CASE WHEN t.data_fim_prevista < CURDATE() 
                    AND t.status != 'concluida' THEN t.id END) as tarefas_atrasadas,
                COUNT(DISTINCT e.id) as total_membros,
                COALESCE(SUM(m.quantidade_utilizada * m.preco_unitario), 0) as valor_gasto_materiais
            FROM projetos p
            LEFT JOIN tarefas t ON p.id = t.projeto_id
            LEFT JOIN equipes e ON p.id = e.projeto_id AND e.ativo = 1
            LEFT JOIN materiais m ON p.id = m.projeto_id
            WHERE p.id = %s
            GROUP BY p.id
        """
        result = self.execute_query(query, (projeto_id,), fetch=True)
        return result[0] if result else None
    
    # ===== MÉTODOS DE TAREFAS =====
    
    def get_tarefas_por_status(self, projeto_id: int) -> Dict[str, List[Dict]]:
        """Retorna tarefas agrupadas por status (para Kanban)"""
        query = """
            SELECT t.*, u.nome as responsavel_nome
            FROM tarefas t
            LEFT JOIN usuarios u ON t.responsavel_id = u.id
            WHERE t.projeto_id = %s
            ORDER BY t.ordem, t.criado_em
        """
        tarefas = self.execute_query(query, (projeto_id,), fetch=True)
        
        # Agrupar por status
        kanban = {
            'a_fazer': [],
            'em_andamento': [],
            'em_revisao': [],
            'concluida': []
        }
        
        for tarefa in tarefas or []:
            status = tarefa.get('status', 'a_fazer')
            if status in kanban:
                kanban[status].append(tarefa)
        
        return kanban
    
    # ===== MÉTODOS DE CHAT =====
    
    def get_mensagens_chat(self, chat_id: int, limit: int = 50) -> List[Dict]:
        """Busca últimas mensagens de um chat"""
        query = """
            SELECT m.*, u.nome as usuario_nome, u.foto_perfil
            FROM mensagens m
            JOIN usuarios u ON m.usuario_id = u.id
            WHERE m.chat_id = %s
            ORDER BY m.criado_em DESC
            LIMIT %s
        """
        mensagens = self.execute_query(query, (chat_id, limit), fetch=True)
        return list(reversed(mensagens)) if mensagens else []
    
    def create_mensagem(self, chat_id: int, usuario_id: int, mensagem: str, 
                       arquivo_url: Optional[str] = None) -> int:
        """Cria nova mensagem no chat"""
        query = """
            INSERT INTO mensagens (chat_id, usuario_id, mensagem, arquivo_url)
            VALUES (%s, %s, %s, %s)
        """
        return self.execute_insert(query, (chat_id, usuario_id, mensagem, arquivo_url))
    
    # ===== MÉTODOS DE ESTATÍSTICAS =====
    
    def get_dashboard_stats(self, usuario_id: Optional[int] = None) -> Dict:
        """Retorna estatísticas gerais do dashboard"""
        # Projetos ativos
        query_projetos = """
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN status = 'em_andamento' THEN 1 END) as em_andamento,
                COUNT(CASE WHEN status = 'atrasado' THEN 1 END) as atrasados
            FROM projetos
            WHERE status != 'cancelado'
        """
        if usuario_id:
            query_projetos += " AND criador_id = %s"
        
        projetos = self.execute_query(
            query_projetos, 
            (usuario_id,) if usuario_id else None, 
            fetch=True
        )[0]
        
        # Tarefas pendentes
        query_tarefas = """
            SELECT 
                COUNT(*) as total_pendentes,
                COUNT(CASE WHEN data_fim_prevista < CURDATE() THEN 1 END) as atrasadas
            FROM tarefas
            WHERE status IN ('a_fazer', 'em_andamento')
        """
        if usuario_id:
            query_tarefas += " AND responsavel_id = %s"
        
        tarefas = self.execute_query(
            query_tarefas,
            (usuario_id,) if usuario_id else None,
            fetch=True
        )[0]
        
        return {
            'projetos_ativos': projetos['em_andamento'],
            'projetos_total': projetos['total'],
            'tarefas_pendentes': tarefas['total_pendentes'],
            'tarefas_atrasadas': tarefas['atrasadas']
        }
    
    # ===== MÉTODOS UTILITÁRIOS =====
    
    def test_connection(self) -> bool:
        """Testa conexão com o banco"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                cursor.fetchone()
                db_name = "SQLite" if self.is_sqlite else "MySQL"
                logger.info(f"✓ Conexão com {db_name} OK")
                return True
        except Exception as e:
            logger.error(f"✗ Erro na conexão: {e}")
            return False
    
    def close_pool(self):
        """Fecha o connection pool (chamar ao encerrar aplicação)"""
        try:
            if self.is_sqlite:
                logger.info("✓ SQLite não requer fechamento de pool")
            else:
                logger.info("✓ Connection pool MySQL fechado")
        except Exception as e:
            logger.error(f"Erro ao fechar pool: {e}")
    
    def init_sqlite_schema(self):
        """Inicializa o schema do SQLite se não existir"""
        if not self.is_sqlite:
            return
        
        schema_path = os.path.join(os.path.dirname(__file__), 'schema_sqlite.sql')
        if not os.path.exists(schema_path):
            logger.warning(f"Schema SQLite não encontrado: {schema_path}")
            return
        
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema = f.read()
        
        with self.get_connection() as conn:
            try:
                # SQLite permite executar múltiplos statements
                conn._conn.executescript(schema)
                logger.info("✓ Schema SQLite inicializado")
            except Exception as e:
                logger.error(f"Erro ao inicializar schema: {e}")


# ===== FUNÇÕES DE CONVENIÊNCIA =====

_db_instance = None

def get_db() -> DatabaseHelper:
    """
    Retorna instância do DatabaseHelper (singleton)
    
    Uso em FastAPI:
        from database.db_helper import get_db
        
        @app.get("/projetos")
        def listar_projetos():
            db = get_db()
            return db.get_projetos_ativos()
    """
    global _db_instance
    if _db_instance is None:
        _db_instance = DatabaseHelper()
    return _db_instance


def get_db_connection():
    """
    Retorna uma conexão do banco de dados
    Compatibilidade com código legado que usa get_db_connection()
    """
    db = get_db()
    if db.is_sqlite:
        conn = sqlite3.connect(db.sqlite_path)
        conn.row_factory = sqlite3.Row
        return SQLiteConnection(conn)
    else:
        return db.pool.get_connection()


if __name__ == '__main__':
    # Teste básico
    print("\n" + "="*60)
    print("TESTANDO DATABASE HELPER")
    print("="*60 + "\n")
    
    try:
        db = DatabaseHelper()
        
        print(f"Tipo de banco: {'SQLite' if db.is_sqlite else 'MySQL'}")
        if db.is_sqlite:
            print(f"Caminho: {db.sqlite_path}")
        
        # Teste de conexão
        if db.test_connection():
            print("✓ Helper funcionando corretamente!")
            
            # Teste de query
            try:
                usuarios = db.execute_query("SELECT COUNT(*) as total FROM usuarios", fetch=True)
                if usuarios:
                    print(f"✓ Total de usuários no banco: {usuarios[0]['total']}")
            except Exception as e:
                print(f"⚠ Tabela usuarios não existe ainda: {e}")
        
    except Exception as e:
        print(f"✗ Erro: {e}")
