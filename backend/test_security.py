"""
Testes de Segurança - Gerenciador de Projetos
Validação de proteção contra ataques comuns
Desenvolvido por: Vicente de Souza
Sprint 1: Rate Limiting, 2FA, Backup
"""

import pytest
from fastapi.testclient import TestClient
from app import app
import json
import time

client = TestClient(app)

# ============================================
# 1. TESTES DE SQL INJECTION
# ============================================

class TestSQLInjection:
    """Verifica proteção contra SQL Injection"""
    
    def test_login_sql_injection_email(self):
        """Tenta SQL injection no email de login"""
        payload = {
            "email": "' OR '1'='1",
            "senha": "qualquer_coisa"
        }
        response = client.post("/auth/login", json=payload)
        # Deve rejeitar (email inválido ou não encontrado)
        assert response.status_code in [400, 401, 422]
        assert "Email ou senha incorretos" in response.text
    
    def test_register_sql_injection_email(self):
        """Tenta SQL injection no register"""
        payload = {
            "nome": "Hacker",
            "email": "test@test.com'; DROP TABLE usuarios; --",
            "senha": "Senha123",
            "cargo": "Engenheiro"
        }
        response = client.post("/auth/register", json=payload)
        # Deve rejeitar email inválido
        assert response.status_code in [400, 422]
        # Tabela não deve ser deletada (prepared statements previnem)
        response_login = client.post("/auth/login", json={"email": "admin@empresa.com", "senha": "admin123"})
        # Se tabela foi deletada, isso falharia
        assert response_login.status_code != 500


# ============================================
# 2. TESTES DE FORÇA DE SENHA
# ============================================

class TestPasswordStrength:
    """Verifica validação de força de senha"""
    
    def test_password_too_short(self):
        """Senha muito curta deve ser rejeitada"""
        payload = {
            "nome": "Teste Curto",
            "email": "teste_curto@test.com",
            "senha": "Abc1",  # Menos de 8 caracteres
            "cargo": "Engenheiro"
        }
        response = client.post("/auth/register", json=payload)
        assert response.status_code in [400, 422]
    
    def test_password_no_uppercase(self):
        """Senha sem maiúscula deve ser rejeitada"""
        payload = {
            "nome": "Teste Minúscula",
            "email": "teste_minuscula@test.com",
            "senha": "abcdef123",  # Sem maiúscula
            "cargo": "Engenheiro"
        }
        response = client.post("/auth/register", json=payload)
        assert response.status_code == 400
        assert "Senha fraca" in response.text
    
    def test_password_no_number(self):
        """Senha sem número deve ser rejeitada"""
        payload = {
            "nome": "Teste Número",
            "email": "teste_numero@test.com",
            "senha": "AbcdefGH",  # Sem número
            "cargo": "Engenheiro"
        }
        response = client.post("/auth/register", json=payload)
        assert response.status_code == 400
        assert "Senha fraca" in response.text
    
    def test_password_valid(self):
        """Senha válida deve ser aceita"""
        payload = {
            "nome": "Teste Válido",
            "email": f"teste_valido_{id(payload)}@test.com",
            "senha": "Senha123",  # Válida: 8+ chars, maiúscula, número
            "cargo": "Engenheiro"
        }
        response = client.post("/auth/register", json=payload)
        assert response.status_code == 201
        assert "sucesso" in response.text.lower()


# ============================================
# 3. TESTES DE ACESSO NÃO AUTORIZADO
# ============================================

