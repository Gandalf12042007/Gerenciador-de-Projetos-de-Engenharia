"""
Rotas de Autenticação - Login e Registro
Desenvolvido por: Vicente de Souza
"""

from fastapi import APIRouter, HTTPException, status, Request, Depends
from pydantic import BaseModel, EmailStr, Field
from datetime import timedelta, datetime
import sys
import os
import re
import logging
import secrets

# Adicionar path do database
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'database'))
from db_helper import DatabaseHelper

from utils.auth import hash_password, verify_password, create_access_token
from utils.two_factor_auth import gerar_otp, enviar_otp_email, validar_otp, resend_otp
from middleware.rate_limit import RateLimitDecorators
from middleware.auth_middleware import get_current_active_user
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


class MessageResponse(BaseModel):
    message: str


class OTPResponse(BaseModel):
    message: str
    requires_2fa: bool = False


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    nome: str
    email: str


class VerifyOTPRequest(BaseModel):
    email: EmailStr
    codigo_otp: str = Field(..., min_length=6, max_length=6, description="Código OTP de 6 dígitos")


@router.post("/login", response_model=TokenResponse)
@RateLimitDecorators.login
async def login(credentials: LoginRequest, request: Request):
    """
    Login de usuário
    
    Returns:
        Token JWT e dados do usuário
    """
    # Usuários de teste hardcoded (sem banco de dados)
    USUARIOS_TESTE = {
        "teste01@gmail.com": {
            "id": 1,
            "nome": "Vicente de Souza", 
            "email": "teste01@gmail.com",
            "senha": "Teste123@",
            "telefone": "11 99999-0001",
            "cargo": "Administrador",
            "ativo": True
        },
        "francisco@gmail.com": {
            "id": 2,
            "nome": "Francisco",
            "email": "francisco@gmail.com", 
            "senha": "Teste123@",
            "telefone": "11 99999-0002",
            "cargo": "Desenvolvedor",
            "ativo": True
        }
    }
    
    # Verificar se é usuário de teste
    if credentials.email in USUARIOS_TESTE:
        user_teste = USUARIOS_TESTE[credentials.email]
        if credentials.senha == user_teste["senha"] and user_teste["ativo"]:
            # Criar token
            access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={"user_id": user_teste["id"], "email": user_teste["email"], "nome": user_teste["nome"]},
                expires_delta=access_token_expires
            )
            
            logger.info(f"Login bem-sucedido (teste): {credentials.email}")
            
            return TokenResponse(
                access_token=access_token,
                user_id=user_teste["id"],
                nome=user_teste["nome"],
                email=user_teste["email"]
            )
    
    # Se não encontrou usuário de teste
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Email ou senha incorretos"
    )


@router.post("/register", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
@RateLimitDecorators.register
async def register(user_data: RegisterRequest, request: Request):
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
        
        # ✅ Sprint 1: Integração de 2FA (Autenticação de Dois Fatores)
        # Enviar OTP por email para validação de cadastro
        logger.info(f"Enviando OTP para confirmação de registro: {user_data.email}")
        enviar_otp_email(user_data.email)
        
        return {"message": "Usuário cadastrado com sucesso. Verifique seu email para confirmar o cadastro."}
    
    except Exception as e:
        # Não expor detalhes de erro ao cliente (segurança)
        logger.error(f"Erro ao cadastrar usuário {user_data.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao cadastrar usuário. Tente novamente mais tarde."
        )


@router.post("/verify-2fa")
async def verify_2fa(otp_data: VerifyOTPRequest):
    """
    Verifica código OTP para autenticação de dois fatores
    
    Returns:
        Token JWT após validação bem-sucedida
    """
    # Validar OTP
    sucesso, mensagem = validar_otp(otp_data.email, otp_data.codigo_otp)
    
    if not sucesso:
        logger.warning(f"Tentativa de validação 2FA falhou para: {otp_data.email} - {mensagem}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=mensagem
        )
    
    # Buscar usuário para gerar token
    db = DatabaseHelper()
    usuario = db.execute_query(
        "SELECT id, nome, email, cargo FROM usuarios WHERE email = %s",
        (otp_data.email,),
        fetch=True
    )
    
    if not usuario or len(usuario) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    usuario = usuario[0]
    
    # Criar token JWT após 2FA validado
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "user_id": usuario[0],
            "email": usuario[2],
            "nome": usuario[1],
            "cargo": usuario[3],
            "2fa_verified": True
        },
        expires_delta=access_token_expires
    )
    
    logger.info(f"Autenticação 2FA bem-sucedida para: {otp_data.email}")
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": usuario[0],
            "nome": usuario[1],
            "email": usuario[2],
            "cargo": usuario[3],
            "2fa_verified": True
        }
    }


