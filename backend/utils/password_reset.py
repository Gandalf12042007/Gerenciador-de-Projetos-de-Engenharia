"""
🔐 Recuperação de Senha - Password Reset Module
Sistema de Gerenciamento de Projetos de Engenharia
Fase 4: Segurança

Este módulo implementa:
- Geração de tokens temporários seguros
- Armazenamento de tokens com expiração
- Validação e consumo de tokens
- Envio de emails de recuperação

Desenvolvido por: Vicente de Souza
"""

import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import logging
import sys
import os

# Adicionar path do database
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'database'))
from db_helper import DatabaseHelper

logger = logging.getLogger(__name__)

# Configurações de token
TOKEN_EXPIRY_MINUTES = 30  # Token válido por 30 minutos
TOKEN_LENGTH = 32  # Tamanho do token em bytes


def _init_reset_tokens_table():
    """
    Cria a tabela de tokens de reset se não existir
    """
    db = DatabaseHelper()
    
    # SQLite usa DATETIME, MySQL usa TIMESTAMP
    db_type = os.getenv('DB_TYPE', 'sqlite').lower()
    
    if db_type == 'sqlite':
        create_sql = """
        CREATE TABLE IF NOT EXISTS password_reset_tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email VARCHAR(255) NOT NULL,
            token_hash VARCHAR(64) NOT NULL UNIQUE,
            expires_at DATETIME NOT NULL,
            used BOOLEAN DEFAULT 0,
            created_at DATETIME DEFAULT (datetime('now', 'localtime')),
            used_at DATETIME,
            ip_address VARCHAR(45)
        )
        """
    else:
        create_sql = """
        CREATE TABLE IF NOT EXISTS password_reset_tokens (
            id INT AUTO_INCREMENT PRIMARY KEY,
            email VARCHAR(255) NOT NULL,
            token_hash VARCHAR(64) NOT NULL UNIQUE,
            expires_at TIMESTAMP NOT NULL,
            used BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            used_at TIMESTAMP,
            ip_address VARCHAR(45),
            INDEX idx_email (email),
            INDEX idx_token_hash (token_hash)
        )
        """
    
    try:
        db.execute_query(create_sql)
        logger.info("✅ Tabela password_reset_tokens verificada/criada")
    except Exception as e:
        logger.error(f"❌ Erro ao criar tabela de tokens: {e}")


# Inicializar tabela ao importar módulo
_init_reset_tokens_table()


def _hash_token(token: str) -> str:
    """
    Gera hash SHA-256 do token para armazenamento seguro
    Nunca armazenamos o token em texto puro
    """
    return hashlib.sha256(token.encode()).hexdigest()


def generate_reset_token(email: str, ip_address: str = None) -> str:
    """
    Gera um token de recuperação de senha único e seguro
    
    Args:
        email: Email do usuário
        ip_address: IP de onde foi feita a solicitação
        
    Returns:
        Token em texto puro (enviar por email)
        
    Note:
        O token é armazenado como hash no banco.
        O usuário recebe o token original por email.
    """
    db = DatabaseHelper()
    email = email.lower().strip()
    
    # Invalidar tokens anteriores não usados do mesmo email
    invalidate_previous_tokens(email)
    
    # Gerar token criptograficamente seguro
    token = secrets.token_urlsafe(TOKEN_LENGTH)
    token_hash = _hash_token(token)
    
    # Calcular expiração
    expires_at = datetime.now() + timedelta(minutes=TOKEN_EXPIRY_MINUTES)
    
    try:
        db.execute_query(
            """
            INSERT INTO password_reset_tokens 
            (email, token_hash, expires_at, ip_address)
            VALUES (%s, %s, %s, %s)
            """,
            (email, token_hash, expires_at.strftime('%Y-%m-%d %H:%M:%S'), ip_address)
        )
        
        logger.info(f"✅ Token de reset gerado para: {email}")
        return token
        
    except Exception as e:
        logger.error(f"❌ Erro ao gerar token de reset: {e}")
        raise