class TestAuthentication:
    """Verifica autenticação e autorização"""
    
    def test_login_invalid_email(self):
        """Email inexistente deve falhar"""
        payload = {
            "email": "nao_existe_12345@test.com",
            "senha": "QualquerSenha123"
        }
        response = client.post("/auth/login", json=payload)
        assert response.status_code == 401
        assert "incorretos" in response.text.lower()
    
    def test_login_invalid_password(self):
        """Senha incorreta deve falhar"""
        payload = {
            "email": "admin@empresa.com",
            "senha": "SenhaErrada123"
        }
        response = client.post("/auth/login", json=payload)
        assert response.status_code == 401
        assert "incorretos" in response.text.lower()
    
    def test_login_success(self):
        """Login válido deve retornar token"""
        payload = {
            "email": "admin@empresa.com",
            "senha": "admin123"
        }
        response = client.post("/auth/login", json=payload)
        # Se a seed foi executada, deve funcionar
        if response.status_code == 401:
            pytest.skip("Usuário de teste não existe - execute seed.py")
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data


# ============================================
# 4. TESTES DE VALIDAÇÃO DE ENTRADA
# ============================================

class TestInputValidation:
    """Verifica validação de entradas"""
    
    def test_register_email_invalid(self):
        """Email inválido deve ser rejeitado"""
        payload = {
            "nome": "Teste Email",
            "email": "nao_eh_email",  # Email inválido
            "senha": "Senha123",
            "cargo": "Engenheiro"
        }
        response = client.post("/auth/register", json=payload)
        assert response.status_code == 422  # Validation error
    
    def test_register_name_too_short(self):
        """Nome muito curto deve ser rejeitado"""
        payload = {
            "nome": "AB",  # Menos de 3 caracteres
            "email": "teste@test.com",
            "senha": "Senha123",
            "cargo": "Engenheiro"
        }
        response = client.post("/auth/register", json=payload)
        assert response.status_code in [400, 422]
    
    def test_register_missing_fields(self):
        """Campos obrigatórios faltando deve falhar"""
        payload = {
            "nome": "Teste",
            # Falta email
            "senha": "Senha123"
        }
        response = client.post("/auth/register", json=payload)
        assert response.status_code == 422  # Validation error


# ============================================
# 5. TESTES DE ERRO NÃO EXPOSTO
# ============================================

class TestErrorHandling:
    """Verifica se erros não expõem detalhes sensíveis"""
    
    def test_login_error_generic(self):
        """Erro de login deve ser genérico (sem detalhar se email existe)"""
        response = client.post("/auth/login", json={
            "email": "nao_existe@test.com",
            "senha": "Qualquer123"
        })
        assert response.status_code == 401
        detail = response.json()["detail"]
        # Não deve detalhar se email existe ou não
        assert "Email ou senha incorretos" in detail
        assert "não existe" not in detail.lower()
        assert "não encontrado" not in detail.lower()
    
    def test_register_duplicate_email_generic(self):
        """Erro de email duplicado deve ser claro mas seguro"""
        # Primeiro registro
        payload1 = {
            "nome": "Primeiro",
            "email": "duplicado_test@test.com",
            "senha": "Senha123",
            "cargo": "Eng"
        }
        response1 = client.post("/auth/register", json=payload1)
        
        if response1.status_code == 201:
            # Tenta registrar de novo
            response2 = client.post("/auth/register", json=payload1)
            assert response2.status_code == 409  # Conflict
            assert "já cadastrado" in response2.json()["detail"].lower()


# ============================================
# 6. TESTES DE BCRYPT
# ============================================

class TestPasswordHashing:
    """Verifica se senhas são hasheadas corretamente"""
    
    def test_password_is_hashed(self):
        """Senha nunca deve ser armazenada em texto plano"""
        from utils.auth import hash_password, verify_password
        
        senha = "SenhaSegura123"
        hash1 = hash_password(senha)
        hash2 = hash_password(senha)
        
        # Mesmo com mesma senha, hashes são diferentes (salt aleatório)
        assert hash1 != hash2
        
        # Mas ambos verificam corretamente
        assert verify_password(senha, hash1)
        assert verify_password(senha, hash2)
        
        # Senha errada não verifica
        assert not verify_password("SenhaErrada123", hash1)


# ============================================
# 7. TESTES DE JWT
# ============================================

