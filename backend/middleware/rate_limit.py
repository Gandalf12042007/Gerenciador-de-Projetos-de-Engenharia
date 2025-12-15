"""
Rate Limiting Middleware - Proteção contra brute force
Desenvolvido por: Vicente de Souza
"""

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

# Criar limiter com chave baseada no IP
limiter = Limiter(key_func=get_remote_address)


async def rate_limit_exception_handler(request: Request, exc: RateLimitExceeded):
    """
    Handler customizado para exceções de rate limit
    """
    logger.warning(f"Rate limit excedido para IP: {get_remote_address(request)}")
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={
            "detail": "Muitas requisições. Tente novamente em alguns minutos.",
            "retry_after": exc.retry_after
        }
    )


# Decoradores pré-configurados para uso nas rotas
class RateLimitDecorators:
    """Decoradores de rate limit pré-configurados"""
    
    # Auth - proteção contra brute force
    login = limiter.limit("5/minute")  # Máx 5 tentativas/min
    register = limiter.limit("10/hour")  # Máx 10 registros/hora
    
    # APIs gerais - proteção contra DoS
    standard = limiter.limit("100/minute")  # Máx 100 req/min
    strict = limiter.limit("50/minute")  # Máx 50 req/min
    
    # Operações custosas
    upload = limiter.limit("10/hour")  # Máx 10 uploads/hora
    delete = limiter.limit("20/hour")  # Máx 20 deletes/hora
