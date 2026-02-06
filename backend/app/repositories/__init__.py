"""
Repositórios - Camada de Acesso a Dados
"""

from .base_repository import BaseRepository
from .project_repository import ProjectRepository
from .user_repository import UserRepository
from .task_repository import TaskRepository
from .team_repository import TeamRepository
from .document_repository import DocumentRepository

__all__ = [
    'BaseRepository',
    'ProjectRepository', 
    'UserRepository',
    'TaskRepository',
    'TeamRepository',
    'DocumentRepository'
]
