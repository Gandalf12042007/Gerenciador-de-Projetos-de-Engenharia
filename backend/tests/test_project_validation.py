"""
Testes para o sistema de validação de projeto selecionado

Demonstra os diferentes cenários de erro
"""

import pytest
from fastapi import Depends
from fastapi.testclient import TestClient

# Imports para os testes
from exceptions.project_exceptions import (
    ProjetoNaoSelecionadoException,
    ProjetoInvalidoException,
    ProjetoAcessoNegadoException
)
from utils.project_validator import ProjectValidator


class TestProjetoNaoSelecionado:
    """Testes para quando usuário não seleciona projeto"""
    
    def test_projeto_id_none(self):
        """Deve lançar exceção quando projeto_id é None"""
        with pytest.raises(ProjetoNaoSelecionadoException) as exc_info:
            ProjectValidator.verificar_projeto_id(None)
        
        assert "Nenhum projeto foi selecionado" in str(exc_info.value.detail)
        assert exc_info.value.status_code == 400
        assert exc_info.value.headers["X-Error-Type"] == "NO_PROJECT_SELECTED"
    
    def test_projeto_id_zero(self):
        """Deve lançar exceção quando projeto_id é 0"""
        with pytest.raises(ProjetoNaoSelecionadoException):
            ProjectValidator.verificar_projeto_id(0)
    
    def test_projeto_id_string_invalida(self):
        """Deve lançar exceção quando projeto_id é string inválida"""
        with pytest.raises(ProjetoNaoSelecionadoException):
            ProjectValidator.verificar_projeto_id("abc")
    
    def test_projeto_id_vazio(self):
        """Deve lançar exceção quando projeto_id é vazio"""
        with pytest.raises(ProjetoNaoSelecionadoException):
            ProjectValidator.verificar_projeto_id("")


class TestProjetoInvalido:
    """Testes para quando projeto não existe"""
    
    def test_mensagem_projeto_invalido(self):
        """Deve ter mensagem clara quando projeto não existe"""
        exc = ProjetoInvalidoException()
        
        assert "Projeto não encontrado" in exc.detail
        assert exc.status_code == 404
        assert exc.headers["X-Error-Type"] == "INVALID_PROJECT"
    
    def test_mensagem_customizada(self):
        """Deve permitir mensagem customizada"""
        msg_custom = "❌ Projeto específico não encontrado"
        exc = ProjetoInvalidoException(detail=msg_custom)
        
        assert exc.detail == msg_custom


class TestProjetoAcessoNegado:
    """Testes para quando usuário não tem acesso"""
    
    def test_mensagem_acesso_negado(self):
        """Deve ter mensagem clara quando acesso é negado"""
        exc = ProjetoAcessoNegadoException()
        
        assert "permissão" in exc.detail
        assert exc.status_code == 403
        assert exc.headers["X-Error-Type"] == "PROJECT_ACCESS_DENIED"


class TestValidadorProjectId:
    """Testes para o validador de projeto_id"""
    
    def test_string_valida_convertida(self):
        """Deve converter string numérica válida para int"""
        result = ProjectValidator.verificar_projeto_id("123")
        assert result == 123
        assert isinstance(result, int)
    
    def test_int_valido(self):
        """Deve aceitar int válido"""
        result = ProjectValidator.verificar_projeto_id(123)
        assert result == 123
    
    def test_numero_negativo(self):
        """Deve rejeitar número negativo"""
        with pytest.raises(ProjetoNaoSelecionadoException):
            ProjectValidator.verificar_projeto_id(-1)


# --- new unit test for project code generation ---

def test_generate_project_code_unique(monkeypatch):
    """_generate_unique_code deve retornar string de 4 caracteres e respeitar unicidade"""
    from services.project_service import ProjectService
    svc = ProjectService()

    # simular colisão na primeira tentativa
    attempts = [True, False]
    def fake_exists(code):
        return attempts.pop(0)
    monkeypatch.setattr(svc.project_repo, 'exists_code', fake_exists)

    code = svc._generate_unique_code()
    assert isinstance(code, str)
    assert len(code) == 4

