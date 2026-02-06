"""
Testes das Exceções Customizadas
"""

import pytest
from utils.exceptions import (
    AppException,
    AuthenticationError,
    TokenExpiredError,
    PermissionDeniedError,
    ResourceNotFoundError,
    ResourceAlreadyExistsError,
    ValidationError,
    FileUploadError,
    FileTooLargeError,
    InvalidFileTypeError,
    RateLimitExceededError
)


class TestAppException:
    """Testes da exceção base"""
    
    def test_basic_exception(self):
        """Testa criação de exceção básica"""
        exc = AppException("Erro de teste")
        
        assert exc.message == "Erro de teste"
        assert exc.status_code == 500
        assert exc.error_code == "INTERNAL_ERROR"
    
    def test_custom_status_code(self):
        """Testa exceção com status code customizado"""
        exc = AppException("Erro", status_code=400)
        
        assert exc.status_code == 400
    
    def test_to_dict(self):
        """Testa conversão para dicionário"""
        exc = AppException("Erro teste", status_code=400, error_code="TEST_ERROR")
        result = exc.to_dict()
        
        assert result["error"] == True
        assert result["message"] == "Erro teste"
        assert result["status_code"] == 400
        assert result["error_code"] == "TEST_ERROR"


class TestAuthenticationExceptions:
    """Testes de exceções de autenticação"""
    
    def test_authentication_error(self):
        """Testa AuthenticationError"""
        exc = AuthenticationError()
        
        assert exc.status_code == 401
        assert exc.error_code == "AUTHENTICATION_FAILED"
        assert "Credenciais" in exc.message
    
    def test_authentication_error_custom_message(self):
        """Testa AuthenticationError com mensagem customizada"""
        exc = AuthenticationError("Email não encontrado")
        
        assert exc.message == "Email não encontrado"
    
    def test_token_expired_error(self):
        """Testa TokenExpiredError"""
        exc = TokenExpiredError()
        
        assert exc.status_code == 401
        assert exc.error_code == "TOKEN_EXPIRED"


class TestAuthorizationExceptions:
    """Testes de exceções de autorização"""
    
    def test_permission_denied_error(self):
        """Testa PermissionDeniedError"""
        exc = PermissionDeniedError()
        
        assert exc.status_code == 403
        assert exc.error_code == "PERMISSION_DENIED"
    
    def test_permission_denied_with_resource(self):
        """Testa PermissionDeniedError com recurso"""
        exc = PermissionDeniedError(
            "Sem permissão para deletar",
            resource="projeto",
            action="delete"
        )
        
        assert exc.details["resource"] == "projeto"
        assert exc.details["action"] == "delete"


class TestResourceExceptions:
    """Testes de exceções de recursos"""
    
    def test_resource_not_found(self):
        """Testa ResourceNotFoundError"""
        exc = ResourceNotFoundError("Projeto", 123)
        
        assert exc.status_code == 404
        assert exc.error_code == "NOT_FOUND"
        assert "123" in exc.message
        assert "Projeto" in exc.message
    
    def test_resource_already_exists(self):
        """Testa ResourceAlreadyExistsError"""
        exc = ResourceAlreadyExistsError("Usuario", "email", "test@test.com")
        
        assert exc.status_code == 409
        assert exc.error_code == "ALREADY_EXISTS"
        assert "email" in exc.message
        assert "test@test.com" in exc.message


class TestValidationExceptions:
    """Testes de exceções de validação"""
    
    def test_validation_error(self):
        """Testa ValidationError"""
        exc = ValidationError("Campo inválido", field="email")
        
        assert exc.status_code == 422
        assert exc.error_code == "VALIDATION_ERROR"
        assert exc.details["field"] == "email"
    
    def test_validation_error_with_multiple_errors(self):
        """Testa ValidationError com múltiplos erros"""
        errors = [
            {"field": "email", "error": "Formato inválido"},
            {"field": "nome", "error": "Muito curto"}
        ]
        exc = ValidationError("Erros de validação", errors=errors)
        
        assert len(exc.details["errors"]) == 2


class TestFileExceptions:
    """Testes de exceções de arquivo"""
    
    def test_file_upload_error(self):
        """Testa FileUploadError"""
        exc = FileUploadError("Falha no upload", filename="teste.pdf")
        
        assert exc.status_code == 400
        assert exc.details["filename"] == "teste.pdf"
    
    def test_file_too_large(self):
        """Testa FileTooLargeError"""
        exc = FileTooLargeError(max_size_mb=50, actual_size_mb=75.5)
        
        assert exc.status_code == 413
        assert exc.error_code == "FILE_TOO_LARGE"
        assert "50MB" in exc.message
        assert "75.50MB" in exc.message
    
    def test_invalid_file_type(self):
        """Testa InvalidFileTypeError"""
        exc = InvalidFileTypeError("exe", ["pdf", "doc", "xlsx"])
        
        assert exc.status_code == 415
        assert exc.error_code == "INVALID_FILE_TYPE"
        assert "exe" in exc.message
        assert "pdf" in exc.message


class TestRateLimitException:
    """Testes de exceção de rate limit"""
    
    def test_rate_limit_exceeded(self):
        """Testa RateLimitExceededError"""
        exc = RateLimitExceededError(limit=100, window="hour")
        
        assert exc.status_code == 429
        assert exc.error_code == "RATE_LIMIT_EXCEEDED"
        assert exc.details["limit"] == 100
        assert exc.details["window"] == "hour"
