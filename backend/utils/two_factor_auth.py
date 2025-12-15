"""
2FA via Email - Autenticação de Dois Fatores
Desenvolvido por: Vicente de Souza
"""

import random
import string
from datetime import datetime, timedelta
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Simulação de banco de dados para OTP (em produção, usar Redis)
# Formato: {email: {"code": "123456", "expires": datetime, "attempts": 0}}
otp_store = {}


def gerar_otp(length: int = 6) -> str:
    """
    Gera código OTP aleatório
    
    Args:
        length: Comprimento do código (padrão 6 dígitos)
        
    Returns:
        Código OTP
    """
    return ''.join(random.choices(string.digits, k=length))


def enviar_otp_email(email: str) -> bool:
    """
    Envia código OTP para email do usuário
    
    Args:
        email: Email do usuário
        
    Returns:
        True se enviado com sucesso, False caso contrário
    """
    try:
        # Gerar código OTP
        codigo = gerar_otp()
        
        # Armazenar temporariamente (15 minutos de validade)
        otp_store[email] = {
            "code": codigo,
            "expires": datetime.utcnow() + timedelta(minutes=15),
            "attempts": 0
        }
        
        # Em produção, seria aqui que envia email via SMTP
        # Para desenvolvimento, apenas logar
        logger.info(f"OTP gerado para {email}: {codigo} (válido por 15 min)")
        
        # Simulação: em produção usar `smtplib` ou SendGrid/Mailgun
        print(f"🔐 [DEV] Código OTP para {email}: {codigo}")
        
        return True
        
    except Exception as e:
        logger.error(f"Erro ao enviar OTP: {str(e)}")
        return False


def validar_otp(email: str, codigo: str) -> tuple[bool, str]:
    """
    Valida código OTP fornecido pelo usuário
    
    Args:
        email: Email do usuário
        codigo: Código OTP fornecido
        
    Returns:
        (válido, mensagem)
    """
    try:
        # Verificar se existe OTP para este email
        if email not in otp_store:
            return False, "Código OTP não encontrado. Solicite um novo."
        
        otp_data = otp_store[email]
        
        # Verificar expiração
        if datetime.utcnow() > otp_data["expires"]:
            del otp_store[email]
            return False, "Código OTP expirou. Solicite um novo."
        
        # Verificar tentativas (máx 3)
        if otp_data["attempts"] >= 3:
            del otp_store[email]
            return False, "Muitas tentativas. Solicite um novo código."
        
        # Verificar código
        if otp_data["code"] != codigo:
            otp_data["attempts"] += 1
            return False, f"Código incorreto. {3 - otp_data['attempts']} tentativas restantes."
        
        # Código válido - remover do armazenamento
        del otp_store[email]
        logger.info(f"OTP validado com sucesso para {email}")
        
        return True, "Código validado com sucesso"
        
    except Exception as e:
        logger.error(f"Erro ao validar OTP: {str(e)}")
        return False, "Erro ao validar código"


def resend_otp(email: str) -> tuple[bool, str]:
    """
    Reenvia código OTP para o email
    
    Args:
        email: Email do usuário
        
    Returns:
        (sucesso, mensagem)
    """
    try:
        # Limpar OTP antigo se existir
        if email in otp_store:
            del otp_store[email]
        
        # Enviar novo OTP
        if enviar_otp_email(email):
            return True, "Código OTP reenviado para seu email"
        else:
            return False, "Erro ao reenviar código OTP"
            
    except Exception as e:
        logger.error(f"Erro ao resend OTP: {str(e)}")
        return False, "Erro ao reenviar código"


def limpar_otp_expirados():
    """
    Limpa códigos OTP expirados do armazenamento
    (Chamado periodicamente)
    """
    agora = datetime.utcnow()
    emails_expirados = [
        email for email, data in otp_store.items()
        if agora > data["expires"]
    ]
    
    for email in emails_expirados:
        del otp_store[email]
        logger.info(f"OTP expirado removido para {email}")
    
    return len(emails_expirados)
