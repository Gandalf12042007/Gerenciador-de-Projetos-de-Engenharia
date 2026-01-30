"""
Utilitários de Autenticação - JWT e Hash de Senhas
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from config import settings


def hash_password(password: str) -> str:
    """
    Gera hash bcrypt da senha
    
    Args:
        password: Senha em texto puro
        
    Returns:
        Hash da senha
    """
    # Garantir que senha não exceda 72 bytes
    password_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica se senha corresponde ao hash
    
    Args:
        plain_password: Senha em texto puro
        hashed_password: Hash armazenado
        
    Returns:
        True se senha correta
    """
    try:
        password_bytes = plain_password.encode('utf-8')[:72]
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception:
        return False


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Cria token JWT
    
    Args:
        data: Dados a serem codificados no token
        expires_delta: Tempo de expiração customizado
        
    Returns:
        Token JWT assinado
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decodifica e valida token JWT
    
    Args:
        token: Token JWT
        
    Returns:
        Dados do token ou None se inválido
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None
