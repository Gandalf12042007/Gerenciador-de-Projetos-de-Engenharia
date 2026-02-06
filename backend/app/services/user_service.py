"""
UserService - Lógica de negócio para Usuários
"""

import logging
import hashlib
import secrets
from typing import Dict, Any, Optional, List
from datetime import datetime

from app.repositories import UserRepository

logger = logging.getLogger(__name__)


class UserService:
    """Service para operações de usuários"""
    
    def __init__(self):
        self.user_repo = UserRepository()
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Obtém usuário por ID (sem senha)"""
        user = self.user_repo.find_by_id(user_id)
        if user:
            return self._safe_user(user)
        return None
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Obtém usuário por email"""
        return self.user_repo.find_by_email(email)
    
    def list_active_users(self) -> List[Dict[str, Any]]:
        """Lista usuários ativos"""
        return self.user_repo.find_active_users()
    
    def create_user(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cria novo usuário
        """
        logger.info(f"Creating user: {data.get('email')}")
        
        # Verificar email duplicado
        if self.user_repo.find_by_email(data['email']):
            raise ValueError("Email já cadastrado")
        
        # Verificar username duplicado
        if data.get('username') and self.user_repo.find_by_username(data['username']):
            raise ValueError("Username já existe")
        
        # Hash da senha
        password_hash = self._hash_password(data['senha'])
        
        user_data = {
            'nome': data['nome'],
            'email': data['email'],
            'username': data.get('username', data['email'].split('@')[0]),
            'senha': password_hash,
            'cargo': data.get('cargo', 'engenheiro'),
            'is_admin': data.get('is_admin', False),
            'ativo': 1
        }
        
        user_id = self.user_repo.create(user_data)
        logger.info(f"User created with ID {user_id}")
        
        return self.get_user_by_id(user_id)
    
    def update_user(self, user_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Atualiza dados do usuário
        """
        # Campos permitidos para atualização
        allowed_fields = ['nome', 'cargo', 'username']
        update_data = {k: v for k, v in data.items() if k in allowed_fields and v is not None}
        
        if update_data:
            self.user_repo.update(user_id, update_data)
            logger.info(f"User {user_id} updated")
        
        return self.get_user_by_id(user_id)
    
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
        current_hash = self._hash_password(current_password)
        if user['senha'] != current_hash:
            logger.warning(f"Password change failed for user {user_id}: wrong current password")
            return False
        
        # Validar nova senha
        if len(new_password) < 6:
            raise ValueError("Nova senha deve ter pelo menos 6 caracteres")
        
        # Atualizar senha
        new_hash = self._hash_password(new_password)
        self.user_repo.update_password(user_id, new_hash)
        logger.info(f"Password changed for user {user_id}")
        
        return True
    
    def reset_password(self, email: str) -> Optional[str]:
        """
        Gera token para reset de senha
        """
        user = self.user_repo.find_by_email(email)
        if not user:
            return None
        
        # Gerar token seguro
        token = secrets.token_urlsafe(32)
        
        # Salvar token (em produção, salvar no banco com expiração)
        # Por agora, apenas retorna o token
        logger.info(f"Password reset token generated for {email}")
        
        return token
    
    def deactivate_user(self, user_id: int, admin_id: int) -> bool:
        """
        Desativa usuário (soft delete)
        """
        # Verificar se admin tem permissão
        admin = self.user_repo.find_by_id(admin_id)
        if not admin or not admin.get('is_admin'):
            logger.warning(f"Non-admin user {admin_id} tried to deactivate user {user_id}")
            return False
        
        self.user_repo.deactivate(user_id)
        logger.info(f"User {user_id} deactivated by admin {admin_id}")
        return True
    
    def get_user_profile(self, user_id: int) -> Dict[str, Any]:
        """
        Retorna perfil completo do usuário
        """
        user = self.get_user_by_id(user_id)
        if not user:
            return None
        
        # Adicionar projetos do usuário
        user['projetos'] = self.user_repo.get_user_projects(user_id)
        
        return user
    
    def validate_credentials(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Valida credenciais do usuário para login
        """
        user = self.user_repo.find_by_email(email)
        if not user:
            return None
        
        password_hash = self._hash_password(password)
        if user['senha'] != password_hash:
            return None
        
        if not user.get('ativo', True):
            return None
        
        # Atualizar último login
        self.user_repo.update_last_login(user['id'])
        
        return self._safe_user(user)
    
    def _hash_password(self, password: str) -> str:
        """Gera hash SHA256 da senha"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _safe_user(self, user: Dict[str, Any]) -> Dict[str, Any]:
        """Remove campos sensíveis do usuário"""
        safe = dict(user)
        safe.pop('senha', None)
        return safe
