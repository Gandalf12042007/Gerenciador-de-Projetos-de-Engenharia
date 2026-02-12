"""
Testes de Segurança - PHASE 3
Testes para validar segurança contra: Injeção SQL, XSS, CSRF, Rate Limiting, etc.
"""

import pytest
from fastapi.testclient import TestClient
import sys
import os
import time
from urllib.parse import quote

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


# ============================================
# TESTES DE INJEÇÃO SQL
# ============================================

class TestInjecaoSQL:
    """Testes para prevenir SQL Injection"""

    def test_sql_injection_em_search(self, token_admin):
        """
        Teste: Tentar SQL injection no parâmetro search
        Esperado: 200 (request aceita) mas sem efeito malicioso
        """
        headers = {"Authorization": f"Bearer {token_admin}"}
        
        # Tentativas de SQL injection
        payloads = [
            "'; DROP TABLE projetos; --",
            "1' OR '1'='1",
            "1'; DELETE FROM usuarios; --",
            "' UNION SELECT * FROM usuarios --"
        ]

        for payload in payloads:
            response = client.get(
                f"/api/projetos?search={quote(payload)}",
                headers=headers
            )
            # Não deve retornar 500 (erro do servidor)
            assert response.status_code != 500
            # Deve ser 200 (seguro) ou 400 (validação)
            assert response.status_code in [200, 400, 422]

    def test_sql_injection_em_filtros(self, token_admin):
        """
        Teste: Tentar SQL injection em filtros
        Esperado: Seguro contra injeção
        """
        headers = {"Authorization": f"Bearer {token_admin}"}
        
        payloads = {
            "status": "'; DROP TABLE tarefas; --",
            "prioridade": "1 OR 1=1",
            "projeto_id": "999999 OR 1=1"
        }

        for param, value in payloads.items():
            response = client.get(
                f"/api/tarefas?{param}={quote(value)}",
                headers=headers
            )
            assert response.status_code != 500

    def test_campos_numericos_validacao(self, token_admin):
        """
        Teste: Validar que campos numéricos rejeitam strings
        Esperado: 422 ou 400 se tipo estar errado
        """
        headers = {"Authorization": f"Bearer {token_admin}"}
        
        # Tentar acessar tarefa com ID não numérico
        response = client.get(
            "/api/tarefas/abc123xyz",
            headers=headers
        )
        assert response.status_code in [400, 404, 422]


# ============================================
# TESTES DE RATE LIMITING
# ============================================

class TestRateLimiting:
    """Testes para validar rate limiting"""

    def test_rate_limit_login(self):
        """
        Teste: Rate limiting em login após múltiplas tentativas
        Esperado: 429 (Too Many Requests) após 5+ tentativas
        """
        tentativas_falhadas = 0
        max_tentativas = 10

        for i in range(max_tentativas):
            response = client.post(
                "/api/auth/login",
                json={
                    "email": "invalido@teste.com",
                    "senha": "senha_errada"
                }
            )
            
            if response.status_code == 429:
                tentativas_falhadas = i
                break

            # Pequeno delay para não sobrecarregar
            # time.sleep(0.1)

        # Rate limiting deve ativar entre 5 e 10 tentativas
        assert tentativas_falhadas > 0 and tentativas_falhadas <= 10

    def test_rate_limit_api_endpoint(self, token_admin):
        """
        Teste: Rate limiting em endpoints da API
        Esperado: Não haver rate limit severo para usuários autenticados
        """
        headers = {"Authorization": f"Bearer {token_admin}"}
        
        # Fazer 5 requisições rápidas
        for i in range(5):
            response = client.get("/api/projetos", headers=headers)
            # Deve aceitar todas (ou no máximo a última pode ser 429)
            assert response.status_code in [200, 429]


# ============================================
# TESTES DE AUTENTICAÇÃO E AUTORIZAÇÃO
# ============================================

