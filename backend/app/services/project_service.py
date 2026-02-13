"""
ProjectService - Lógica de negócio para Projetos
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import date, datetime

from app.repositories import ProjectRepository, TeamRepository, TaskRepository

logger = logging.getLogger(__name__)


class ProjectService:
    """Service para operações de projetos"""
    
    def __init__(self):
        self.project_repo = ProjectRepository()
        self.team_repo = TeamRepository()
        self.task_repo = TaskRepository()
    
    def list_user_projects(
        self, 
        user_id: int, 
        status: str = None,
        page: int = 1,
        per_page: int = 20
    ) -> Dict[str, Any]:
        """
        Lista projetos do usuário com paginação
        """
        logger.info(f"Listing projects for user {user_id}, status={status}")
        
        projects = self.project_repo.find_by_user(user_id, status)
        
        # Enriquecer dados
        result = []
        for project in projects:
            project_data = self._format_project(project)
            project_data['membros_count'] = len(
                self.team_repo.find_members(project['id'])
            )
            result.append(project_data)
        
        # Paginação
        start = (page - 1) * per_page
        end = start + per_page
        
        return {
            'items': result[start:end],
            'total': len(result),
            'page': page,
            'per_page': per_page,
            'pages': (len(result) + per_page - 1) // per_page
        }
    
    def get_project(self, project_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtém detalhes de um projeto com verificação de acesso
        """
        # Verificar acesso
        if not self.team_repo.is_member(project_id, user_id):
            logger.warning(f"User {user_id} tried to access project {project_id} without permission")
            return None
        
        project = self.project_repo.find_with_stats(project_id)
        if not project:
            return None
        
        # Adicionar membros da equipe
        project_data = self._format_project(project)
        project_data['equipe'] = self.team_repo.find_members(project_id)
        project_data['documentos_recentes'] = []  # Pode ser populado depois
        
        return project_data
    
    def create_project(self, data: Dict[str, Any], creator_id: int) -> Dict[str, Any]:
        """
        Cria novo projeto e adiciona criador como gerente
        """
        logger.info(f"Creating project '{data.get('nome')}' for user {creator_id}")
        
        # Preparar dados
        project_data = {
            'nome': data['nome'],
            'descricao': data.get('descricao'),
            'endereco': data.get('endereco'),
            'cliente': data.get('cliente'),
            'valor_total': data.get('valor_total'),
            'data_inicio': data.get('data_inicio'),
            'data_fim_prevista': data.get('data_fim_prevista'),
            'status': data.get('status', 'planejamento'),
            'progresso_percentual': 0,
            'criador_id': creator_id
        }
        
        # Criar projeto
        project_id = self.project_repo.create(project_data)
        
        # Adicionar criador como gerente
        self.team_repo.add_member(project_id, creator_id, 'gerente')
        
        logger.info(f"Project created with ID {project_id}")
        
        return self.project_repo.find_by_id(project_id)
    
    def update_project(
        self, 
        project_id: int, 
        data: Dict[str, Any], 
        user_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Atualiza projeto com verificação de permissão
        """
        # Verificar se é gerente
        if not self.team_repo.is_manager(project_id, user_id):
            logger.warning(f"User {user_id} tried to update project {project_id} without manager permission")
            return None
        
        # Filtrar campos atualizáveis
        allowed_fields = [
            'nome', 'descricao', 'endereco', 'cliente', 'valor_total',
            'data_inicio', 'data_fim_prevista', 'data_fim_real', 'status'
        ]
        update_data = {k: v for k, v in data.items() if k in allowed_fields and v is not None}
        
        if update_data:
            self.project_repo.update(project_id, update_data)
            logger.info(f"Project {project_id} updated by user {user_id}")
        
        return self.project_repo.find_by_id(project_id)
    
    def delete_project(self, project_id: int, user_id: int) -> bool:
        """
        Deleta projeto (apenas gerente/criador)
        """
        project = self.project_repo.find_by_id(project_id)
        if not project:
            return False
        
        # Verificar se é criador ou gerente
        is_creator = project.get('criador_id') == user_id
        is_manager = self.team_repo.is_manager(project_id, user_id)
        
        if not (is_creator or is_manager):
            logger.warning(f"User {user_id} tried to delete project {project_id} without permission")
            return False
        
        self.project_repo.delete(project_id)
        logger.info(f"Project {project_id} deleted by user {user_id}")
        return True
    
    def get_dashboard_data(self, user_id: int) -> Dict[str, Any]:
        """
        Retorna dados completos para dashboard
        """
        logger.info(f"Getting dashboard data for user {user_id}")
        
        # Estatísticas de projetos
        project_stats = self.project_repo.get_dashboard_stats(user_id)
        
        # Estatísticas de tarefas
        task_stats = self.task_repo.get_statistics(user_id=user_id)
        
        # Tarefas atrasadas
        overdue_tasks = self.task_repo.find_overdue(user_id)
        
        # Tarefas próximas
        upcoming_tasks = self.task_repo.find_upcoming(user_id, 7)
        
        # Projetos recentes
        projects = self.project_repo.find_by_user(user_id)[:5]
        
        return {
            'projetos': {
                'total': project_stats.get('total_projetos', 0),
                'em_andamento': project_stats.get('em_andamento', 0),
                'concluidos': project_stats.get('concluidos', 0),
                'planejamento': project_stats.get('planejamento', 0),
                'progresso_medio': float(project_stats.get('progresso_medio') or 0)
            },
            'tarefas': {
                'total': task_stats.get('total', 0),
                'pendentes': task_stats.get('pendentes', 0),
                'em_andamento': task_stats.get('em_andamento', 0),
                'concluidas': task_stats.get('concluidas', 0),
                'atrasadas': task_stats.get('atrasadas', 0)
            },
            'tarefas_atrasadas': overdue_tasks[:5],
            'tarefas_proximas': upcoming_tasks[:5],
            'projetos_recentes': [self._format_project(p) for p in projects]
        }
    
    def recalculate_progress(self, project_id: int) -> float:
        """
        Recalcula progresso do projeto baseado nas tarefas
        """
        return self.project_repo.update_progress(project_id)
    
    def _format_project(self, project: Dict[str, Any]) -> Dict[str, Any]:
        """Formata dados do projeto para resposta"""
        return {
            'id': project.get('id'),
            'nome': project.get('nome'),
            'descricao': project.get('descricao'),
            'endereco': project.get('endereco'),
            'cliente': project.get('cliente'),
            'valor_total': float(project.get('valor_total')) if project.get('valor_total') else None,
            'data_inicio': str(project.get('data_inicio')) if project.get('data_inicio') else None,
            'data_fim_prevista': str(project.get('data_fim_prevista')) if project.get('data_fim_prevista') else None,
            'data_fim_real': str(project.get('data_fim_real')) if project.get('data_fim_real') else None,
            'status': project.get('status'),
            'progresso_percentual': float(project.get('progresso_percentual') or 0),
            'criador_id': project.get('criador_id'),
            'criado_em': str(project.get('criado_em')) if project.get('criado_em') else None,
            'atualizado_em': str(project.get('atualizado_em')) if project.get('atualizado_em') else None,
            'total_tarefas': project.get('total_tarefas', 0),
            'tarefas_concluidas': project.get('tarefas_concluidas', 0)
        }
