"""
AuthService - Lógica de autenticação e autorização
"""

import os
import logging
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import jwt

from config import settings
from app.repositories import UserRepository

logger = logging.getLogger(__name__)


class AuthService:
    """Service para autenticação e autorização"""
    
    def __init__(self):
        self.user_repo = UserRepository()
        self.secret_key = settings.SECRET_KEY
        self.algorithm = settings.ALGORITHM
        self.token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
    
    def authenticate(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Autentica usuário e retorna dados se válido
        """
        logger.info(f"Authentication attempt for: {email}")
        
        user = self.user_repo.find_by_email(email)
        if not user:
            logger.warning(f"User not found: {email}")
            return None
        
        # Verificar senha
        password_hash = self._hash_password(password)
        if user['senha'] != password_hash:
            logger.warning(f"Invalid password for: {email}")
            return None
        
        # Verificar se ativo
        if not user.get('ativo', True):
            logger.warning(f"Inactive user tried to login: {email}")
            return None
        
        # Atualizar último login
        self.user_repo.update_last_login(user['id'])
        
        logger.info(f"User authenticated: {email}")
        
        # Retornar dados sem senha
        return {
            'id': user['id'],
            'nome': user['nome'],
            'email': user['email'],
            'username': user.get('username'),
            'cargo': user.get('cargo'),
            'is_admin': user.get('is_admin', False),
            'ativo': user.get('ativo', True)
        }
    
    def create_access_token(
        self, 
        user_data: Dict[str, Any], 
        expires_delta: timedelta = None
    ) -> str:
        """
        Gera token JWT
        """
        to_encode = user_data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.token_expire_minutes)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        })
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        
        logger.debug(f"Token created for user {user_data.get('id')}")
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verifica e decodifica token JWT
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Verificar expiração
            exp = payload.get('exp')
            if exp and datetime.utcnow() > datetime.fromtimestamp(exp):
                logger.warning("Token expired")
                return None
            
            return payload
            
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {str(e)}")
            return None
    
    def refresh_token(self, token: str) -> Optional[str]:
        """
        Renova token se válido
        """
        payload = self.verify_token(token)
        if not payload:
            return None
        
        # Verificar se usuário ainda existe e está ativo
        user = self.user_repo.find_by_id(payload.get('id'))
        if not user or not user.get('ativo', True):
            return None
        
        # Criar novo token com os mesmos dados
        user_data = {
            'id': user['id'],
            'email': user['email'],
            'nome': user['nome'],
            'is_admin': user.get('is_admin', False)
        }
        
        return self.create_access_token(user_data)
    
    def login(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Processo completo de login
        """
        user = self.authenticate(email, password)
        if not user:
            return None
        
        # Gerar token
        token = self.create_access_token({
            'id': user['id'],
            'user_id': user['id'],  # Compatibilidade
            'email': user['email'],
            'nome': user['nome'],
            'is_admin': user.get('is_admin', False)
        })
        
        return {
            'access_token': token,
            'token_type': 'bearer',
            'expires_in': self.token_expire_minutes * 60,
            'user': user
        }
    
    def register(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Registra novo usuário
        """
        logger.info(f"Registration attempt for: {data.get('email')}")
        
        # Verificar email duplicado
        if self.user_repo.find_by_email(data['email']):
            raise ValueError("Email já cadastrado")
        
        # Validar senha
        if len(data.get('senha', '')) < 6:
            raise ValueError("Senha deve ter pelo menos 6 caracteres")
        
        # Hash da senha
        password_hash = self._hash_password(data['senha'])
        
        # Criar usuário
        user_data = {
            'nome': data['nome'],
            'email': data['email'],
            'username': data.get('username', data['email'].split('@')[0]),
            'senha': password_hash,
            'cargo': data.get('cargo', 'engenheiro'),
            'is_admin': False,
            'ativo': 1
        }
        
        user_id = self.user_repo.create(user_data)
        logger.info(f"User registered with ID {user_id}")
        
        # Fazer login automático
        return self.login(data['email'], data['senha'])
    
    def change_password(
        self, 
        user_id: int, 
        current_password: str, 
        new_password: str
    ) -> bool:
        """
        Altera senha do usuário
        """
        user = self.user_repo.find_by_id(user_id)
        if not user:
            return False
        
        # Verificar senha atual
        if user['senha'] != self._hash_password(current_password):
            logger.warning(f"Wrong current password for user {user_id}")
            return False
        
        # Validar nova senha
        if len(new_password) < 6:
            raise ValueError("Nova senha deve ter pelo menos 6 caracteres")
        
        # Atualizar
        new_hash = self._hash_password(new_password)
        self.user_repo.update_password(user_id, new_hash)
        
        logger.info(f"Password changed for user {user_id}")
        return True
    
    def request_password_reset(self, email: str) -> Optional[str]:
        """
        Gera token para reset de senha
        """
        user = self.user_repo.find_by_email(email)
        if not user:
            # Não revelar se email existe
            return None
        
        # Gerar token seguro
        reset_token = secrets.token_urlsafe(32)
        
        # Em produção: salvar no banco com expiração
        # Por agora: apenas log e retorno
        logger.info(f"Password reset requested for {email}")
        
        return reset_token
    
    def reset_password(self, token: str, new_password: str) -> bool:
        """
        Reseta senha usando token
        """
        # Em produção: verificar token no banco
        # Por agora: placeholder
        
        if len(new_password) < 6:
            raise ValueError("Nova senha deve ter pelo menos 6 caracteres")
        
        logger.info("Password reset executed")
        return True
    
    def get_current_user(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Retorna usuário atual baseado no token
        """
        payload = self.verify_token(token)
        if not payload:
            return None
        
        user_id = payload.get('id') or payload.get('user_id')
        if not user_id:
            return None
        
        user = self.user_repo.find_by_id(user_id)
        if not user or not user.get('ativo', True):
            return None
        
        # Retornar sem senha
        return {
            'id': user['id'],
            'nome': user['nome'],
            'email': user['email'],
            'username': user.get('username'),
            'cargo': user.get('cargo'),
            'is_admin': user.get('is_admin', False)
        }
    
    def _hash_password(self, password: str) -> str:
        """Gera hash SHA256 da senha"""
        return hashlib.sha256(password.encode()).hexdigest()