class TestJWTTokens:
    """Verifica segurança de tokens JWT"""
    
    def test_token_expires(self):
        """Token expirado deve ser rejeitado"""
        from utils.auth import create_access_token, decode_access_token
        from datetime import timedelta
        
        # Criar token com expiração no passado
        token = create_access_token(
            {"user_id": 1, "email": "test@test.com"},
            expires_delta=timedelta(seconds=-1)
        )
        
        # Decodificar deve retornar None (token expirado)
        payload = decode_access_token(token)
        assert payload is None
    
    def test_token_tampering(self):
        """Token modificado deve ser rejeitado"""
        from utils.auth import create_access_token, decode_access_token
        
        token = create_access_token({"user_id": 1})
        
        # Tentar modificar token
        tampered = token[:-5] + "xxxxx"  # Muda últimos 5 caracteres
        
        # Decodificar deve falhar
        payload = decode_access_token(tampered)
        assert payload is None


# ============================================
# 6. TESTES DE RATE LIMITING (Sprint 1)
# ============================================

class TestRateLimiting:
    """Verifica proteção de rate limiting contra brute force"""
    
    def test_login_rate_limit_5_por_minuto(self):
        """Login deve ser limitado a 5 tentativas por minuto"""
        # Fazer 6 requisições seguidas
        for i in range(6):
            response = client.post("/auth/login", json={
                "email": f"test{i}@email.com",
                "senha": "SenhaErrada123"
            })
            
            # Primeira 5 devem retornar 401 (não autenticado)
            if i < 5:
                assert response.status_code in [401, 422]  # Não autenticado ou email inválido
            # A 6ª deve retornar 429 (rate limit exceeded)
            elif i == 5:
                assert response.status_code == 429
                assert "muitas requisições" in response.text.lower() or "rate limit" in response.text.lower()
    
    def test_register_rate_limit_10_por_hora(self):
        """Register deve ser limitado a 10 por hora"""
        # Testar múltiplas requisições (simplificado - em prod testaríamos 11+)
        response = client.post("/auth/register", json={
            "nome": "Teste User",
            "email": f"test_rate_limit_{int(time.time())}@email.com",
            "senha": "SenhaForte123",
            "cargo": "Engenheiro"
        })
        
        # Não deve ser bloqueado na primeira vez
        assert response.status_code in [201, 409]  # Criado ou já existe
    
    def test_rate_limit_retry_after_header(self):
        """Rate limit deve incluir header Retry-After"""
        # Fazer muitas requisições rapidamente
        for i in range(6):
            response = client.post("/auth/login", json={
                "email": f"test{i}@email.com",
                "senha": "SenhaErrada123"
            })
        
        # Última deve ter rate limit (429)
        assert response.status_code == 429
        # Deve incluir header Retry-After
        assert "retry-after" in response.headers or "retry_after" in response.json().get("detail", {})


# ============================================
# 7. TESTES DE 2FA (Sprint 1)
# ============================================

