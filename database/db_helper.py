"""
Database Helper - Gerenciador de Projetos
Classe auxiliar para conexão e operações com o banco de dados
"""

import os
from typing import List, Dict, Any, Optional
import mysql.connector
from mysql.connector import Error, pooling
from contextlib import contextmanager
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseHelper:
    """Helper para operações no banco de dados"""
    
    def __init__(self, pool_name="gerenciador_pool", pool_size=5):
        """
        Inicializa o helper com connection pool
        
        Args:
            pool_name: Nome do pool de conexões
            pool_size: Tamanho do pool (padrão: 5)
        """
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
            logger.info(f"✓ Connection pool criado: {pool_name} (size: {pool_size})")
        except Error as e:
            logger.error(f"✗ Erro ao criar connection pool: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """
        Context manager para obter conexão do pool
        
        Uso:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM usuarios")
        """
        conn = None
        try:
            conn = self.pool.get_connection()
            yield conn
        except Error as e:
            logger.error(f"Erro na conexão: {e}")
            raise
        finally:
            if conn and conn.is_connected():
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
                    
            except Error as e:
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
            except Error as e:
                conn.rollback()
                logger.error(f"Erro ao executar batch: {e}")
                raise
            finally:
                cursor.close()
    
    # ===== MÉTODOS DE USUÁRIOS =====
    
    def get_usuario_by_email(self, email: str) -> Optional[Dict]:
        """Busca usuário por email"""
        query = "SELECT * FROM usuarios WHERE email = %s AND ativo = TRUE"
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
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(query, (
                    nome, email, senha_hash,
                    kwargs.get('telefone'),
                    kwargs.get('cargo'),
                    kwargs.get('ativo', True)
                ))
                conn.commit()
                return cursor.lastrowid
            except Error as e:
                conn.rollback()
                logger.error(f"Erro ao criar usuário: {e}")
                raise
            finally:
                cursor.close()
    
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
            LEFT JOIN equipes e ON p.id = e.projeto_id AND e.ativo = TRUE
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
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(query, (chat_id, usuario_id, mensagem, arquivo_url))
                conn.commit()
                return cursor.lastrowid
            except Error as e:
                conn.rollback()
                logger.error(f"Erro ao criar mensagem: {e}")
                raise
            finally:
                cursor.close()
    
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
                logger.info("✓ Conexão com banco OK")
                return True
        except Error as e:
            logger.error(f"✗ Erro na conexão: {e}")
            return False
    
    def close_pool(self):
        """Fecha o connection pool (chamar ao encerrar aplicação)"""
        try:
            # MySQL Connector Python não tem método direto para fechar pool
            # As conexões são fechadas automaticamente
            logger.info("✓ Connection pool fechado")
        except Exception as e:
            logger.error(f"Erro ao fechar pool: {e}")


# ===== FUNÇÕES DE CONVENIÊNCIA =====

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
    if not hasattr(get_db, '_instance'):
        get_db._instance = DatabaseHelper()
    return get_db._instance


if __name__ == '__main__':
    # Teste básico
    print("\n" + "="*60)
    print("TESTANDO DATABASE HELPER")
    print("="*60 + "\n")
    
    try:
        db = DatabaseHelper()
        
        # Teste de conexão
        if db.test_connection():
            print("✓ Helper funcionando corretamente!")
            
            # Teste de query
            usuarios = db.execute_query("SELECT COUNT(*) as total FROM usuarios", fetch=True)
            if usuarios:
                print(f"✓ Total de usuários no banco: {usuarios[0]['total']}")
        
    except Exception as e:
        print(f"✗ Erro: {e}")
