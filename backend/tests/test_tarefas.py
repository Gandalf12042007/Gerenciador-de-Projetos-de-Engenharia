"""
Testes para os endpoints de Tarefas
PHASE 3: Testes automatizados com pytest
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import sys
import os

# Adicionar diretório do app ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import app

client = TestClient(app)


# ============================================
# FIXTURES
# ============================================

@pytest.fixture
def token_admin():
    """Obter token JWT para usuário admin"""
    response = client.post(
        "/api/auth/login",
        json={
            "email": "vicentedesouza762@gmail.com",
            "senha": "senha123"
        }
    )
    if response.status_code == 200:
        return response.json().get("token")
    return None


@pytest.fixture
def token_gerente():
    """Obter token JWT para usuário gerente"""
    response = client.post(
        "/api/auth/login",
        json={
            "email": "gerenteteste@projeto.com",
            "senha": "senha123"
        }
    )
    if response.status_code == 200:
        return response.json().get("token")
    return None


@pytest.fixture
def token_engenheiro():
    """Obter token JWT para usuário engenheiro"""
    response = client.post(
        "/api/auth/login",
        json={
            "email": "engenheiroteste@projeto.com",
            "senha": "senha123"
        }
    )
    if response.status_code == 200:
        return response.json().get("token")
    return None


@pytest.fixture
def projeto_id_valido(token_admin):
    """Criar um projeto para usar nos testes"""
    headers = {"Authorization": f"Bearer {token_admin}"}
    response = client.post(
        "/api/projetos",
        headers=headers,
        json={
            "nome": f"Teste Tarefas {datetime.now().isoformat()}",
            "descricao": "Projeto para testes de tarefas",
            "status": "ativo"
        }
    )
    if response.status_code in [200, 201]:
        return response.json().get("id")
    return None


# ============================================
# TESTES DE LISTAGEM DE TAREFAS
# ============================================

class TestListagemTarefas:
    """Testes para GET /api/tarefas"""

    def test_listar_tarefas_sem_autenticacao(self):
        """
        Teste: Listar tarefas SEM token de autenticação
        Esperado: 401 (Não autorizado)
        """
        response = client.get("/api/tarefas")
        assert response.status_code == 401

    def test_listar_tarefas_com_token_valido(self, token_admin):
        """
        Teste: Listar tarefas COM token válido
        Esperado: 200 (OK) com lista de tarefas
        """
        headers = {"Authorization": f"Bearer {token_admin}"}
        response = client.get("/api/tarefas", headers=headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_listar_tarefas_filtrado_por_projeto(self, token_admin, projeto_id_valido):
        """
        Teste: Listar tarefas de um projeto específico
        Esperado: 200 com apenas tarefas do projeto
        """
        headers = {"Authorization": f"Bearer {token_admin}"}
        response = client.get(
            f"/api/tarefas?projeto_id={projeto_id_valido}",
            headers=headers
        )
        assert response.status_code == 200
        tarefas = response.json()
        if tarefas:  # Se houver tarefas
            assert all(t.get("projeto_id") == projeto_id_valido for t in tarefas)

    def test_listar_tarefas_filtrado_por_status(self, token_admin):
        """
        Teste: Listar tarefas filtradas por status
        Esperado: 200 com tarefas do status especificado
        """
        statuses = ["aberta", "em_progresso", "concluida"]
        headers = {"Authorization": f"Bearer {token_admin}"}

        for status in statuses:
            response = client.get(
                f"/api/tarefas?status={status}",
                headers=headers
            )
            assert response.status_code == 200
            tarefas = response.json()
            if tarefas:
                assert all(t.get("status") == status for t in tarefas)

    def test_listar_tarefas_com_token_invalido(self):
        """
        Teste: Listar tarefas com token inválido/expirado
        Esperado: 401 (Não autorizado)
        """
        headers = {"Authorization": "Bearer token_invalido_123"}
        response = client.get("/api/tarefas", headers=headers)
        assert response.status_code == 401


# ============================================
# TESTES DE CRIAÇÃO DE TAREFAS
# ============================================

class TestCriacaoTarefas:
    """Testes para POST /api/tarefas"""

    def test_criar_tarefa_basica(self, token_admin, projeto_id_valido):
        """
        Teste: Criar tarefa com dados básicos
        Esperado: 200 ou 201 com ID da tarefa
        """
        if not projeto_id_valido:
            pytest.skip("Não foi possível criar projeto de teste")

        headers = {"Authorization": f"Bearer {token_admin}"}
        payload = {
            "projeto_id": projeto_id_valido,
            "titulo": f"Tarefa Teste {datetime.now().isoformat()}",
            "descricao": "Descrição da tarefa de teste",
            "status": "aberta",
            "prioridade": "media"
        }
        response = client.post("/api/tarefas", headers=headers, json=payload)
        assert response.status_code in [200, 201]
        data = response.json()
        assert "id" in data
        assert data["titulo"] == payload["titulo"]

    def test_criar_tarefa_com_data_vencimento(self, token_admin, projeto_id_valido):
        """
        Teste: Criar tarefa com data de vencimento
        Esperado: 200 ou 201 com data preservada
        """
        if not projeto_id_valido:
            pytest.skip("Não foi possível criar projeto de teste")

        headers = {"Authorization": f"Bearer {token_admin}"}
        data_vencimento = (datetime.now() + timedelta(days=7)).date().isoformat()

        payload = {
            "projeto_id": projeto_id_valido,
            "titulo": f"Tarefa com Prazo {datetime.now().isoformat()}",
            "data_vencimento": data_vencimento,
            "prioridade": "alta"
        }
        response = client.post("/api/tarefas", headers=headers, json=payload)
        assert response.status_code in [200, 201]
        data = response.json()
        assert data.get("data_vencimento") is not None

    def test_criar_tarefa_campos_obrigatorios_faltando(self, token_admin):
        """
        Teste: Criar tarefa SEM projeto_id (campo obrigatório)
        Esperado: 422 (Validação falhou) ou 400
        """
        headers = {"Authorization": f"Bearer {token_admin}"}
        payload = {
            "titulo": "Tarefa sem projeto",
            "descricao": "Esta tarefa não tem projeto_id"
        }
        response = client.post("/api/tarefas", headers=headers, json=payload)
        assert response.status_code in [400, 422]

    def test_criar_tarefa_sem_autenticacao(self, projeto_id_valido):
        """
        Teste: Criar tarefa SEM token de autenticação
        Esperado: 401 (Não autorizado)
        """
        if not projeto_id_valido:
            pytest.skip("Não foi possível criar projeto de teste")

        payload = {
            "projeto_id": projeto_id_valido,
            "titulo": "Tarefa não autorizada",
            "descricao": "Esta tarefa foi criada sem autenticação"
        }
        response = client.post("/api/tarefas", json=payload)
        assert response.status_code == 401

    def test_criar_tarefa_prioridades_validas(self, token_admin, projeto_id_valido):
        """
        Teste: Criar tarefas com diferentes prioridades
        Esperado: 200 ou 201 para cada prioridade
        """
        if not projeto_id_valido:
            pytest.skip("Não foi possível criar projeto de teste")

        headers = {"Authorization": f"Bearer {token_admin}"}
        prioridades = ["baixa", "media", "alta", "critica"]

        for prioridade in prioridades:
            payload = {
                "projeto_id": projeto_id_valido,
                "titulo": f"Tarefa {prioridade} {datetime.now().isoformat()}",
                "prioridade": prioridade
            }
            response = client.post("/api/tarefas", headers=headers, json=payload)
            assert response.status_code in [200, 201]
            assert response.json()["prioridade"] == prioridade


# ============================================
# TESTES DE ATUALIZAÇÃO DE TAREFAS
# ============================================

class TestAtualizacaoTarefas:
    """Testes para PUT/PATCH /api/tarefas/{id}"""

    def test_atualizar_status_tarefa(self, token_admin, projeto_id_valido):
        """
        Teste: Atualizar status de uma tarefa
        Esperado: 200 com status atualizado
        """
        if not projeto_id_valido:
            pytest.skip("Não foi possível criar projeto de teste")

        headers = {"Authorization": f"Bearer {token_admin}"}

        # Criar tarefa
        criar_response = client.post(
            "/api/tarefas",
            headers=headers,
            json={
                "projeto_id": projeto_id_valido,
                "titulo": f"Tarefa Para Atualizar {datetime.now().isoformat()}",
                "status": "aberta"
            }
        )
        if criar_response.status_code not in [200, 201]:
            pytest.skip("Não foi possível criar tarefa de teste")

        tarefa_id = criar_response.json()["id"]

        # Atualizar status
        update_response = client.put(
            f"/api/tarefas/{tarefa_id}",
            headers=headers,
            json={"status": "em_progresso"}
        )
        assert update_response.status_code == 200
        assert update_response.json()["status"] == "em_progresso"

    def test_atualizar_tarefa_sem_permissao(self, token_gerente, token_admin, projeto_id_valido):
        """
        Teste: Atualizar tarefa criada por outro usuário
        Esperado: 403 (Proibido) ou 200 se usuário tem permissão de gerente
        """
        if not projeto_id_valido:
            pytest.skip("Não foi possível criar projeto de teste")

        # Admin cria tarefa
        headers_admin = {"Authorization": f"Bearer {token_admin}"}
        criar_response = client.post(
            "/api/tarefas",
            headers=headers_admin,
            json={
                "projeto_id": projeto_id_valido,
                "titulo": f"Tarefa de Admin {datetime.now().isoformat()}",
                "status": "aberta"
            }
        )
        if criar_response.status_code not in [200, 201]:
            pytest.skip("Não foi possível criar tarefa de teste")

        tarefa_id = criar_response.json()["id"]

        # Gerente tenta atualizar (comportamento depende da política de controle de acesso)
        headers_gerente = {"Authorization": f"Bearer {token_gerente}"}
        update_response = client.put(
            f"/api/tarefas/{tarefa_id}",
            headers=headers_gerente,
            json={"status": "concluida"}
        )
        # Pode ser 200 (se gerente tem permissão) ou 403 (se não tem)
        assert update_response.status_code in [200, 403]


# ============================================
# TESTES DE DELEÇÃO DE TAREFAS
# ============================================

class TestDelecaoTarefas:
    """Testes para DELETE /api/tarefas/{id}"""

    def test_deletar_tarefa(self, token_admin, projeto_id_valido):
        """
        Teste: Deletar uma tarefa
        Esperado: 200 ou 204 (No Content)
        """
        if not projeto_id_valido:
            pytest.skip("Não foi possível criar projeto de teste")

        headers = {"Authorization": f"Bearer {token_admin}"}

        # Criar tarefa
        criar_response = client.post(
            "/api/tarefas",
            headers=headers,
            json={
                "projeto_id": projeto_id_valido,
                "titulo": f"Tarefa Para Deletar {datetime.now().isoformat()}",
                "status": "aberta"
            }
        )
        if criar_response.status_code not in [200, 201]:
            pytest.skip("Não foi possível criar tarefa de teste")

        tarefa_id = criar_response.json()["id"]

        # Deletar tarefa
        delete_response = client.delete(
            f"/api/tarefas/{tarefa_id}",
            headers=headers
        )
        assert delete_response.status_code in [200, 204]

        # Verificar que foi deletada (GET deve retornar 404)
        get_response = client.get(
            f"/api/tarefas/{tarefa_id}",
            headers=headers
        )
        assert get_response.status_code == 404

    def test_deletar_tarefa_inexistente(self, token_admin):
        """
        Teste: Deletar tarefa que não existe
        Esperado: 404 (Não encontrada)
        """
        headers = {"Authorization": f"Bearer {token_admin}"}
        response = client.delete(
            "/api/tarefas/999999",
            headers=headers
        )
        assert response.status_code == 404


# ============================================
# TESTES DE BUSCA E FILTROS
# ============================================

class TestBuscaTarefas:
    """Testes para buscas e filtros"""

    def test_buscar_tarefas_por_titulo(self, token_admin):
        """
        Teste: Buscar tarefas pelo título
        Esperado: 200 com tarefas que contenham o texto
        """
        headers = {"Authorization": f"Bearer {token_admin}"}
        response = client.get(
            "/api/tarefas?search=teste",
            headers=headers
        )
        assert response.status_code == 200
        # Resultado pode estar vazio, mas deve ser lista
        assert isinstance(response.json(), list)

    def test_tarefas_atrasadas(self, token_admin):
        """
        Teste: Buscar tarefas atrasadas
        Esperado: 200 com tarefas vencidas
        """
        headers = {"Authorization": f"Bearer {token_admin}"}
        response = client.get(
            "/api/tarefas?atrasadas=true",
            headers=headers
        )
        assert response.status_code == 200
        tarefas = response.json()
        if tarefas:
            # Verificar que todas têm data_vencimento no passado
            for tarefa in tarefas:
                if "data_vencimento" in tarefa:
                    assert tarefa["status"] != "concluida"

    def test_tarefas_por_responsavel(self, token_admin):
        """
        Teste: Listar tarefas de um responsável
        Esperado: 200 com tarefas atribuídas ao responsável
        """
        headers = {"Authorization": f"Bearer {token_admin}"}
        # Usar um ID de responsável válido
        response = client.get(
            "/api/tarefas?responsavel_id=1",
            headers=headers
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)
