"""
Exception Handler - Tratamento global de exceções FastAPI
"""

import logging
import traceback
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

from utils.exceptions import AppException

logger = logging.getLogger(__name__)


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """
    Handler para exceções customizadas da aplicação
    """
    logger.error(
        f"AppException: {exc.error_code} - {exc.message}",
        extra={
            "status_code": exc.status_code,
            "path": request.url.path,
            "method": request.method,
            "details": exc.details
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_dict()
    )


async def validation_exception_handler(
    request: Request, 
    exc: RequestValidationError
) -> JSONResponse:
    """
    Handler para erros de validação do Pydantic
    """
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        errors.append({
            "field": field,
            "message": error["msg"],
            "type": error["type"]
        })
    
    logger.warning(
        f"Validation Error: {request.url.path}",
        extra={"errors": errors}
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": True,
            "message": "Erro de validação nos dados enviados",
            "error_code": "VALIDATION_ERROR",
            "status_code": 422,
            "details": {"errors": errors}
        }
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handler genérico para exceções não tratadas
    """
    # Log completo do erro
    logger.exception(
        f"Unhandled Exception: {type(exc).__name__} - {str(exc)}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "traceback": traceback.format_exc()
        }
    )
    
    # Em produção, não expor detalhes internos
    import os
    is_debug = os.getenv("DEBUG", "False").lower() == "true"
    
    if is_debug:
        message = f"Erro interno: {str(exc)}"
        details = {"traceback": traceback.format_exc()}
    else:
        message = "Ocorreu um erro interno. Por favor, tente novamente."
        details = {}
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": True,
            "message": message,
            "error_code": "INTERNAL_SERVER_ERROR",
            "status_code": 500,
            "details": details
        }
    )


async def http_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handler para HTTPException do FastAPI
    """
    from fastapi import HTTPException
    
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": True,
                "message": exc.detail,
                "error_code": f"HTTP_{exc.status_code}",
                "status_code": exc.status_code,
                "details": {}
            }
        )
    
    return await generic_exception_handler(request, exc)


def register_exception_handlers(app):
    """
    Registra todos os handlers de exceção na aplicação
    """
    from fastapi import HTTPException
    
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
    
    logger.info("Exception handlers registered")
