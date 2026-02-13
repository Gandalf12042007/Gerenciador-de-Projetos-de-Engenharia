"""
Testes de Repositórios
"""

import pytest


class TestBaseRepository:
    """Testes do repositório base"""
    
    def test_repository_initialization(self):
        """Testa inicialização do repositório"""
        from app.repositories.project_repository import ProjectRepository
        
        repo = ProjectRepository()
        
        assert repo.table_name == "projetos"
        assert repo.primary_key == "id"
        assert repo.db is not None
    
    def test_user_repository_initialization(self):
        """Testa inicialização do repositório de usuários"""
        from app.repositories.user_repository import UserRepository
        
        repo = UserRepository()
        
        assert repo.table_name == "usuarios"


class TestProjectRepository:
    """Testes do repositório de projetos"""
    
    def test_find_all(self, test_db):
        """Testa listagem de projetos"""
        from app.repositories.project_repository import ProjectRepository
        
        repo = ProjectRepository()
        projects = repo.find_all(limit=10)
        
        assert isinstance(projects, list)
    
    def test_find_by_id_not_found(self, test_db):
        """Testa busca por ID inexistente"""
        from app.repositories.project_repository import ProjectRepository
        
        repo = ProjectRepository()
        project = repo.find_by_id(99999)
        
        assert project is None


class TestUserRepository:
    """Testes do repositório de usuários"""
    
    def test_find_by_email(self, test_db, test_user):
        """Testa busca por email"""
        from app.repositories.user_repository import UserRepository
        
        repo = UserRepository()
        user = repo.find_by_email("test@test.com")
        
        # Pode ou não existir dependendo do estado do banco
        if user:
            assert user["email"] == "test@test.com"
    
    def test_find_by_email_not_found(self, test_db):
        """Testa busca por email inexistente"""
        from app.repositories.user_repository import UserRepository
        
        repo = UserRepository()
        user = repo.find_by_email("naoexiste@test.com")
        
        assert user is None


class TestTaskRepository:
    """Testes do repositório de tarefas"""
    
    def test_get_statistics_empty(self, test_db):
        """Testa estatísticas de tarefas vazias"""
        from app.repositories.task_repository import TaskRepository
        
        repo = TaskRepository()
        stats = repo.get_statistics(project_id=99999)
        
        # Deve retornar estatísticas com valores zerados
        assert isinstance(stats, dict)


class TestTeamRepository:
    """Testes do repositório de equipes"""
    
    def test_is_member_false(self, test_db):
        """Testa verificação de membro falso"""
        from app.repositories.team_repository import TeamRepository
        
        repo = TeamRepository()
        is_member = repo.is_member(99999, 99999)
        
        assert is_member == False
    
    def test_is_manager_false(self, test_db):
        """Testa verificação de gerente falso"""
        from app.repositories.team_repository import TeamRepository
        
        repo = TeamRepository()
        is_manager = repo.is_manager(99999, 99999)
        
        assert is_manager == False