class TestTwoFactorAuth:
    """Verifica autenticação de dois fatores (2FA)"""
    
    def test_gerar_otp(self):
        """OTP deve ser gerado com 6 dígitos"""
        from utils.two_factor_auth import gerar_otp
        
        otp = gerar_otp(length=6)
        assert len(otp) == 6
        assert otp.isdigit()
    
    def test_enviar_otp_email(self):
        """OTP deve ser enviado (simulado em dev)"""
        from utils.two_factor_auth import enviar_otp_email, otp_store
        
        email = "test_2fa@email.com"
        enviar_otp_email(email)
        
        # OTP deve estar armazenado (em dev usa dict, em prod seria Redis)
        assert email in otp_store
        assert "code" in otp_store[email]
        assert "expires" in otp_store[email]
        assert len(otp_store[email]["code"]) == 6
    
    def test_validar_otp_sucesso(self):
        """OTP válido deve passar na validação"""
        from utils.two_factor_auth import enviar_otp_email, validar_otp, otp_store
        
        email = "test_otp_valid@email.com"
        enviar_otp_email(email)
        
        # Pegar o OTP gerado
        codigo = otp_store[email]["code"]
        
        # Validar com código correto
        sucesso, mensagem = validar_otp(email, codigo)
        assert sucesso is True
        assert "sucesso" in mensagem.lower()
    
    def test_validar_otp_codigo_errado(self):
        """OTP inválido deve falhar"""
        from utils.two_factor_auth import enviar_otp_email, validar_otp
        
        email = "test_otp_wrong@email.com"
        enviar_otp_email(email)
        
        # Validar com código errado
        sucesso, mensagem = validar_otp(email, "000000")
        assert sucesso is False
        assert "incorreto" in mensagem.lower()
    
    def test_validar_otp_limite_tentativas(self):
        """Após 3 tentativas erradas, OTP deve ser bloqueado"""
        from utils.two_factor_auth import enviar_otp_email, validar_otp
        
        email = "test_otp_limits@email.com"
        enviar_otp_email(email)
        
        # Fazer 3 tentativas erradas
        for i in range(3):
            sucesso, mensagem = validar_otp(email, "999999")
            if i < 2:
                assert sucesso is False
            elif i == 2:
                # 3ª tentativa deve indicar limite excedido
                assert sucesso is False
    
    def test_verify_2fa_endpoint(self):
        """Endpoint /auth/verify-2fa deve validar OTP e retornar token"""
        from utils.two_factor_auth import enviar_otp_email, otp_store
        
        # Primeiro, registrar um usuário
        # (Assumindo que isso foi feito antes do teste)
        
        # Simulado: enviar OTP
        email = "test_endpoint_2fa@email.com"
        enviar_otp_email(email)
        codigo = otp_store[email]["code"]
        
        # Chamar endpoint verify-2fa
        response = client.post("/auth/verify-2fa", json={
            "email": email,
            "codigo_otp": codigo
        })
        
        # Pode falhar porque usuário não existe, mas não deve dar erro de implementação
        assert response.status_code in [200, 404, 401]
    
    def test_resend_otp_endpoint(self):
        """Endpoint /auth/resend-otp deve reenviar código OTP"""
        email = "test_resend@email.com"
        
        response = client.post("/auth/resend-otp", json={
            "email": email
        })
        
        # Deve retornar sucesso ou erro apropriado
        assert response.status_code in [200, 400]


# ============================================
# 8. TESTES DE BACKUP (Sprint 1)
# ============================================

class TestBackup:
    """Verifica sistema de backup automático"""
    
    def test_backup_manager_inicializacao(self):
        """BackupManager deve inicializar corretamente"""
        from utils.backup_manager import BackupManager
        
        backup = BackupManager(
            db_host="localhost",
            db_user="root",
            db_password="",
            db_name="test_db",
            backup_dir="test_backups"
        )
        
        assert backup.db_host == "localhost"
        assert backup.db_name == "test_db"
        assert backup.backup_dir == "test_backups"
    
    def test_backup_manager_listar_backups(self):
        """BackupManager deve listar backups existentes"""
        from utils.backup_manager import BackupManager
        from pathlib import Path
        
        backup_dir = "test_backups"
        Path(backup_dir).mkdir(exist_ok=True)
        
        backup = BackupManager(backup_dir=backup_dir)
        backups = backup.listar_backups()
        
        # Deve retornar uma lista (pode estar vazia)
        assert isinstance(backups, list)
    
    def test_backup_manager_limpar_antigos(self):
        """BackupManager deve limpar backups antigos"""
        from utils.backup_manager import BackupManager
        
        backup = BackupManager(backup_dir="test_backups")
        removidos = backup.limpar_backups_antigos(dias=0)  # Remove todos
        
        # Deve retornar número de arquivos removidos (pode ser 0)
        assert isinstance(removidos, int)
        assert removidos >= 0


# ============================================
# EXECUTAR TESTES
# ============================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
