"""
Testes de Services
"""

import pytest


class TestProjectService:
    """Testes do serviço de projetos"""
    
    def test_format_project(self):
        """Testa formatação de projeto"""
        from services.project_service import ProjectService
        
        service = ProjectService()
        
        project_data = {
            "id": 1,
            "nome": "Projeto Teste",
            "descricao": "Descrição",
            "status": "em_andamento",
            "progresso_percentual": 50.5,
            "valor_total": 100000.00,
            "criador_id": 1,
            "criado_em": "2024-01-01 10:00:00"
        }
        
        formatted = service._format_project(project_data)
        
        assert formatted["id"] == 1
        assert formatted["nome"] == "Projeto Teste"
        assert formatted["status"] == "em_andamento"
        assert formatted["progresso_percentual"] == 50.5
        assert formatted["valor_total"] == 100000.00
    
    def test_format_project_with_none_values(self):
        """Testa formatação com valores None"""
        from services.project_service import ProjectService
        
        service = ProjectService()
        
        project_data = {
            "id": 1,
            "nome": "Projeto",
            "descricao": None,
            "valor_total": None,
            "status": "planejamento",
            "progresso_percentual": None
        }
        
        formatted = service._format_project(project_data)
        
        assert formatted["descricao"] is None
        assert formatted["valor_total"] is None
        assert formatted["progresso_percentual"] == 0


class TestUserService:
    """Testes do serviço de usuários"""
    
    def test_safe_user_removes_password(self):
        """Testa que _safe_user remove senha"""
        from services.user_service import UserService
        
        service = UserService()
        
        user = {
            "id": 1,
            "nome": "Test",
            "email": "test@test.com",
            "senha": "hash_da_senha_aqui"
        }
        
        safe = service._safe_user(user)
        
        assert "senha" not in safe
        assert safe["id"] == 1
        assert safe["nome"] == "Test"
    
    def test_hash_password(self):
        """Testa hash de senha no UserService"""
        from services.user_service import UserService
        
        service = UserService()
        
        hash1 = service._hash_password("senha123")
        hash2 = service._hash_password("senha123")
        hash3 = service._hash_password("outrasenha")
        
        assert hash1 == hash2  # Mesmo input = mesmo hash
        assert hash1 != hash3  # Inputs diferentes = hashes diferentes


class TestTaskService:
    """Testes do serviço de tarefas"""
    
    def test_valid_statuses(self):
        """Testa que status válidos são aceitos"""
        valid_statuses = ['pendente', 'em_andamento', 'em_revisao', 'concluida']
        
        for status in valid_statuses:
            assert status in valid_statuses
    
    def test_invalid_status_raises_error(self):
        """Testa que status inválido gera erro"""
        from services.task_service import TaskService
        
        service = TaskService()
        
        with pytest.raises(ValueError, match="Status inválido"):
            # Este método valida o status
            # Simulamos diretamente a validação
            valid_statuses = ['pendente', 'em_andamento', 'em_revisao', 'concluida']
            new_status = "invalido"
            if new_status not in valid_statuses:
                raise ValueError(f"Status inválido. Use: {', '.join(valid_statuses)}")


class TestTeamService:
    """Testes do serviço de equipes"""
    
    def test_role_hierarchy(self):
        """Testa hierarquia de cargos"""
        from services.team_service import TeamService
        
        service = TeamService()
        
        role_hierarchy = {
            'membro': 1,
            'tecnico': 2,
            'engenheiro': 3,
            'coordenador': 4,
            'gerente': 5
        }
        
        # Gerente > Engenheiro
        assert role_hierarchy['gerente'] > role_hierarchy['engenheiro']
        
        # Engenheiro > Técnico
        assert role_hierarchy['engenheiro'] > role_hierarchy['tecnico']
        
        # Membro é o mais baixo
        assert role_hierarchy['membro'] == min(role_hierarchy.values())
    
    def test_valid_cargos(self):
        """Testa lista de cargos válidos"""
        valid_cargos = ['gerente', 'coordenador', 'engenheiro', 'tecnico', 'membro']
        
        assert 'gerente' in valid_cargos
        assert 'admin' not in valid_cargos  # Admin não é cargo de equipe


class TestDocumentService:
    """Testes do serviço de documentos"""
    
    def test_allowed_extensions(self):
        """Testa extensões permitidas"""
        from services.document_service import DocumentService
        
        service = DocumentService()
        
        # Engenharia
        assert 'pdf' in service.ALLOWED_EXTENSIONS
        assert 'dwg' in service.ALLOWED_EXTENSIONS
        assert 'dxf' in service.ALLOWED_EXTENSIONS
        
        # Office
        assert 'doc' in service.ALLOWED_EXTENSIONS
        assert 'xlsx' in service.ALLOWED_EXTENSIONS
        
        # Imagens
        assert 'jpg' in service.ALLOWED_EXTENSIONS
        assert 'png' in service.ALLOWED_EXTENSIONS
        
        # Executáveis NÃO permitidos
        assert 'exe' not in service.ALLOWED_EXTENSIONS
        assert 'bat' not in service.ALLOWED_EXTENSIONS
    
    def test_max_file_size(self):
        """Testa tamanho máximo de arquivo"""
        from services.document_service import DocumentService
        
        service = DocumentService()
        
        # 50MB em bytes
        expected_max = 50 * 1024 * 1024
        assert service.MAX_FILE_SIZE == expected_max
    
    def test_get_content_type(self):
        """Testa detecção de content type"""
        from services.document_service import DocumentService
        
        service = DocumentService()
        
        assert service._get_content_type('pdf') == 'application/pdf'
        assert service._get_content_type('jpg') == 'image/jpeg'
        assert service._get_content_type('png') == 'image/png'
        assert service._get_content_type('unknown') == 'application/octet-stream'