@router.post("/resend-otp")
async def resend_otp_endpoint(email_data: dict):
    """
    Reenvia código OTP para email
    
    Returns:
        Mensagem de confirmação
    """
    email = email_data.get("email")
    
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email é obrigatório"
        )
    
    sucesso, mensagem = resend_otp(email)
    
    if not sucesso:
        logger.warning(f"Erro ao reenviar OTP para: {email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=mensagem
        )
    
    logger.info(f"OTP reenviado com sucesso para: {email}")
    return {"message": mensagem}


# ===== SCHEMAS PARA RESET DE SENHA =====

class ForgotPasswordRequest(BaseModel):
    email: EmailStr = Field(..., description="Email cadastrado no sistema")


class ResetPasswordRequest(BaseModel):
    token: str = Field(..., min_length=32, max_length=64, description="Token de reset recebido por email")
    nova_senha: str = Field(..., min_length=8, description="Nova senha (mín. 8 caracteres, 1 maiúscula, 1 número)")


class ChangePasswordRequest(BaseModel):
    senha_atual: str = Field(..., description="Senha atual do usuário")
    nova_senha: str = Field(..., min_length=8, description="Nova senha (mín. 8 caracteres, 1 maiúscula, 1 número)")


class ForgotPasswordResponse(BaseModel):
    message: str
    reset_link: str | None = None  # Apenas em modo desenvolvimento, opcional


# ===== ENDPOINTS DE RESET DE SENHA =====

