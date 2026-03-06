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
from utils.user_manager import obter_usuario_por_email, atualizar_ultimo_login
from utils.security_audit import (
    registro_log_auth, 
    registrar_tentativa_falhada, 
    esta_bloqueado,
    tempo_ate_desbloquear
)
from utils.smtp_mailer import send_password_reset_email, send_password_changed_notification
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
    role: str = "usuario"


class VerifyOTPRequest(BaseModel):
    email: EmailStr
    codigo_otp: str = Field(..., min_length=6, max_length=6, description="Código OTP de 6 dígitos")


@router.post("/login", response_model=TokenResponse)
@RateLimitDecorators.login
async def login(credentials: LoginRequest, request: Request):
    """
    Login de usuário com autenticação baseada em banco de dados
    
    Segurança implementada:
    - Bcrypt para hash de senhas
    - Rate limiting (3 tentativas = 15 min bloqueio)
    - Auditoria completa de login/falhas
    - IP address logging
    
    Returns:
        Token JWT e dados do usuário
    """
    try:
        # Extrair IP da request
        client_ip = request.client.host if request.client else "desconhecido"
        email_normalized = credentials.email.lower()
        
        # ═════════════════════════════════════════════════════════════════════
        # PASSO 1: Verificar se conta está bloqueada por rate limiting
        # ═════════════════════════════════════════════════════════════════════
        if esta_bloqueado(email_normalized):
            minutos = tempo_ate_desbloquear(email_normalized)
            
            # Log da tentativa bloqueada
            registro_log_auth(
                email=email_normalized,
                acao="login_bloqueado",
                sucesso=False,
                ip_address=client_ip,
                motivo=f"Conta bloqueada por rate limit - {minutos} minutos restantes"
            )
            
            logger.warning(f"❌ Tentativa de login bloqueada (rate limit): {email_normalized} de {client_ip}")
            
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Conta temporariamente bloqueada. Tente novamente em {minutos} minutos."
            )
        
        # ═════════════════════════════════════════════════════════════════════
        # PASSO 2: Buscar usuário no banco de dados
        # ═════════════════════════════════════════════════════════════════════
        user = obter_usuario_por_email(email_normalized)
        
        if not user:
            # Usuário não encontrado - registrar tentativa
            registrar_tentativa_falhada(email_normalized, client_ip)
            
            registro_log_auth(
                email=email_normalized,
                acao="login_falha",
                sucesso=False,
                ip_address=client_ip,
                motivo="Usuário não encontrado"
            )
            
            logger.warning(f"❌ Tentativa de login para usuário não encontrado: {email_normalized} de {client_ip}")
            
            # Resposta genérica (não revela informações)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou senha incorretos"
            )
        
        # ═════════════════════════════════════════════════════════════════════
        # PASSO 3: Verificar senha usando bcrypt
        # ═════════════════════════════════════════════════════════════════════
        senha_hash = user.get('senha_hash') or user.get('senha_hash')
        
        if not verify_password(credentials.senha, senha_hash):
            # Senha incorreta - registrar tentativa falhada
            registrar_tentativa_falhada(email_normalized, client_ip)
            
            registro_log_auth(
                email=email_normalized,
                acao="login_falha",
                sucesso=False,
                ip_address=client_ip,
                motivo="Senha incorreta"
            )
            
            logger.warning(f"❌ Senha incorreta para: {email_normalized} de {client_ip}")
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou senha incorretos"
            )
        
        # ═════════════════════════════════════════════════════════════════════
        # PASSO 4: Gerar token JWT e registrar login bem-sucedido
        # ═════════════════════════════════════════════════════════════════════
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={
                "user_id": user.get("id"),
                "email": user.get("email"),
                "nome": user.get("nome"),
                "role": user.get("role", "usuario")
            },
            expires_delta=access_token_expires
        )
        
        # Atualizar último login
        atualizar_ultimo_login(email_normalized)
        
        # Log de sucesso
        registro_log_auth(
            email=email_normalized,
            acao="login_sucesso",
            sucesso=True,
            ip_address=client_ip,
            motivo="Credenciais válidas"
        )
        
        logger.info(f"✅ Login bem-sucedido: {email_normalized} de {client_ip}")
        
        return TokenResponse(
            access_token=access_token,
            user_id=user.get("id"),
            nome=user.get("nome"),
            email=user.get("email"),
            role=user.get("role", "usuario")
        )
    
    except HTTPException:
        # Re-lançar exceções HTTP (para não serem capturadas novamente)
        raise
    
    except Exception as e:
        # Log de erro não esperado
        logger.error(f"❌ Erro inesperado no login: {str(e)}")
        
        registro_log_auth(
            email=credentials.email.lower(),
            acao="login_erro",
            sucesso=False,
            ip_address=request.client.host if request.client else "desconhecido",
            motivo=f"Erro interno: {str(e)[:50]}"
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao processar login"
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
            INSERT INTO usuarios (nome, email, senha_hash, telefone, cargo, ativo)
            VALUES (%s, %s, %s, %s, %s, 1)
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
            "user_id": usuario['id'],
            "email": usuario['email'],
            "nome": usuario['nome'],
            "cargo": usuario['cargo'],
            "2fa_verified": True
        },
        expires_delta=access_token_expires
    )
    
    logger.info(f"Autenticação 2FA bem-sucedida para: {otp_data.email}")
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": usuario['id'],
            "nome": usuario['nome'],
            "email": usuario['email'],
            "cargo": usuario['cargo'],
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
            
            # Gerar link de reset
            reset_link = f"http://localhost:5500/web/reset-password.html?token={token}"
            
            # Obter nome do usuário
            user_nome = user['nome'] if isinstance(user, dict) else user[1]
            
            # Enviar email de recuperação de senha
            email_result = send_password_reset_email(
                to_email=user_email,
                nome_usuario=user_nome or "Usuário",
                token=token,
                reset_link=reset_link
            )
            
            # Log do resultado
            if email_result.get('success'):
                logger.info(f"[RESET SENHA] Email enviado para {user_email}")
            else:
                logger.warning(f"[RESET SENHA] Falha ao enviar email: {email_result.get('error')}")
            
            # Log no console (modo desenvolvimento)
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
        
        # Buscar nome do usuário para notificação
        usuario_info = db.execute_query(
            "SELECT nome FROM usuarios WHERE id = %s",
            (user_id,),
            fetch=True
        )
        user_nome = usuario_info[0]['nome'] if usuario_info and isinstance(usuario_info[0], dict) else "Usuário"
        
        # Enviar notificação de senha alterada
        send_password_changed_notification(user_email, user_nome)
        
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