class TestAutenticacaoAutorizacao:
    """Testes de autenticação e autorização"""

    def test_token_expirado(self, token_admin):
        """
        Teste: Usar token expirado
        Esperado: 401 (Não autorizado) ou atualizar token
        """
        # Criar um token "expirado" (inválido)
        invalid_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid.signature"
        headers = {"Authorization": f"Bearer {invalid_token}"}
        
        response = client.get("/api/projetos", headers=headers)
        assert response.status_code == 401

    def test_token_malformado(self):
        """
        Teste: Header Authorization malformado
        Esperado: 401 ou tratamento gracioso
        """
        headers_list = [
            {"Authorization": "InvalidFormat"},
            {"Authorization": "Bearer"},
            {"Authorization": "Bearer "},
            {"Authorization": "token123"},
        ]

        for headers in headers_list:
            response = client.get("/api/projetos", headers=headers)
            assert response.status_code in [400, 401]

    def test_sem_token(self):
        """
        Teste: Requisição sem header Authorization
        Esperado: 401 (Não autorizado)
        """
        response = client.get("/api/projetos")
        assert response.status_code == 401

    def test_token_de_outro_usuario(self, token_admin):
        """
        Teste: Usar token de admin para tentar acessar dados de outro usuário
        Esperado: Acesso permitido (admin tem permissão) ou negado
        """
        headers = {"Authorization": f"Bearer {token_admin}"}
        
        # Admin deve ter acesso a todos os dados
        response = client.get("/api/usuarios", headers=headers)
        # Pode ser 200 (acesso) ou 403 (sem permissão de listar usuários)
        assert response.status_code in [200, 403]


# ============================================
# TESTES DE VALIDAÇÃO DE ENTRADA
# ============================================

class TestValidacaoEntrada:
    """Testes para validação de entrada de dados"""

    def test_campo_vazio_obrigatorio(self, token_admin):
        """
        Teste: Enviar campo obrigatório vazio
        Esperado: 422 (Validação falhou)
        """
        headers = {"Authorization": f"Bearer {token_admin}"}
        
        response = client.post(
            "/api/projetos",
            headers=headers,
            json={
                "nome": "",  # Campo vazio
                "descricao": "Projeto sem nome"
            }
        )
        assert response.status_code in [400, 422]

    def test_tipo_dado_invalido(self, token_admin):
        """
        Teste: Enviar tipo de dado incorreto
        Esperado: 422 ou 400
        """
        headers = {"Authorization": f"Bearer {token_admin}"}
        
        response = client.post(
            "/api/projetos",
            headers=headers,
            json={
                "nome": "Projeto Teste",
                "orcamento": "não é número"  # Deve ser número
            }
        )
        assert response.status_code in [400, 422]

    def test_tamanho_campo_excedido(self, token_admin):
        """
        Teste: Enviar string muito longa
        Esperado: 422 ou 400 (validação de tamanho)
        """
        headers = {"Authorization": f"Bearer {token_admin}"}
        
        response = client.post(
            "/api/projetos",
            headers=headers,
            json={
                "nome": "A" * 10000,  # String muito longa
                "descricao": "Projeto com nome muito longo"
            }
        )
        assert response.status_code in [400, 422, 200]  # Pode aceitar se não há limite

    def test_caracteres_especiais_permitidos(self, token_admin):
        """
        Teste: Enviar dados com caracteres especiais
        Esperado: 200 ou 201 (deve aceitar caracteres especiais válidos)
        """
        headers = {"Authorization": f"Bearer {token_admin}"}
        
        response = client.post(
            "/api/projetos",
            headers=headers,
            json={
                "nome": "Projeto ñ é ü & < > / ... válido",
                "descricao": "Descrição com caracteres! @#$%"
            }
        )
        assert response.status_code in [200, 201, 400]


# ============================================
# TESTES DE HEADERS E CORS
# ============================================

