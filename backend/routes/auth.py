"""
Rotas de Autenticação - Login e Registro
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
from datetime import timedelta
import sys
import os

# Adicionar path do database
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'database'))
from db_helper import DatabaseHelper

from utils.auth import hash_password, verify_password, create_access_token
from config import settings

router = APIRouter(prefix="/auth", tags=["Autenticação"])


# Schemas
class LoginRequest(BaseModel):
    email: EmailStr
    senha: str


class RegisterRequest(BaseModel):
    nome: str
    email: EmailStr
    senha: str
    telefone: str = None
    cargo: str = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


class MessageResponse(BaseModel):
    message: str


@router.post("/login", response_model=TokenResponse)
async def login(credentials: LoginRequest):
    """
    Login de usuário
    
    Returns:
        Token JWT e dados do usuário
    """
    db = DatabaseHelper()
    
    # Buscar usuário por email
    usuario = db.execute_query(
        "SELECT id, nome, email, senha_hash, telefone, cargo, ativo FROM usuarios WHERE email = %s",
        (credentials.email,),
        fetch=True
    )
    
    if not usuario or len(usuario) == 0:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos"
        )
    
    usuario = usuario[0]
    
    # Verificar se usuário está ativo
    if not usuario[6]:  # ativo
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário desativado"
        )
    
    # Verificar senha
    if not verify_password(credentials.senha, usuario[2]):  # senha_hash
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos"
        )
    
    # Criar token JWT
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "user_id": usuario[0],
            "email": usuario[2],
            "nome": usuario[1],
            "cargo": usuario[5]
        },
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": usuario[0],
            "nome": usuario[1],
            "email": usuario[2],
            "telefone": usuario[4],
            "cargo": usuario[5]
        }
    }


@router.post("/register", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: RegisterRequest):
    """
    Registro de novo usuário
    
    Returns:
        Mensagem de sucesso
    """
    db = DatabaseHelper()
    
    # Verificar se email já existe
    existing = db.execute_query(
        "SELECT id FROM usuarios WHERE email = %s",
        (user_data.email,),
        fetch=True
    )
    
    if existing and len(existing) > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já cadastrado"
        )
    
    # Hash da senha
    senha_hash = hash_password(user_data.senha)
    
    # Inserir usuário
    try:
        db.execute_query(
            """
            INSERT INTO usuarios (nome, email, senha_hash, telefone, cargo, ativo)
            VALUES (%s, %s, %s, %s, %s, TRUE)
            """,
            (user_data.nome, user_data.email, senha_hash, user_data.telefone, user_data.cargo)
        )
        
        return {"message": "Usuário cadastrado com sucesso"}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao cadastrar usuário: {str(e)}"
        )


@router.post("/validate-token")
async def validate_token(token: str):
    """
    Valida se token JWT é válido
    
    Returns:
        Status da validação
    """
    from utils.auth import decode_access_token
    
    payload = decode_access_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado"
        )
    
    return {"valid": True, "user_id": payload.get("user_id")}
