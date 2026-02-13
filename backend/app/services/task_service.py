"""
TaskService - Lógica de negócio para Tarefas
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import date, datetime, timedelta

from app.repositories import TaskRepository, TeamRepository, ProjectRepository

logger = logging.getLogger(__name__)


class TaskService:
    """Service para operações de tarefas"""
    
    def __init__(self):
        self.task_repo = TaskRepository()
        self.team_repo = TeamRepository()
        self.project_repo = ProjectRepository()
    
    def list_project_tasks(
        self, 
        project_id: int, 
        user_id: int,
        status: str = None
    ) -> List[Dict[str, Any]]:
        """
        Lista tarefas de um projeto com verificação de acesso
        """
        # Verificar acesso ao projeto
        if not self.team_repo.is_member(project_id, user_id):
            logger.warning(f"User {user_id} tried to access tasks of project {project_id}")
            return []
        
        return self.task_repo.find_by_project(project_id, status)
    
    def list_user_tasks(
        self, 
        user_id: int, 
        status: str = None
    ) -> List[Dict[str, Any]]:
        """
        Lista tarefas atribuídas ao usuário
        """
        return self.task_repo.find_by_user(user_id, status)
    
    def get_task(self, task_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtém detalhes de uma tarefa com verificação de acesso
        """
        task = self.task_repo.find_by_id(task_id)
        if not task:
            return None
        
        # Verificar acesso ao projeto
        if not self.team_repo.is_member(task['projeto_id'], user_id):
            logger.warning(f"User {user_id} tried to access task {task_id}")
            return None
        
        return task
    
    def create_task(
        self, 
        project_id: int, 
        data: Dict[str, Any], 
        creator_id: int
    ) -> Dict[str, Any]:
        """
        Cria nova tarefa
        """
        # Verificar acesso ao projeto
        if not self.team_repo.is_member(project_id, creator_id):
            raise PermissionError("Sem permissão para criar tarefa neste projeto")
        
        logger.info(f"Creating task '{data.get('titulo')}' in project {project_id}")
        
        task_data = {
            'projeto_id': project_id,
            'titulo': data['titulo'],
            'descricao': data.get('descricao'),
            'responsavel_id': data.get('responsavel_id'),
            'prioridade': data.get('prioridade', 'media'),
            'status': data.get('status', 'pendente'),
            'data_limite': data.get('data_limite'),
            'estimativa_horas': data.get('estimativa_horas'),
            'ordem': data.get('ordem', 0),
            'criador_id': creator_id
        }
        
        task_id = self.task_repo.create(task_data)
        
        # Recalcular progresso do projeto
        self.project_repo.update_progress(project_id)
        
        logger.info(f"Task created with ID {task_id}")
        
        return self.task_repo.find_by_id(task_id)
    
    def update_task(
        self, 
        task_id: int, 
        data: Dict[str, Any], 
        user_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Atualiza tarefa
        """
        task = self.task_repo.find_by_id(task_id)
        if not task:
            return None
        
        # Verificar acesso
        if not self.team_repo.is_member(task['projeto_id'], user_id):
            raise PermissionError("Sem permissão para editar esta tarefa")
        
        # Campos atualizáveis
        allowed_fields = [
            'titulo', 'descricao', 'responsavel_id', 'prioridade',
            'status', 'data_limite', 'estimativa_horas', 'horas_trabalhadas', 'ordem'
        ]
        update_data = {k: v for k, v in data.items() if k in allowed_fields}
        
        if update_data:
            self.task_repo.update(task_id, update_data)
            
            # Se mudou status, recalcular progresso
            if 'status' in update_data:
                self.project_repo.update_progress(task['projeto_id'])
            
            logger.info(f"Task {task_id} updated by user {user_id}")
        
        return self.task_repo.find_by_id(task_id)
    
    def update_status(
        self, 
        task_id: int, 
        new_status: str, 
        user_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Atualiza apenas o status da tarefa
        """
        valid_statuses = ['pendente', 'em_andamento', 'em_revisao', 'concluida']
        if new_status not in valid_statuses:
            raise ValueError(f"Status inválido. Use: {', '.join(valid_statuses)}")
        
        task = self.task_repo.find_by_id(task_id)
        if not task:
            return None
        
        # Verificar acesso
        if not self.team_repo.is_member(task['projeto_id'], user_id):
            raise PermissionError("Sem permissão para alterar status")
        
        self.task_repo.update_status(task_id, new_status)
        self.project_repo.update_progress(task['projeto_id'])
        
        logger.info(f"Task {task_id} status changed to {new_status} by user {user_id}")
        
        return self.task_repo.find_by_id(task_id)
    
    def delete_task(self, task_id: int, user_id: int) -> bool:
        """
        Deleta tarefa
        """
        task = self.task_repo.find_by_id(task_id)
        if not task:
            return False
        
        # Verificar se é gerente ou criador
        is_manager = self.team_repo.is_manager(task['projeto_id'], user_id)
        is_creator = task.get('criador_id') == user_id
        
        if not (is_manager or is_creator):
            raise PermissionError("Sem permissão para deletar esta tarefa")
        
        self.task_repo.delete(task_id)
        self.project_repo.update_progress(task['projeto_id'])
        
        logger.info(f"Task {task_id} deleted by user {user_id}")
        return True
    
    def get_kanban(self, project_id: int, user_id: int) -> Dict[str, List[Dict[str, Any]]]:
        """
        Retorna dados para visualização Kanban
        """
        if not self.team_repo.is_member(project_id, user_id):
            logger.warning(f"User {user_id} tried to access kanban of project {project_id}")
            return {}
        
        return self.task_repo.get_kanban_data(project_id)
    
    def move_task(
        self, 
        task_id: int, 
        new_status: str, 
        new_order: int, 
        user_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Move tarefa no Kanban (status e ordem)
        """
        task = self.task_repo.find_by_id(task_id)
        if not task:
            return None
        
        if not self.team_repo.is_member(task['projeto_id'], user_id):
            raise PermissionError("Sem permissão")
        
        self.task_repo.update(task_id, {
            'status': new_status,
            'ordem': new_order
        })
        
        self.project_repo.update_progress(task['projeto_id'])
        
        return self.task_repo.find_by_id(task_id)
    
    def get_overdue(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Lista tarefas atrasadas do usuário
        """
        return self.task_repo.find_overdue(user_id)
    
    def get_upcoming(self, user_id: int, days: int = 7) -> List[Dict[str, Any]]:
        """
        Lista tarefas com prazo próximo
        """
        return self.task_repo.find_upcoming(user_id, days)
    
    def get_statistics(
        self, 
        project_id: int = None, 
        user_id: int = None
    ) -> Dict[str, Any]:
        """
        Retorna estatísticas de tarefas
        """
        return self.task_repo.get_statistics(project_id, user_id)
