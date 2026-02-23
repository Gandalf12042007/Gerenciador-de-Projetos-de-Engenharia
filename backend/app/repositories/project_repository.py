"""
ProjectRepository - Repositório para operações de Projetos
"""

import logging
from typing import List, Dict, Any, Optional
from .base_repository import BaseRepository

logger = logging.getLogger(__name__)


class ProjectRepository(BaseRepository):
    """Repositório para gerenciamento de projetos"""
    
    def __init__(self):
        super().__init__()
        self.table_name = "projetos"
        self.primary_key = "id"

    # ------------------------------------------------------------------
    # Métodos específicos de projeto
    # ------------------------------------------------------------------
    def exists_code(self, code: str) -> bool:
        """Retorna True se já existe projeto com o código especificado"""
        results = self.find_by("project_code", code)
        return bool(results)

    def find_by_code(self, code: str) -> Optional[Dict[str, Any]]:
        """Busca projeto utilizando o código único"""
        results = self.find_by("project_code", code)
        return results[0] if results else None

    
    def find_by_user(self, user_id: int, status: str = None) -> List[Dict[str, Any]]:
        """
        Lista projetos onde o usuário é membro da equipe
        """
        base_query = """
            SELECT DISTINCT p.id, p.nome, p.descricao, p.endereco, p.cliente, 
                   p.valor_total, p.data_inicio, p.data_fim_prevista, p.data_fim_real, 
                   p.status, p.progresso_percentual, p.criador_id, p.criado_em, p.atualizado_em
            FROM projetos p
            INNER JOIN equipes e ON p.id = e.projeto_id
            WHERE e.usuario_id = %s AND e.ativo = 1
        """
        
        params = [user_id]
        
        if status:
            base_query += " AND p.status = %s"
            params.append(status)
        
        base_query += " ORDER BY p.criado_em DESC"
        
        try:
            return self.execute_raw(base_query, tuple(params), fetch=True) or []
        except Exception as e:
            logger.error(f"Error finding projects by user {user_id}: {str(e)}")
            raise
    
    def find_with_stats(self, project_id: int) -> Optional[Dict[str, Any]]:
        """
        Busca projeto com estatísticas de tarefas
        """
        query = """
            SELECT p.*,
                   COUNT(t.id) as total_tarefas,
                   SUM(CASE WHEN t.status = 'concluida' THEN 1 ELSE 0 END) as tarefas_concluidas,
                   SUM(CASE WHEN t.status = 'em_andamento' THEN 1 ELSE 0 END) as tarefas_andamento,
                   SUM(CASE WHEN t.status = 'pendente' THEN 1 ELSE 0 END) as tarefas_pendentes
            FROM projetos p
            LEFT JOIN tarefas t ON p.id = t.projeto_id
            WHERE p.id = %s
            GROUP BY p.id
        """
        
        try:
            result = self.execute_raw(query, (project_id,), fetch=True)
            return result[0] if result else None
        except Exception as e:
            logger.error(f"Error finding project with stats {project_id}: {str(e)}")
            raise
    
    def update_progress(self, project_id: int) -> float:
        """
        Recalcula e atualiza progresso do projeto baseado nas tarefas
        """
        query = """
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'concluida' THEN 1 ELSE 0 END) as concluidas
            FROM tarefas 
            WHERE projeto_id = %s
        """
        
        try:
            result = self.execute_raw(query, (project_id,), fetch=True)
            if result and result[0]['total'] > 0:
                progress = (result[0]['concluidas'] / result[0]['total']) * 100
            else:
                progress = 0.0
            
            self.update(project_id, {'progresso_percentual': progress})
            logger.info(f"Updated project {project_id} progress to {progress}%")
            return progress
        except Exception as e:
            logger.error(f"Error updating progress for project {project_id}: {str(e)}")
            raise
    
    def get_dashboard_stats(self, user_id: int) -> Dict[str, Any]:
        """
        Retorna estatísticas do dashboard para o usuário
        """
        query = """
            SELECT 
                COUNT(DISTINCT p.id) as total_projetos,
                SUM(CASE WHEN p.status = 'em_andamento' THEN 1 ELSE 0 END) as em_andamento,
                SUM(CASE WHEN p.status = 'concluido' THEN 1 ELSE 0 END) as concluidos,
                SUM(CASE WHEN p.status = 'planejamento' THEN 1 ELSE 0 END) as planejamento,
                AVG(p.progresso_percentual) as progresso_medio
            FROM projetos p
            INNER JOIN equipes e ON p.id = e.projeto_id
            WHERE e.usuario_id = %s AND e.ativo = 1
        """
        
        try:
            result = self.execute_raw(query, (user_id,), fetch=True)
            return result[0] if result else {}
        except Exception as e:
            logger.error(f"Error getting dashboard stats for user {user_id}: {str(e)}")
            raise
    
    def search(self, user_id: int, termo: str) -> List[Dict[str, Any]]:
        """
        Pesquisa projetos por nome, descrição ou cliente
        """
        query = """
            SELECT DISTINCT p.*
            FROM projetos p
            INNER JOIN equipes e ON p.id = e.projeto_id
            WHERE e.usuario_id = %s AND e.ativo = 1
            AND (p.nome LIKE %s OR p.descricao LIKE %s OR p.cliente LIKE %s)
            ORDER BY p.criado_em DESC
        """
        
        search_term = f"%{termo}%"
        
        try:
            return self.execute_raw(
                query, 
                (user_id, search_term, search_term, search_term), 
                fetch=True
            ) or []
        except Exception as e:
            logger.error(f"Error searching projects: {str(e)}")
            raise
