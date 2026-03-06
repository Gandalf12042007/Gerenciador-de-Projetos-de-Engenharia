"""
📧 SMTP Mailer - Envio de Emails via Gmail SMTP
Sistema de Gerenciamento de Projetos de Engenharia
Fase 4: Segurança - Recuperação de Senha

Este módulo implementa:
- Envio de emails via SMTP (Gmail)
- Templates HTML para recuperação de senha
- Fallback para modo desenvolvimento (log no console)

Desenvolvido por: Vicente de Souza
Data: Março 2026
"""

import smtplib
import ssl
import os
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURAÇÕES SMTP
# ═══════════════════════════════════════════════════════════════════════════════

class SMTPConfig:
    """Configurações do servidor SMTP"""
    
    # Gmail SMTP settings
    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER = os.getenv("SMTP_USER", "")  # Seu email Gmail
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")  # Senha de App do Gmail
    
    # Remetente
    FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL", SMTP_USER or "noreply@gerenciador-projetos.com")
    FROM_NAME = os.getenv("SMTP_FROM_NAME", "Gerenciador de Projetos")
    
    # URLs
    APP_URL = os.getenv("APP_URL", "http://localhost:5500")
    
    # Modo de desenvolvimento (não envia email, apenas loga)
    DEV_MODE = os.getenv("SMTP_DEV_MODE", "true").lower() == "true"


# ═══════════════════════════════════════════════════════════════════════════════
# TEMPLATES DE EMAIL HTML
# ═══════════════════════════════════════════════════════════════════════════════

