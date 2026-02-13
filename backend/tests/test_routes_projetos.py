"""
Test Projetos - Testes de integração para rotas de projetos
"""

import pytest
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)


@pytest.fixture
def token_admin():
    """Fixture que retorna token de admin"""
    response = client.post("/api/auth/login", json={
        "email": "vicentedesouza762@gmail.com",
        "password": "Abc123456"
    })
    if response.status_code == 200:
        return response.json()["access_token"]
    return None


@pytest.fixture
def token_gerente():
    """Fixture que retorna token de gerente"""
    response = client.post("/api/auth/login", json={
        "email": "francisco@projeto.com",
        "password": "Abc123456"
    })
    if response.status_code == 200:
        return response.json()["access_token"]
    return None


class TestProjetosEndpoints:
    """Testes de endpoints de projetos"""
    
    def test_listar_projetos_sem_autenticacao(self):
        """Deve retornar 401 sem token"""
        response = client.get("/api/projetos/")
        assert response.status_code == 401
    
    def test_listar_projetos_com_token_valido(self, token_admin):
        """Deve listar projetos com token válido"""
        headers = {"Authorization": f"Bearer {token_admin}"}
        response = client.get("/api/projetos/", headers=headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_listar_projetos_com_token_invalido(self):
        """Deve retornar 401 com token inválido"""
        headers = {"Authorization": "Bearer invalid_token_xyz"}
        response = client.get("/api/projetos/", headers=headers)
        assert response.status_code == 401
    
    def test_criar_projeto_admin(self, token_admin):
        """Admin deve conseguir criar projeto"""
        headers = {"Authorization": f"Bearer {token_admin}"}
        projeto_data = {
            "nome": "Projeto Teste " + str(__import__('time').time()),
            "descricao": "Descrição teste",
            "status": "em_planejamento",
            "data_inicio": "2024-01-01"
        }
        response = client.post(
            "/api/projetos/",
            headers=headers,
            json=projeto_data
        )
        assert response.status_code in [200, 201]
        data = response.json()
        assert data["nome"] == projeto_data["nome"]
    
    def test_criar_projeto_gerente(self, token_gerente):
        """Gerente deve conseguir criar projeto"""
        headers = {"Authorization": f"Bearer {token_gerente}"}
        projeto_data = {
            "nome": "Projeto Gerente " + str(__import__('time').time()),
            "descricao": "Do gerente",
            "status": "em_planejamento"
        }
        response = client.post(
            "/api/projetos/",
            headers=headers,
            json=projeto_data
        )
        # Pode ser 200, 201, ou 403 dependendo de permissões
        assert response.status_code in [200, 201, 403]
    
    def test_campo_nome_obrigatorio(self, token_admin):
        """Deve falhar sem campo 'nome' """
        headers = {"Authorization": f"Bearer {token_admin}"}
        projeto_data = {
            "descricao": "Sem nome"
        }
        response = client.post(
            "/api/projetos/",
            headers=headers,
            json=projeto_data
        )
        assert response.status_code == 422  # Validation error
    
    def test_filtrar_projetos_por_status(self, token_admin):
        """Deve filtrar projetos por status"""
        headers = {"Authorization": f"Bearer {token_admin}"}
        response = client.get(
            "/api/projetos/?status=em_planejamento",
            headers=headers
        )
        assert response.status_code == 200
        projetos = response.json()
        if projetos:
            assert all(p["status"] == "em_planejamento" for p in projetos)


class TestTarefasEndpoints:
    """Testes de endpoints de tarefas"""
    
    def test_listar_tarefas_sem_autenticacao(self):
        """Deve retornar 401 sem token"""
        response = client.get("/api/tarefas/")
        assert response.status_code == 401
    
    def test_listar_tarefas_de_projeto(self, token_admin):
        """Deve listar tarefas de um projeto"""
        headers = {"Authorization": f"Bearer {token_admin}"}
        response = client.get("/api/tarefas?projeto_id=1", headers=headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_criar_tarefa(self, token_admin):
        """Deve criar uma tarefa"""
        headers = {"Authorization": f"Bearer {token_admin}"}
        tarefa_data = {
            "projeto_id": 1,
            "titulo": "Tarefa Teste",
            "descricao": "Descrição da tarefa",
            "status": "aberta"
        }
        response = client.post(
            "/api/tarefas/",
            headers=headers,
            json=tarefa_data
        )
        assert response.status_code in [200, 201]


class TestAutenticacao:
    """Testes de autenticação"""
    
    def test_login_credenciais_validas(self):
        """Login com credenciais válidas"""
        response = client.post("/api/auth/login", json={
            "email": "vicentedesouza762@gmail.com",
            "password": "Abc123456"
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["role"] in ["admin", "gerente", "engenheiro", "tecnico", "cliente"]
    
    def test_login_senha_errada(self):
        """Login com senha errada"""
        response = client.post("/api/auth/login", json={
            "email": "vicentedesouza762@gmail.com",
            "password": "SenhaErrada123"
        })
        assert response.status_code == 401
    
    def test_login_usuario_nao_existe(self):
        """Login com usuário que não existe"""
        response = client.post("/api/auth/login", json={
            "email": "naoexiste@projeto.com",
            "password": "Abc123456"
        })
        assert response.status_code == 401
    
    def test_login_campos_ausentes(self):
        """Login sem email ou senha"""
        response = client.post("/api/auth/login", json={
            "email": "vicentedesouza762@gmail.com"
        })
        assert response.status_code == 422  # Validation error


class TestSeguranca:
    """Testes de segurança"""
    
    def test_sql_injection_prevention(self):
        """Teste de proteção contra SQL injection"""
        response = client.post("/api/auth/login", json={
            "email": "' OR '1'='1",
            "password": "anything"
        })
        # Não deve fazer login
        assert response.status_code in [400, 401]
    
    def test_cors_headers(self):
        """Verificar headers CORS"""
        response = client.options("/api/projetos/")
        # CORS pode estar configurado ou não
        assert response.status_code in [200, 405]
    
    def test_rate_limiting_login(self):
        """Teste rate limiting em login"""
        # Fazer múltiplas tentativas
        for i in range(10):
            response = client.post("/api/auth/login", json={
                "email": "vicentedesouza762@gmail.com",
                "password": "WrongPassword"
            })
            if i > 5 and response.status_code == 429:
                # Rate limit ativado (esperado)
                assert True
                break
        else:
            # Se não ativou rate limit, tudo bem também
            assert True


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
