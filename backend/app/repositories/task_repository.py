"""
TaskRepository - Repositório para operações de Tarefas
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import date
from .base_repository import BaseRepository

logger = logging.getLogger(__name__)


class TaskRepository(BaseRepository):
    """Repositório para gerenciamento de tarefas"""
    
    def __init__(self):
        super().__init__()
        self.table_name = "tarefas"
        self.primary_key = "id"
    
    def find_by_project(self, project_id: int, status: str = None) -> List[Dict[str, Any]]:
        """Lista tarefas de um projeto"""
        query = """
            SELECT t.*, u.nome as responsavel_nome
            FROM tarefas t
            LEFT JOIN usuarios u ON t.responsavel_id = u.id
            WHERE t.projeto_id = %s
        """
        params = [project_id]
        
        if status:
            query += " AND t.status = %s"
            params.append(status)
        
        query += " ORDER BY t.data_limite ASC, t.prioridade DESC"
        
        try:
            return self.execute_raw(query, tuple(params), fetch=True) or []
        except Exception as e:
            logger.error(f"Error finding tasks by project {project_id}: {str(e)}")
            raise
    
    def find_by_user(self, user_id: int, status: str = None) -> List[Dict[str, Any]]:
        """Lista tarefas atribuídas a um usuário"""
        query = """
            SELECT t.*, p.nome as projeto_nome
            FROM tarefas t
            INNER JOIN projetos p ON t.projeto_id = p.id
            WHERE t.responsavel_id = %s
        """
        params = [user_id]
        
        if status:
            query += " AND t.status = %s"
            params.append(status)
        
        query += " ORDER BY t.data_limite ASC, t.prioridade DESC"
        
        try:
            return self.execute_raw(query, tuple(params), fetch=True) or []
        except Exception as e:
            logger.error(f"Error finding tasks by user {user_id}: {str(e)}")
            raise
    
    def find_overdue(self, user_id: int = None) -> List[Dict[str, Any]]:
        """Lista tarefas atrasadas"""
        query = """
            SELECT t.*, p.nome as projeto_nome, u.nome as responsavel_nome
            FROM tarefas t
            INNER JOIN projetos p ON t.projeto_id = p.id
            LEFT JOIN usuarios u ON t.responsavel_id = u.id
            WHERE t.data_limite < CURDATE() AND t.status != 'concluida'
        """
        params = []
        
        if user_id:
            query += " AND t.responsavel_id = %s"
            params.append(user_id)
        
        query += " ORDER BY t.data_limite ASC"
        
        try:
            return self.execute_raw(query, tuple(params) if params else None, fetch=True) or []
        except Exception as e:
            logger.error(f"Error finding overdue tasks: {str(e)}")
            raise
    
    def find_upcoming(self, user_id: int, days: int = 7) -> List[Dict[str, Any]]:
        """Lista tarefas próximas do prazo"""
        query = """
            SELECT t.*, p.nome as projeto_nome
            FROM tarefas t
            INNER JOIN projetos p ON t.projeto_id = p.id
            WHERE t.responsavel_id = %s 
            AND t.status != 'concluida'
            AND t.data_limite BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL %s DAY)
            ORDER BY t.data_limite ASC
        """
        
        try:
            return self.execute_raw(query, (user_id, days), fetch=True) or []
        except Exception as e:
            logger.error(f"Error finding upcoming tasks: {str(e)}")
            raise
    
    def update_status(self, task_id: int, status: str) -> bool:
        """Atualiza status da tarefa"""
        return self.update(task_id, {'status': status})
    
    def get_kanban_data(self, project_id: int) -> Dict[str, List[Dict[str, Any]]]:
        """Retorna tarefas organizadas para Kanban"""
        query = """
            SELECT t.*, u.nome as responsavel_nome
            FROM tarefas t
            LEFT JOIN usuarios u ON t.responsavel_id = u.id
            WHERE t.projeto_id = %s
            ORDER BY t.ordem ASC, t.prioridade DESC
        """
        
        try:
            tasks = self.execute_raw(query, (project_id,), fetch=True) or []
            
            kanban = {
                'pendente': [],
                'em_andamento': [],
                'em_revisao': [],
                'concluida': []
            }
            
            for task in tasks:
                status = task.get('status', 'pendente')
                if status in kanban:
                    kanban[status].append(task)
                else:
                    kanban['pendente'].append(task)
            
            return kanban
        except Exception as e:
            logger.error(f"Error getting kanban data for project {project_id}: {str(e)}")
            raise
    
    def get_statistics(self, project_id: int = None, user_id: int = None) -> Dict[str, Any]:
        """Retorna estatísticas de tarefas"""
        where_clauses = []
        params = []
        
        if project_id:
            where_clauses.append("projeto_id = %s")
            params.append(project_id)
        
        if user_id:
            where_clauses.append("responsavel_id = %s")
            params.append(user_id)
        
        where = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""
        
        query = f"""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'pendente' THEN 1 ELSE 0 END) as pendentes,
                SUM(CASE WHEN status = 'em_andamento' THEN 1 ELSE 0 END) as em_andamento,
                SUM(CASE WHEN status = 'em_revisao' THEN 1 ELSE 0 END) as em_revisao,
                SUM(CASE WHEN status = 'concluida' THEN 1 ELSE 0 END) as concluidas,
                SUM(CASE WHEN data_limite < CURDATE() AND status != 'concluida' THEN 1 ELSE 0 END) as atrasadas
            FROM tarefas
            {where}
        """
        
        try:
            result = self.execute_raw(query, tuple(params) if params else None, fetch=True)
            return result[0] if result else {}
        except Exception as e:
            logger.error(f"Error getting task statistics: {str(e)}")
            raise
    
    def reorder(self, task_id: int, new_order: int) -> bool:
        """Reordena tarefa no Kanban"""
        return self.update(task_id, {'ordem': new_order})