def get_reset_password_template(
    nome_usuario: str,
    reset_link: str,
    token: str,
    expira_em: str
) -> str:
    """
    Template HTML para email de recuperação de senha
    Design profissional com a paleta do sistema
    """
    return f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Recuperação de Senha</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f5f7fa;
            margin: 0;
            padding: 20px;
            line-height: 1.6;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            background-color: #ffffff;
            border-radius: 16px;
            box-shadow: 0 4px 24px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #0B3D91 0%, #0F3057 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 28px;
            font-weight: 600;
        }}
        .header .icon {{
            font-size: 48px;
            margin-bottom: 15px;
        }}
        .content {{
            padding: 40px 30px;
        }}
        .greeting {{
            font-size: 18px;
            color: #1C1F26;
            margin-bottom: 20px;
        }}
        .message {{
            color: #4a5568;
            font-size: 15px;
            margin-bottom: 30px;
        }}
        .btn-container {{
            text-align: center;
            margin: 35px 0;
        }}
        .btn {{
            display: inline-block;
            background: linear-gradient(135deg, #1FAA59 0%, #159947 100%);
            color: white !important;
            text-decoration: none;
            padding: 16px 45px;
            border-radius: 30px;
            font-weight: 600;
            font-size: 16px;
            box-shadow: 0 4px 15px rgba(31, 170, 89, 0.4);
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        .btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(31, 170, 89, 0.5);
        }}
        .token-box {{
            background-color: #f8fafc;
            border: 2px dashed #e2e8f0;
            border-radius: 12px;
            padding: 20px;
            margin: 25px 0;
            text-align: center;
        }}
        .token-label {{
            color: #718096;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 10px;
        }}
        .token-value {{
            font-family: 'Courier New', monospace;
            font-size: 14px;
            color: #0B3D91;
            word-break: break-all;
            background: #edf2f7;
            padding: 10px;
            border-radius: 6px;
        }}
        .warning {{
            background-color: #fff8e6;
            border-left: 4px solid #f59e0b;
            padding: 15px 20px;
            margin: 25px 0;
            border-radius: 0 8px 8px 0;
            font-size: 14px;
            color: #92400e;
        }}
        .warning strong {{
            color: #b45309;
        }}
        .info-box {{
            background-color: #f0f9ff;
            border-left: 4px solid #0B3D91;
            padding: 15px 20px;
            margin: 25px 0;
            border-radius: 0 8px 8px 0;
        }}
        .info-row {{
            display: flex;
            margin: 8px 0;
            font-size: 14px;
        }}
        .info-label {{
            font-weight: 600;
            color: #0B3D91;
            min-width: 100px;
        }}
        .footer {{
            background-color: #1C1F26;
            padding: 30px;
            text-align: center;
            color: #9AA4B2;
            font-size: 13px;
        }}
        .footer a {{
            color: #1FAA59;
            text-decoration: none;
        }}
        .divider {{
            border: none;
            border-top: 1px solid #e2e8f0;
            margin: 25px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="icon">🔐</div>
            <h1>Recuperação de Senha</h1>
        </div>
        
        <div class="content">
            <p class="greeting">Olá, <strong>{nome_usuario}</strong>! 👋</p>
            
            <p class="message">
                Recebemos uma solicitação para redefinir a senha da sua conta no 
                <strong>Gerenciador de Projetos de Engenharia</strong>.
            </p>
            
            <div class="btn-container">
                <a href="{reset_link}" class="btn">
                    🔓 Redefinir Minha Senha
                </a>
            </div>
            
            <div class="token-box">
                <div class="token-label">Ou copie o token abaixo:</div>
                <div class="token-value">{token}</div>
            </div>
            
            <div class="info-box">
                <div class="info-row">
                    <span class="info-label">⏰ Expira em:</span>
                    <span>{expira_em}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">🌐 Link:</span>
                    <span style="word-break: break-all; font-size: 12px;">{reset_link}</span>
                </div>
            </div>
            
            <hr class="divider">
            
            <div class="warning">
                <strong>⚠️ Não solicitou este email?</strong><br>
                Se você não solicitou a recuperação de senha, ignore este email. 
                Sua conta permanece segura.
            </div>
            
            <p style="color: #718096; font-size: 13px; margin-top: 25px;">
                Por motivos de segurança, este link expira em <strong>1 hora</strong>.
                Após esse período, será necessário solicitar um novo link.
            </p>
        </div>
        
        <div class="footer">
            <p>📋 Gerenciador de Projetos de Engenharia</p>
            <p>Este é um email automático, não responda.</p>
            <p style="margin-top: 15px;">
                <a href="{SMTPConfig.APP_URL}">Acessar Sistema</a>
            </p>
        </div>
    </div>
</body>
</html>
"""


def get_plain_text_template(
    nome_usuario: str,
    reset_link: str,
    token: str,
    expira_em: str
) -> str:
    """Template texto simples para clientes de email que não suportam HTML"""
    return f"""
RECUPERAÇÃO DE SENHA - Gerenciador de Projetos de Engenharia
============================================================

Olá, {nome_usuario}!

Recebemos uma solicitação para redefinir a senha da sua conta.

LINK PARA REDEFINIR SENHA:
{reset_link}

TOKEN (se preferir copiar):
{token}

IMPORTANTE:
- Este link expira em: {expira_em}
- Se você não solicitou este email, ignore-o.
- Sua conta permanece segura.

============================================================
Este é um email automático, não responda.
"""


# ═══════════════════════════════════════════════════════════════════════════════
# FUNÇÕES DE ENVIO
# ═══════════════════════════════════════════════════════════════════════════════

def send_email_smtp(
    to_email: str,
    subject: str,
    html_content: str,
    plain_content: Optional[str] = None
) -> Dict[str, Any]:
    """
    Envia email via SMTP (Gmail)
    
    Args:
        to_email: Email do destinatário
        subject: Assunto do email
        html_content: Conteúdo HTML
        plain_content: Conteúdo texto (opcional)
        
    Returns:
        Dict com status do envio
    """
    # Modo desenvolvimento - apenas loga
    if SMTPConfig.DEV_MODE or not SMTPConfig.SMTP_USER:
        logger.info(f"📧 [DEV MODE] Email que seria enviado para: {to_email}")
        logger.info(f"📧 [DEV MODE] Assunto: {subject}")
        print(f"\n{'='*70}")
        print(f"📧 EMAIL (MODO DESENVOLVIMENTO)")
        print(f"{'='*70}")
        print(f"Para: {to_email}")
        print(f"Assunto: {subject}")
        print(f"{'='*70}")
        if plain_content:
            print(plain_content[:500] + "..." if len(plain_content) > 500 else plain_content)
        print(f"{'='*70}\n")
        
        return {
            "success": True,
            "dev_mode": True,
            "message": "Email logado (modo desenvolvimento)"
        }
    
    try:
        # Criar mensagem
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{SMTPConfig.FROM_NAME} <{SMTPConfig.FROM_EMAIL}>"
        msg["To"] = to_email
        
        # Adicionar versão texto
        if plain_content:
            part_plain = MIMEText(plain_content, "plain", "utf-8")
            msg.attach(part_plain)
        
        # Adicionar versão HTML
        part_html = MIMEText(html_content, "html", "utf-8")
        msg.attach(part_html)
        
        # Conectar e enviar
        context = ssl.create_default_context()
        
        with smtplib.SMTP(SMTPConfig.SMTP_SERVER, SMTPConfig.SMTP_PORT) as server:
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            server.login(SMTPConfig.SMTP_USER, SMTPConfig.SMTP_PASSWORD)
            server.sendmail(SMTPConfig.FROM_EMAIL, to_email, msg.as_string())
        
        logger.info(f"✅ Email enviado com sucesso para: {to_email}")
        
        return {
            "success": True,
            "message": "Email enviado com sucesso"
        }
        
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"❌ Erro de autenticação SMTP: {e}")
        return {
            "success": False,
            "error": "Erro de autenticação. Verifique SMTP_USER e SMTP_PASSWORD.",
            "details": str(e)
        }
    except smtplib.SMTPException as e:
        logger.error(f"❌ Erro SMTP: {e}")
        return {
            "success": False,
            "error": "Erro ao enviar email",
            "details": str(e)
        }
    except Exception as e:
        logger.error(f"❌ Erro inesperado ao enviar email: {e}")
        return {
            "success": False,
            "error": "Erro inesperado",
            "details": str(e)
        }


def send_password_reset_email(
    to_email: str,
    nome_usuario: str,
    token: str,
    reset_link: Optional[str] = None
) -> Dict[str, Any]:
    """
    Envia email de recuperação de senha
    
    Args:
        to_email: Email do usuário
        nome_usuario: Nome do usuário
        token: Token de reset
        reset_link: Link completo (opcional, será gerado se não fornecido)
        
    Returns:
        Dict com status do envio
    """
    # Gerar link se não fornecido
    if not reset_link:
        reset_link = f"{SMTPConfig.APP_URL}/web/reset-password.html?token={token}"
    
    # Calcular expiração (1 hora a partir de agora)
    from datetime import timedelta
    expira_em = (datetime.now() + timedelta(hours=1)).strftime("%d/%m/%Y às %H:%M")
    
    # Gerar templates
    html_content = get_reset_password_template(
        nome_usuario=nome_usuario,
        reset_link=reset_link,
        token=token,
        expira_em=expira_em
    )
    
    plain_content = get_plain_text_template(
        nome_usuario=nome_usuario,
        reset_link=reset_link,
        token=token,
        expira_em=expira_em
    )
    
    # Enviar
    return send_email_smtp(
        to_email=to_email,
        subject="🔐 Recuperação de Senha - Gerenciador de Projetos",
        html_content=html_content,
        plain_content=plain_content
    )


def send_password_changed_notification(
    to_email: str,
    nome_usuario: str
) -> Dict[str, Any]:
    """
    Envia notificação de que a senha foi alterada
    
    Args:
        to_email: Email do usuário
        nome_usuario: Nome do usuário
        
    Returns:
        Dict com status do envio
    """
    html_content = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: 'Segoe UI', sans-serif; background: #f5f7fa; margin: 0; padding: 20px; }}
        .container {{ max-width: 600px; margin: 0 auto; background: #fff; border-radius: 16px; box-shadow: 0 4px 24px rgba(0,0,0,0.1); overflow: hidden; }}
        .header {{ background: linear-gradient(135deg, #1FAA59 0%, #159947 100%); color: white; padding: 30px; text-align: center; }}
        .content {{ padding: 30px; }}
        .footer {{ background: #1C1F26; padding: 20px; text-align: center; color: #9AA4B2; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>✅ Senha Alterada</h1>
        </div>
        <div class="content">
            <p>Olá, <strong>{nome_usuario}</strong>!</p>
            <p>Sua senha foi alterada com sucesso em {datetime.now().strftime("%d/%m/%Y às %H:%M")}.</p>
            <p style="color: #e53e3e; background: #fff5f5; padding: 15px; border-radius: 8px;">
                <strong>⚠️ Não foi você?</strong><br>
                Entre em contato imediatamente com o suporte.
            </p>
        </div>
        <div class="footer">
            Gerenciador de Projetos de Engenharia
        </div>
    </div>
</body>
</html>
"""
    
    plain_content = f"""
SENHA ALTERADA - Gerenciador de Projetos
========================================

Olá, {nome_usuario}!

Sua senha foi alterada com sucesso em {datetime.now().strftime("%d/%m/%Y às %H:%M")}.

Se não foi você quem alterou, entre em contato imediatamente com o suporte.
"""
    
    return send_email_smtp(
        to_email=to_email,
        subject="✅ Senha Alterada - Gerenciador de Projetos",
        html_content=html_content,
        plain_content=plain_content
    )


# ═══════════════════════════════════════════════════════════════════════════════
# VERIFICAÇÃO DE CONFIGURAÇÃO
# ═══════════════════════════════════════════════════════════════════════════════

def check_smtp_config() -> Dict[str, Any]:
    """
    Verifica se as configurações SMTP estão corretas
    
    Returns:
        Dict com status da configuração
    """
    return {
        "configured": bool(SMTPConfig.SMTP_USER and SMTPConfig.SMTP_PASSWORD),
        "dev_mode": SMTPConfig.DEV_MODE,
        "smtp_server": SMTPConfig.SMTP_SERVER,
        "smtp_port": SMTPConfig.SMTP_PORT,
        "from_email": SMTPConfig.FROM_EMAIL,
        "from_name": SMTPConfig.FROM_NAME,
        "app_url": SMTPConfig.APP_URL,
        "user_configured": bool(SMTPConfig.SMTP_USER),
        "password_configured": bool(SMTPConfig.SMTP_PASSWORD)
    }


# ═══════════════════════════════════════════════════════════════════════════════
# INSTRUÇÕES DE CONFIGURAÇÃO (para documentação)
# ═══════════════════════════════════════════════════════════════════════════════

SETUP_INSTRUCTIONS = """
📧 CONFIGURAÇÃO DO SMTP (Gmail)
===============================

Para enviar emails reais, configure as seguintes variáveis de ambiente:

1. SMTP_USER - Seu email do Gmail (ex: seuemail@gmail.com)
2. SMTP_PASSWORD - Senha de App do Gmail (não a senha normal!)
3. SMTP_DEV_MODE - "false" para modo produção

COMO CRIAR SENHA DE APP DO GMAIL:
---------------------------------
1. Acesse: https://myaccount.google.com/security
2. Ative a verificação em duas etapas
3. Vá em "Senhas de app"
4. Selecione "Outro" e dê um nome (ex: "Gerenciador Projetos")
5. Copie a senha gerada de 16 caracteres

VARIÁVEIS OPCIONAIS:
-------------------
- SMTP_SERVER (padrão: smtp.gmail.com)
- SMTP_PORT (padrão: 587)
- SMTP_FROM_EMAIL (padrão: SMTP_USER)
- SMTP_FROM_NAME (padrão: "Gerenciador de Projetos")
- APP_URL (padrão: http://localhost:5500)

EXEMPLO DE .env:
---------------
SMTP_USER=seuemail@gmail.com
SMTP_PASSWORD=abcd efgh ijkl mnop
SMTP_DEV_MODE=false
APP_URL=http://localhost:5500
"""

if __name__ == "__main__":
    print(SETUP_INSTRUCTIONS)
    print("\n📊 Status atual da configuração:")
    config = check_smtp_config()
    for key, value in config.items():
        print(f"  {key}: {value}")
