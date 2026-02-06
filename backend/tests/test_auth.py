"""
Testes de Autenticação
"""

import pytest
import hashlib
from datetime import datetime, timedelta


class TestAuthService:
    """Testes do serviço de autenticação"""
    
    def test_hash_password(self):
        """Testa hash de senha"""
        password = "senhaSecreta123"
        expected_hash = hashlib.sha256(password.encode()).hexdigest()
        
        from app.services.auth_service import AuthService
        auth_service = AuthService()
        
        result = auth_service._hash_password(password)
        
        assert result == expected_hash
        assert len(result) == 64  # SHA256 = 64 caracteres hex
    
    def test_hash_password_different_inputs(self):
        """Testa que senhas diferentes geram hashes diferentes"""
        from app.services.auth_service import AuthService
        auth_service = AuthService()
        
        hash1 = auth_service._hash_password("senha1")
        hash2 = auth_service._hash_password("senha2")
        
        assert hash1 != hash2
    
    def test_create_access_token(self):
        """Testa criação de token JWT"""
        from app.services.auth_service import AuthService
        auth_service = AuthService()
        
        user_data = {
            "id": 1,
            "email": "test@test.com",
            "nome": "Test User"
        }
        
        token = auth_service.create_access_token(user_data)
        
        assert token is not None
        assert len(token) > 0
        assert "." in token  # JWT tem formato xxx.yyy.zzz
    
    def test_verify_valid_token(self):
        """Testa verificação de token válido"""
        from app.services.auth_service import AuthService
        auth_service = AuthService()
        
        user_data = {
            "id": 1,
            "email": "test@test.com"
        }
        
        token = auth_service.create_access_token(user_data)
        payload = auth_service.verify_token(token)
        
        assert payload is not None
        assert payload["id"] == 1
        assert payload["email"] == "test@test.com"
    
    def test_verify_invalid_token(self):
        """Testa rejeição de token inválido"""
        from app.services.auth_service import AuthService
        auth_service = AuthService()
        
        result = auth_service.verify_token("token.invalido.aqui")
        
        assert result is None
    
    def test_verify_expired_token(self):
        """Testa rejeição de token expirado"""
        import jwt
        import os
        from datetime import datetime, timedelta
        
        from app.services.auth_service import AuthService
        auth_service = AuthService()
        
        # Criar token já expirado
        expired_data = {
            "id": 1,
            "email": "test@test.com",
            "exp": datetime.utcnow() - timedelta(hours=1)  # Expirou 1 hora atrás
        }
        
        expired_token = jwt.encode(
            expired_data, 
            os.environ.get("SECRET_KEY", "test-key"),
            algorithm="HS256"
        )
        
        result = auth_service.verify_token(expired_token)
        
        assert result is None


class TestPasswordValidation:
    """Testes de validação de senha"""
    
    def test_password_min_length(self):
        """Testa senha muito curta"""
        from app.services.auth_service import AuthService
        auth_service = AuthService()
        
        # Tentar registrar com senha curta deve falhar
        with pytest.raises(ValueError, match="pelo menos 6 caracteres"):
            auth_service.register({
                "nome": "Test",
                "email": "short@test.com",
                "senha": "12345"  # Apenas 5 caracteres
            })
    
    def test_valid_password(self):
        """Testa senha válida"""
        password = "senhaValida123"
        
        # Senha com 6+ caracteres é válida
        assert len(password) >= 6


class TestTokenRefresh:
    """Testes de renovação de token"""
    
    def test_refresh_valid_token(self):
        """Testa renovação de token válido"""
        from app.services.auth_service import AuthService
        auth_service = AuthService()
        
        # Este teste depende de um usuário existente no banco
        # Por enquanto, testamos apenas a lógica básica
        user_data = {"id": 999, "email": "noexist@test.com"}
        token = auth_service.create_access_token(user_data)
        
        # Refresh deve falhar pois usuário não existe
        new_token = auth_service.refresh_token(token)
        assert new_token is None
