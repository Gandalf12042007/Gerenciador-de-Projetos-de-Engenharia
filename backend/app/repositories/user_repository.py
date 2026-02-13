"""
UserRepository - Repositório para operações de Usuários
"""

import logging
from typing import List, Dict, Any, Optional
from .base_repository import BaseRepository

logger = logging.getLogger(__name__)


class UserRepository(BaseRepository):
    """Repositório para gerenciamento de usuários"""
    
    def __init__(self):
        super().__init__()
        self.table_name = "usuarios"
        self.primary_key = "id"
    
    def find_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Busca usuário por email"""
        query = "SELECT * FROM usuarios WHERE email = %s"
        try:
            result = self.execute_raw(query, (email,), fetch=True)
            return result[0] if result else None
        except Exception as e:
            logger.error(f"Error finding user by email: {str(e)}")
            raise
    
    def find_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Busca usuário por username"""
        query = "SELECT * FROM usuarios WHERE username = %s"
        try:
            result = self.execute_raw(query, (username,), fetch=True)
            return result[0] if result else None
        except Exception as e:
            logger.error(f"Error finding user by username: {str(e)}")
            raise
    
    def find_active_users(self) -> List[Dict[str, Any]]:
        """Lista apenas usuários ativos"""
        query = "SELECT id, nome, email, username, cargo, is_admin, criado_em FROM usuarios WHERE ativo = 1"
        try:
            return self.execute_raw(query, fetch=True) or []
        except Exception as e:
            logger.error(f"Error finding active users: {str(e)}")
            raise
    
    def authenticate(self, email: str, password_hash: str) -> Optional[Dict[str, Any]]:
        """Autentica usuário por email e senha hash"""
        query = """
            SELECT id, nome, email, username, cargo, is_admin, ativo
            FROM usuarios 
            WHERE email = %s AND senha = %s AND ativo = 1
        """
        try:
            result = self.execute_raw(query, (email, password_hash), fetch=True)
            return result[0] if result else None
        except Exception as e:
            logger.error(f"Error authenticating user: {str(e)}")
            raise
    
    def get_user_projects(self, user_id: int) -> List[Dict[str, Any]]:
        """Retorna projetos do usuário"""
        query = """
            SELECT p.id, p.nome, p.status, e.cargo
            FROM projetos p
            INNER JOIN equipes e ON p.id = e.projeto_id
            WHERE e.usuario_id = %s AND e.ativo = 1
        """
        try:
            return self.execute_raw(query, (user_id,), fetch=True) or []
        except Exception as e:
            logger.error(f"Error getting user projects: {str(e)}")
            raise
    
    def update_password(self, user_id: int, new_password_hash: str) -> bool:
        """Atualiza senha do usuário"""
        return self.update(user_id, {'senha': new_password_hash})
    
    def update_last_login(self, user_id: int) -> bool:
        """Atualiza data do último login"""
        query = "UPDATE usuarios SET ultimo_login = NOW() WHERE id = %s"
        try:
            self.execute_raw(query, (user_id,))
            return True
        except Exception as e:
            logger.error(f"Error updating last login: {str(e)}")
            raise
    
    def deactivate(self, user_id: int) -> bool:
        """Desativa usuário (soft delete)"""
        return self.update(user_id, {'ativo': 0})
    
    def get_admins(self) -> List[Dict[str, Any]]:
        """Lista usuários administradores"""
        query = "SELECT id, nome, email FROM usuarios WHERE is_admin = 1 AND ativo = 1"
        try:
            return self.execute_raw(query, fetch=True) or []
        except Exception as e:
            logger.error(f"Error getting admins: {str(e)}")
            raise