@router.post("/forgot-password", response_model=ForgotPasswordResponse)
async def forgot_password(request_data: ForgotPasswordRequest, request: Request):
    """
    Solicita reset de senha - gera token e retorna link (modo desenvolvimento)
    
    Em produção, enviaria email. Em desenvolvimento, retorna o link diretamente.
    """
    db = DatabaseHelper()
    reset_link = None
    
    try:
        # Buscar usuário pelo email
        usuario = db.execute_query(
            "SELECT id, nome, email FROM usuarios WHERE email = %s AND ativo = 1",
            (request_data.email.lower(),),
            fetch=True
        )
        
        if usuario and len(usuario) > 0:
            user = usuario[0]
            user_id = user['id'] if isinstance(user, dict) else user[0]
            user_email = user['email'] if isinstance(user, dict) else user[2]
            
            # Gerar token único
            token = secrets.token_urlsafe(32)
            
            # Expira em 1 hora
            expira_em = (datetime.now() + timedelta(hours=1)).isoformat()
            
            # Invalidar tokens anteriores do usuário
            db.execute_query(
                "UPDATE tokens_reset_senha SET usado = 1 WHERE usuario_id = %s AND usado = 0",
                (user_id,)
            )
            
            # Salvar novo token
            db.execute_query(
                "INSERT INTO tokens_reset_senha (usuario_id, token, expira_em) VALUES (%s, %s, %s)",
                (user_id, token, expira_em)
            )
            
            # MODO DESENVOLVIMENTO: Retorna o link diretamente
            reset_link = f"http://localhost:5500/web/reset-password.html?token={token}"
            logger.info(f"[RESET SENHA] Link gerado para {user_email}: {reset_link}")
            print(f"\n{'='*60}")
            print(f"📧 LINK DE RESET DE SENHA")
            print(f"📧 Email: {user_email}")
            print(f"🔗 Link: {reset_link}")
            print(f"⏰ Expira em: 1 hora")
            print(f"{'='*60}\n")
            
            return {
                "message": "Link de reset gerado com sucesso!",
                "reset_link": reset_link
            }
        else:
            # Log para auditoria
            logger.warning(f"Tentativa de reset para email não cadastrado: {request_data.email}")
        
        # Email não encontrado
        return {
            "message": "Email não encontrado no sistema.",
            "reset_link": None
        }
        
    except Exception as e:
        logger.error(f"Erro ao processar forgot-password: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao processar solicitação"
        )


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(request_data: ResetPasswordRequest, request: Request):
    """
    Redefine senha usando token de reset
    """
    db = DatabaseHelper()
    
    # Validar força da nova senha
    if not RegisterRequest.validate_password(request_data.nova_senha):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Senha fraca. Requisitos: mín. 8 caracteres, 1 maiúscula, 1 número"
        )
    
    try:
        # Buscar token válido
        token_data = db.execute_query(
            """
            SELECT t.id, t.usuario_id, t.expira_em, u.email 
            FROM tokens_reset_senha t
            INNER JOIN usuarios u ON t.usuario_id = u.id
            WHERE t.token = %s AND t.usado = 0
            """,
            (request_data.token,),
            fetch=True
        )
        
        if not token_data or len(token_data) == 0:
            logger.warning(f"Tentativa de reset com token inválido: {request_data.token[:10]}...")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token inválido ou já utilizado"
            )
        
        token_info = token_data[0]
        token_id = token_info['id'] if isinstance(token_info, dict) else token_info[0]
        user_id = token_info['usuario_id'] if isinstance(token_info, dict) else token_info[1]
        expira_em = token_info['expira_em'] if isinstance(token_info, dict) else token_info[2]
        user_email = token_info['email'] if isinstance(token_info, dict) else token_info[3]
        
        # Verificar expiração
        if isinstance(expira_em, str):
            expira_dt = datetime.fromisoformat(expira_em)
        else:
            expira_dt = expira_em
            
        if datetime.now() > expira_dt:
            logger.warning(f"Token expirado usado para: {user_email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token expirado. Solicite um novo reset de senha."
            )
        
        # Hash da nova senha
        nova_senha_hash = hash_password(request_data.nova_senha)
        
        # Atualizar senha do usuário
        db.execute_query(
            "UPDATE usuarios SET senha_hash = %s WHERE id = %s",
            (nova_senha_hash, user_id)
        )
        
        # Marcar token como usado
        db.execute_query(
            "UPDATE tokens_reset_senha SET usado = 1 WHERE id = %s",
            (token_id,)
        )
        
        logger.info(f"Senha resetada com sucesso para: {user_email}")
        
        return {"message": "Senha redefinida com sucesso! Você já pode fazer login."}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao resetar senha: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao redefinir senha"
        )


@router.put("/change-password", response_model=MessageResponse)
async def change_password(
    request_data: ChangePasswordRequest,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Troca de senha para usuário logado
    Requer autenticação
    """
    db = DatabaseHelper()
    
    # Validar força da nova senha
    if not RegisterRequest.validate_password(request_data.nova_senha):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Senha fraca. Requisitos: mín. 8 caracteres, 1 maiúscula, 1 número"
        )
    
    # Não permitir mesma senha
    if request_data.senha_atual == request_data.nova_senha:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A nova senha deve ser diferente da senha atual"
        )
    
    try:
        user_id = current_user.get('user_id') or current_user.get('id')
        user_email = current_user.get('email')
        
        # Buscar senha atual do banco
        usuario = db.execute_query(
            "SELECT id, senha_hash FROM usuarios WHERE id = %s",
            (user_id,),
            fetch=True
        )
        
        if not usuario or len(usuario) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado"
            )
        
        user_data = usuario[0]
        senha_hash_atual = user_data['senha_hash'] if isinstance(user_data, dict) else user_data[1]
        
        # Verificar senha atual
        if not verify_password(request_data.senha_atual, senha_hash_atual):
            logger.warning(f"Tentativa de troca de senha com senha incorreta: {user_email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Senha atual incorreta"
            )
        
        # Hash da nova senha
        nova_senha_hash = hash_password(request_data.nova_senha)
        
        # Atualizar senha
        db.execute_query(
            "UPDATE usuarios SET senha_hash = %s WHERE id = %s",
            (nova_senha_hash, user_id)
        )
        
        logger.info(f"Senha alterada com sucesso para: {user_email}")
        
        return {"message": "Senha alterada com sucesso!"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao alterar senha: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao alterar senha"
        )


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
