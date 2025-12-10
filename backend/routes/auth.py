"""
Rotas de Autenticação - Login e Registro
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from datetime import timedelta
import sys
import os
import re
import logging

# Adicionar path do database
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'database'))
from db_helper import DatabaseHelper

from utils.auth import hash_password, verify_password, create_access_token
from config import settings

# Logger para auditoria de segurança
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Autenticação"])


# Schemas
class LoginRequest(BaseModel):
    email: EmailStr
    senha: str


class RegisterRequest(BaseModel):
    nome: str = Field(..., min_length=3, max_length=255, description="Nome completo (mín. 3 caracteres)")
    email: EmailStr = Field(..., description="Email válido e único")
    senha: str = Field(..., min_length=8, max_length=255, description="Senha com mín. 8 caracteres, 1 maiúscula, 1 número")
    telefone: str = Field(None, max_length=20, description="Telefone opcional")
    cargo: str = Field(None, max_length=50, description="Cargo/função")
    
    @staticmethod
    def validate_password(senha: str) -> bool:
        """Valida força da senha: mín 8 chars, 1 maiúscula, 1 número"""
        if len(senha) < 8:
            return False
        if not re.search(r'[A-Z]', senha):  # Pelo menos 1 maiúscula
            return False
        if not re.search(r'[0-9]', senha):  # Pelo menos 1 número
            return False
        return True


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
    
    # Verificar senha (usuario[3] é a senha_hash)
    if not verify_password(credentials.senha, usuario[3]):
        # Log de tentativa falha (auditoria)
        logger.warning(f"Tentativa de login falhou para email: {credentials.email}")
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
    Registro de novo usuário com validações de segurança
    
    Returns:
        Mensagem de sucesso
        
    Raises:
        HTTPException: Email já existe, senha fraca, erro ao inserir
    """
    db = DatabaseHelper()
    
    # Validar força da senha
    if not RegisterRequest.validate_password(user_data.senha):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Senha fraca. Requisitos: mín. 8 caracteres, 1 maiúscula, 1 número"
        )
    
    # Validar nome (mínimo 3 caracteres)
    if len(user_data.nome.strip()) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nome deve ter no mínimo 3 caracteres"
        )
    
    # Verificar se email já existe (sem expor detalhes)
    try:
        existing = db.execute_query(
            "SELECT id FROM usuarios WHERE email = %s",
            (user_data.email,),
            fetch=True
        )
        
        if existing and len(existing) > 0:
            # Log para auditoria
            logger.warning(f"Tentativa de registro com email já existente: {user_data.email}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email já cadastrado no sistema"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao verificar email único: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao validar email"
        )
    
    # Hash da senha (bcrypt com salt rounds automático)
    try:
        senha_hash = hash_password(user_data.senha)
    except Exception as e:
        logger.error(f"Erro ao gerar hash de senha: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao processar senha"
        )
    
    # Inserir usuário com tratamento específico de erros
    try:
        db.execute_query(
            """
            INSERT INTO usuarios (nome, email, senha_hash, telefone, cargo, ativo, data_criacao)
            VALUES (%s, %s, %s, %s, %s, TRUE, NOW())
            """,
            (user_data.nome.strip(), user_data.email.lower(), senha_hash, user_data.telefone, user_data.cargo)
        )
        
        logger.info(f"Novo usuário registrado: {user_data.email}")
        return {"message": "Usuário cadastrado com sucesso. Você pode fazer login agora."}
    
    except Exception as e:
        # Não expor detalhes de erro ao cliente (segurança)
        logger.error(f"Erro ao cadastrar usuário {user_data.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao cadastrar usuário. Tente novamente mais tarde."
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
