"""
Exceções Customizadas - Tratamento de Erros da Aplicação
"""

from typing import Any, Dict, Optional


class AppException(Exception):
    """Exceção base da aplicação"""
    
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: str = None,
        details: Dict[str, Any] = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or "INTERNAL_ERROR"
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte exceção para dicionário"""
        return {
            "error": True,
            "message": self.message,
            "error_code": self.error_code,
            "status_code": self.status_code,
            "details": self.details
        }


# === Exceções de Autenticação ===

class AuthenticationError(AppException):
    """Erro de autenticação"""
    
    def __init__(self, message: str = "Credenciais inválidas", details: Dict = None):
        super().__init__(
            message=message,
            status_code=401,
            error_code="AUTHENTICATION_FAILED",
            details=details
        )


class TokenExpiredError(AppException):
    """Token JWT expirado"""
    
    def __init__(self, message: str = "Token expirado"):
        super().__init__(
            message=message,
            status_code=401,
            error_code="TOKEN_EXPIRED"
        )


class InvalidTokenError(AppException):
    """Token JWT inválido"""
    
    def __init__(self, message: str = "Token inválido"):
        super().__init__(
            message=message,
            status_code=401,
            error_code="INVALID_TOKEN"
        )


# === Exceções de Autorização ===

class PermissionDeniedError(AppException):
    """Usuário sem permissão"""
    
    def __init__(
        self, 
        message: str = "Você não tem permissão para esta ação",
        resource: str = None,
        action: str = None
    ):
        super().__init__(
            message=message,
            status_code=403,
            error_code="PERMISSION_DENIED",
            details={"resource": resource, "action": action}
        )


class InsufficientRoleError(AppException):
    """Cargo insuficiente para ação"""
    
    def __init__(self, required_role: str, current_role: str):
        super().__init__(
            message=f"Cargo '{current_role}' insuficiente. Necessário: '{required_role}'",
            status_code=403,
            error_code="INSUFFICIENT_ROLE",
            details={"required_role": required_role, "current_role": current_role}
        )


# === Exceções de Recursos ===

class ResourceNotFoundError(AppException):
    """Recurso não encontrado"""
    
    def __init__(self, resource_type: str, resource_id: Any):
        super().__init__(
            message=f"{resource_type} com ID {resource_id} não encontrado",
            status_code=404,
            error_code="NOT_FOUND",
            details={"resource_type": resource_type, "resource_id": resource_id}
        )


class ResourceAlreadyExistsError(AppException):
    """Recurso já existe"""
    
    def __init__(self, resource_type: str, field: str, value: Any):
        super().__init__(
            message=f"{resource_type} com {field}='{value}' já existe",
            status_code=409,
            error_code="ALREADY_EXISTS",
            details={"resource_type": resource_type, "field": field, "value": value}
        )


# === Exceções de Validação ===

class ValidationError(AppException):
    """Erro de validação de dados"""
    
    def __init__(self, message: str, field: str = None, errors: list = None):
        super().__init__(
            message=message,
            status_code=422,
            error_code="VALIDATION_ERROR",
            details={"field": field, "errors": errors or []}
        )


class InvalidInputError(AppException):
    """Entrada inválida"""
    
    def __init__(self, field: str, message: str):
        super().__init__(
            message=f"Campo '{field}': {message}",
            status_code=400,
            error_code="INVALID_INPUT",
            details={"field": field}
        )


# === Exceções de Negócio ===

class BusinessLogicError(AppException):
    """Erro de regra de negócio"""
    
    def __init__(self, message: str, rule: str = None):
        super().__init__(
            message=message,
            status_code=400,
            error_code="BUSINESS_RULE_VIOLATION",
            details={"rule": rule}
        )


class OperationNotAllowedError(AppException):
    """Operação não permitida no estado atual"""
    
    def __init__(self, operation: str, reason: str):
        super().__init__(
            message=f"Operação '{operation}' não permitida: {reason}",
            status_code=400,
            error_code="OPERATION_NOT_ALLOWED",
            details={"operation": operation, "reason": reason}
        )


# === Exceções de Upload ===

class FileUploadError(AppException):
    """Erro no upload de arquivo"""
    
    def __init__(self, message: str, filename: str = None):
        super().__init__(
            message=message,
            status_code=400,
            error_code="FILE_UPLOAD_ERROR",
            details={"filename": filename}
        )


class FileTooLargeError(AppException):
    """Arquivo muito grande"""
    
    def __init__(self, max_size_mb: int, actual_size_mb: float):
        super().__init__(
            message=f"Arquivo muito grande. Máximo: {max_size_mb}MB, Enviado: {actual_size_mb:.2f}MB",
            status_code=413,
            error_code="FILE_TOO_LARGE",
            details={"max_size_mb": max_size_mb, "actual_size_mb": actual_size_mb}
        )


class InvalidFileTypeError(AppException):
    """Tipo de arquivo não permitido"""
    
    def __init__(self, file_type: str, allowed_types: list):
        super().__init__(
            message=f"Tipo '{file_type}' não permitido. Permitidos: {', '.join(allowed_types)}",
            status_code=415,
            error_code="INVALID_FILE_TYPE",
            details={"file_type": file_type, "allowed_types": allowed_types}
        )


# === Exceções de Banco de Dados ===

class DatabaseError(AppException):
    """Erro de banco de dados"""
    
    def __init__(self, message: str = "Erro interno do banco de dados"):
        super().__init__(
            message=message,
            status_code=500,
            error_code="DATABASE_ERROR"
        )


class ConnectionError(AppException):
    """Erro de conexão com banco"""
    
    def __init__(self, message: str = "Não foi possível conectar ao banco de dados"):
        super().__init__(
            message=message,
            status_code=503,
            error_code="DATABASE_CONNECTION_ERROR"
        )


# === Exceções de Rate Limiting ===

class RateLimitExceededError(AppException):
    """Limite de requisições excedido"""
    
    def __init__(self, limit: int, window: str):
        super().__init__(
            message=f"Limite de requisições excedido. Máximo: {limit}/{window}",
            status_code=429,
            error_code="RATE_LIMIT_EXCEEDED",
            details={"limit": limit, "window": window}
        )


# === Exceções de Serviços Externos ===

class ExternalServiceError(AppException):
    """Erro em serviço externo"""
    
    def __init__(self, service: str, message: str):
        super().__init__(
            message=f"Erro no serviço {service}: {message}",
            status_code=502,
            error_code="EXTERNAL_SERVICE_ERROR",
            details={"service": service}
        )


class ServiceUnavailableError(AppException):
    """Serviço indisponível"""
    
    def __init__(self, service: str = None):
        super().__init__(
            message=f"Serviço {service or 'externo'} temporariamente indisponível",
            status_code=503,
            error_code="SERVICE_UNAVAILABLE",
            details={"service": service}
        )
