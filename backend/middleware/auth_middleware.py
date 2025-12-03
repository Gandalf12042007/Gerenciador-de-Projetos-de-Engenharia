"""
Middleware de Autenticação JWT
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from utils.auth import decode_access_token

security = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Extrai e valida usuário do token JWT
    
    Args:
        credentials: Credenciais HTTP Bearer
        
    Returns:
        Dados do usuário
        
    Raises:
        HTTPException: Se token inválido ou expirado
    """
    token = credentials.credentials
    
    payload = decode_access_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id: Optional[int] = payload.get("user_id")
    email: Optional[str] = payload.get("email")
    
    if user_id is None or email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return {
        "user_id": user_id,
        "email": email,
        "nome": payload.get("nome"),
        "cargo": payload.get("cargo")
    }


async def get_current_active_user(current_user: dict = Depends(get_current_user)) -> dict:
    """
    Verifica se usuário está ativo
    
    Args:
        current_user: Usuário do token
        
    Returns:
        Dados do usuário ativo
    """
    # Aqui poderia adicionar verificação adicional no banco se necessário
    return current_user