class TestIntegracaoCompleta:
    """Testes de integração com endpoints"""
    
    # Exemplo de teste de endpoint
    def test_listar_tarefas_sem_projeto(self, client: TestClient):
        """GET /tarefas/null deve retornar erro 400"""
        response = client.get("/tarefas/null")
        
        assert response.status_code == 400
        assert "Nenhum projeto foi selecionado" in response.json()["detail"]
        assert response.headers.get("X-Error-Type") == "NO_PROJECT_SELECTED"
    
    def test_listar_tarefas_projeto_inexistente(self, client: TestClient):
        """GET /tarefas/999 deve retornar erro 404"""
        response = client.get("/tarefas/999")
        
        assert response.status_code == 404
        assert "não foi encontrado" in response.json()["detail"]
        assert response.headers.get("X-Error-Type") == "INVALID_PROJECT"


# ============ CENÁRIOS DE TESTE MANUAL ============

"""
Execute estes testes manualmente com curl:

1. PROJETO NÃO SELECIONADO (deve retornar 400):
   curl -X GET "http://localhost:8000/api/tarefas/" \
     -H "Authorization: Bearer TOKEN"
   
   Resposta esperada:
   {
     "detail": "❌ Nenhum projeto foi selecionado. Selecione um projeto para continuar."
   }

2. PROJETO INVÁLIDO (deve retornar 404):
   curl -X GET "http://localhost:8000/api/tarefas/999" \
     -H "Authorization: Bearer TOKEN"
   
   Resposta esperada:
   {
     "detail": "❌ Projeto #999 não foi encontrado..."
   }

3. ACESSO NEGADO (deve retornar 403):
   curl -X GET "http://localhost:8000/api/tarefas/1" \
     -H "Authorization: Bearer TOKEN_DE_OUTRO_USUARIO"
   
   Resposta esperada:
   {
     "detail": "❌ Você não tem permissão para acessar o projeto #1"
   }

4. SUCESSO (deve retornar 200):
   curl -X GET "http://localhost:8000/api/tarefas/1" \
     -H "Authorization: Bearer TOKEN_DO_MEMBRO"
   
   Resposta esperada: (lista de tarefas)
"""


# ============ TESTES POSTMAN ============

"""
Configurar no Postman:

1. Collection: Validação de Projeto
   
2. Test 1: Projeto Não Selecionado
   URL: {{base_url}}/tarefas/
   Método: GET
   Headers: Authorization: Bearer {{token}}
   Expected: 400
   
   Test Script:
   pm.test("Status deve ser 400", function() {
     pm.response.to.have.status(400);
   });
   
   pm.test("Deve conter mensagem de projeto não selecionado", function() {
     let json = pm.response.json();
     pm.expect(json.detail).to.include("Nenhum projeto foi selecionado");
   });
   
   pm.test("Header X-Error-Type deve ser NO_PROJECT_SELECTED", function() {
     pm.expect(pm.response.headers.get("X-Error-Type")).to.equal("NO_PROJECT_SELECTED");
   });

3. Test 2: Projeto Inválido
   URL: {{base_url}}/tarefas/999
   Método: GET
   Headers: Authorization: Bearer {{token}}
   Expected: 404
   
   Test Script:
   pm.test("Status deve ser 404", function() {
     pm.response.to.have.status(404);
   });

4. Test 3: Acesso Negado
   URL: {{base_url}}/tarefas/1
   Método: GET
   Headers: Authorization: Bearer {{token_sem_acesso}}
   Expected: 403
   
   Test Script:
   pm.test("Status deve ser 403", function() {
     pm.response.to.have.status(403);
   });
"""


if __name__ == "__main__":
    print("""
    Para executar os testes:
    
    pytest backend/tests/test_project_validation.py -v
    
    Para teste único:
    pytest backend/tests/test_project_validation.py::TestProjetoNaoSelecionado::test_projeto_id_none -v
    """)