def validate_reset_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Valida um token de recuperação de senha
    
    Args:
        token: Token recebido por email
        
    Returns:
        Dados do token se válido, None se inválido/expirado
    """
    db = DatabaseHelper()
    token_hash = _hash_token(token)
    
    result = db.execute_query(
        """
        SELECT id, email, expires_at, used
        FROM password_reset_tokens
        WHERE token_hash = %s
        """,
        (token_hash,),
        fetch=True
    )
    
    if not result or len(result) == 0:
        logger.warning(f"⚠️ Token de reset não encontrado")
        return None
    
    token_data = result[0]
    
    # Verificar se já foi usado
    if token_data.get('used'):
        logger.warning(f"⚠️ Token de reset já utilizado: {token_data.get('email')}")
        return None
    
    # Verificar expiração
    expires_at = token_data.get('expires_at')
    if isinstance(expires_at, str):
        expires_at = datetime.strptime(expires_at, '%Y-%m-%d %H:%M:%S')
    
    if datetime.now() > expires_at:
        logger.warning(f"⚠️ Token de reset expirado: {token_data.get('email')}")
        return None
    
    logger.info(f"✅ Token de reset válido para: {token_data.get('email')}")
    return dict(token_data)


def consume_reset_token(token: str) -> bool:
    """
    Marca um token como utilizado após reset bem-sucedido
    
    Args:
        token: Token a ser consumido
        
    Returns:
        True se consumido com sucesso, False caso contrário
    """
    db = DatabaseHelper()
    token_hash = _hash_token(token)
    
    try:
        result = db.execute_query(
            """
            UPDATE password_reset_tokens
            SET used = 1, used_at = %s
            WHERE token_hash = %s AND used = 0
            """,
            (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), token_hash)
        )
        
        logger.info(f"✅ Token de reset consumido")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao consumir token: {e}")
        return False


def invalidate_previous_tokens(email: str):
    """
    Invalida todos os tokens anteriores não usados de um email
    Chamado antes de gerar um novo token
    """
    db = DatabaseHelper()
    email = email.lower().strip()
    
    try:
        db.execute_query(
            """
            UPDATE password_reset_tokens
            SET used = 1, used_at = %s
            WHERE email = %s AND used = 0
            """,
            (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), email)
        )
        logger.info(f"✅ Tokens anteriores invalidados para: {email}")
    except Exception as e:
        logger.warning(f"⚠️ Erro ao invalidar tokens anteriores: {e}")


def cleanup_expired_tokens():
    """
    Remove tokens expirados do banco (manutenção)
    Pode ser chamado periodicamente via cron/scheduler
    """
    db = DatabaseHelper()
    
    try:
        db.execute_query(
            """
            DELETE FROM password_reset_tokens
            WHERE expires_at < %s OR used = 1
            """,
            (datetime.now().strftime('%Y-%m-%d %H:%M:%S'),)
        )
        logger.info("✅ Tokens expirados limpos")
    except Exception as e:
        logger.warning(f"⚠️ Erro ao limpar tokens: {e}")


def get_token_stats() -> Dict[str, Any]:
    """
    Retorna estatísticas de tokens (para admin/monitoramento)
    """
    db = DatabaseHelper()
    
    stats = {
        'total': 0,
        'active': 0,
        'used': 0,
        'expired': 0
    }
    
    try:
        result = db.execute_query(
            """
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN used = 0 AND expires_at > %s THEN 1 ELSE 0 END) as active,
                SUM(CASE WHEN used = 1 THEN 1 ELSE 0 END) as used,
                SUM(CASE WHEN used = 0 AND expires_at <= %s THEN 1 ELSE 0 END) as expired
            FROM password_reset_tokens
            """,
            (
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ),
            fetch=True
        )
        
        if result and len(result) > 0:
            stats = dict(result[0])
            
    except Exception as e:
        logger.error(f"❌ Erro ao obter estatísticas de tokens: {e}")
    
    return stats