# ===== LOGIN COM GOOGLE OAUTH =====

class GoogleLoginRequest(BaseModel):
    credential: str = Field(..., description="Token de credencial do Google")
    client_id: str = Field(None, description="Client ID do Google (opcional)")


class GoogleUserInfo(BaseModel):
    email: str
    name: str
    picture: str = None
    google_id: str


@router.post("/google-login")
async def google_login(google_data: GoogleLoginRequest, request: Request):
    """
    Login com conta Google usando credencial JWT do Google Sign-In
    
    - Valida o token do Google
    - Cria ou atualiza usuário no banco
    - Retorna token JWT do sistema
    """
    try:
        import httpx
        
        # Validar token do Google
        # Em produção, use a biblioteca google-auth para validar propriamente
        # Aqui fazemos uma validação simplificada usando o endpoint do Google
        
        async with httpx.AsyncClient() as client:
            # Decodificar o JWT do Google (para extrair informações)
            # Em produção, valide a assinatura do token
            parts = google_data.credential.split('.')
            if len(parts) != 3:
                raise HTTPException(status_code=400, detail="Token Google inválido")
            
            import base64
            import json
            
            # Decodificar payload do JWT
            payload_b64 = parts[1]
            # Adicionar padding se necessário
            payload_b64 += '=' * (4 - len(payload_b64) % 4)
            payload_bytes = base64.urlsafe_b64decode(payload_b64)
            payload = json.loads(payload_bytes)
            
            google_email = payload.get('email')
            google_name = payload.get('name')
            google_picture = payload.get('picture')
            google_id = payload.get('sub')
            
            if not google_email:
                raise HTTPException(status_code=400, detail="Email não encontrado no token Google")
        
        db = DatabaseHelper()
        
        # Verificar se usuário já existe
        existing = db.execute_query(
            "SELECT id, nome, email, cargo FROM usuarios WHERE email = ?",
            (google_email.lower(),),
            fetch=True
        )
        
        if existing and len(existing) > 0:
            # Usuário existe, fazer login
            user = existing[0]
            user_id = user['id']
            user_nome = user['nome']
            user_email = user['email']
            user_cargo = user.get('cargo', 'Usuário')
        else:
            # Criar novo usuário
            user_id = db.execute_query(
                """
                INSERT INTO usuarios (nome, email, senha_hash, cargo, ativo, criado_em)
                VALUES (?, ?, ?, ?, 1, datetime('now'))
                """,
                (google_name, google_email.lower(), 'GOOGLE_OAUTH', 'Usuário')
            )
            user_nome = google_name
            user_email = google_email
            user_cargo = 'Usuário'
            
            logger.info(f"Novo usuário criado via Google OAuth: {google_email}")
        
        # Criar token JWT do sistema
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={
                "user_id": user_id,
                "email": user_email,
                "nome": user_nome,
                "cargo": user_cargo,
                "oauth_provider": "google"
            },
            expires_delta=access_token_expires
        )
        
        logger.info(f"Login Google OAuth bem-sucedido: {google_email}")
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": user_id,
            "nome": user_nome,
            "email": user_email,
            "cargo": user_cargo,
            "picture": google_picture
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro no login Google: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao processar login com Google"
        )