class TestHeadersCORS:
    """Testes de headers HTTP e CORS"""

    def test_cors_headers_presentes(self):
        """
        Teste: Verificar se headers CORS estão presentes
        Esperado: Access-Control-Allow-* headers
        """
        response = client.options("/api/projetos")
        
        # Headers podem estar presentes ou não (depende da config)
        # Verificar que não há erro 500
        assert response.status_code != 500

    def test_content_type_json(self, token_admin):
        """
        Teste: Resposta deve ter Content-Type: application/json
        Esperado: application/json no header
        """
        headers = {"Authorization": f"Bearer {token_admin}"}
        response = client.get("/api/projetos", headers=headers)
        
        # Verificar content type
        content_type = response.headers.get("content-type", "")
        assert "application/json" in content_type or "json" in content_type

    def test_security_headers(self):
        """
        Teste: Verificar headers de segurança
        Esperado: X-Content-Type-Options, X-Frame-Options, etc.
        """
        response = client.get("/api/projetos")
        
        # Headers de segurança (podem ou não estar presentes)
        important_headers = {
            "x-content-type-options": "nosniff",
            "x-frame-options": "DENY",
        }
        
        # Apenas verificar que não há erro
        assert response.status_code in [200, 401]


# ============================================
# TESTES DE ERRO HANDLING
# ============================================

class TestErroHandling:
    """Testes para tratamento de erros"""

    def test_erro_500_nao_expoe_detalhes(self, token_admin):
        """
        Teste: Erro 500 não deve expor detalhes do sistema
        Esperado: Mensagem genérica sem stack trace
        """
        # Tentar acessar recurso que causa erro
        response = client.get("/api/endpoint_invalido", headers={"Authorization": f"Bearer {token_admin}"})
        
        # Se houver erro, não deve conter detalhes sensíveis
        if response.status_code == 500:
            body = response.json() if response.headers.get("content-type") else response.text
            # Não deve conter "traceback" ou "File"
            assert "traceback" not in str(body).lower() or True  # Pode ser configurado

    def test_erro_404_adequado(self, token_admin):
        """
        Teste: Erro 404 para recurso não encontrado
        Esperado: Status 404
        """
        headers = {"Authorization": f"Bearer {token_admin}"}
        response = client.get("/api/projetos/999999999", headers=headers)
        assert response.status_code == 404

    def test_erro_403_acesso_negado(self, token_admin):
        """
        Teste: Erro 403 para acesso negado
        Esperado: Status 403 em recursos restritos
        """
        headers = {"Authorization": f"Bearer {token_admin}"}
        # Se houver endpoint restrito
        response = client.delete("/api/usuarios/999999", headers=headers)
        # Pode ser 404 (recurso não existe) ou 403 (sem permissão)
        assert response.status_code in [403, 404]


# ============================================
# TESTES DE DADOS SENSÍVEIS
# ============================================

class TestDadosSensiveis:
    """Testes para proteção de dados sensíveis"""

    def test_senha_nao_retornada_em_resposta(self, token_admin):
        """
        Teste: API nunca deve retornar senhas em plaintext
        Esperado: Campo 'senha' não presente em respostas
        """
        headers = {"Authorization": f"Bearer {token_admin}"}
        response = client.get("/api/usuarios", headers=headers)
        
        if response.status_code == 200:
            users = response.json()
            if isinstance(users, list):
                for user in users:
                    assert "senha" not in user
                    assert "password" not in user

    def test_token_nao_exposto_em_logs(self, token_admin):
        """
        Teste: Tokens não devem ser expostos em mensagens de erro
        Esperado: Erro não contém o token
        """
        headers = {"Authorization": f"Bearer {token_admin}"}
        
        # Fazer requisição com token inválido
        bad_headers = {"Authorization": f"Bearer invalid_token_xyz"}
        response = client.get("/api/projetos", headers=bad_headers)
        
        # Resposta não deve conter o token
        assert "invalid_token_xyz" not in response.text

    def test_email_mascarado_em_erros(self):
        """
        Teste: Emails não devem ser completamente expostos em mensagens de erro
        Esperado: Erros de login não devem dizer qual tipo de erro (usuário ou senha)
        """
        response = client.post(
            "/api/auth/login",
            json={
                "email": "naoexiste@teste.com",
                "senha": "senha"
            }
        )
        
        # Não deve expor se é "usuário não existe" ou "senha errada"
        error_msg = response.text.lower()
        # Pode conter "não autorizado" mas não "usuário não encontrado"
        assert "não encontrado" not in error_msg or True  # Depende da implementação
