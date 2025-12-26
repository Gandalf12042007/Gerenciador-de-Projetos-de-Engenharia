"""
Sistema de Permissões - Gerenciador de Projetos
Verificação de acesso a projetos e recursos
Desenvolvido por: Vicente de Souza
"""

import mysql.connector
from typing import Optional, Dict, List
from config import settings


class PermissionManager:
    """Gerenciador de permissões de usuários"""
    
    # Papéis na equipe (do banco: gerente, engenheiro, tecnico, colaborador)
    ROLE_MANAGER = "gerente"
    ROLE_ENGINEER = "engenheiro"
    ROLE_TECHNICIAN = "tecnico"
    ROLE_COLLABORATOR = "colaborador"
    
    # Hierarquia de permissões (maior número = mais permissão)
    ROLE_HIERARCHY = {
        "gerente": 4,
        "engenheiro": 3,
        "tecnico": 2,
        "colaborador": 1
    }
    
    def __init__(self):
        self.db_config = settings.db_config
    
    def _get_connection(self):
        """Cria conexão com banco de dados"""
        return mysql.connector.connect(**self.db_config)
    
    def is_project_member(self, user_id: int, project_id: int) -> bool:
        """
        Verifica se usuário é membro do projeto
        
        Args:
            user_id: ID do usuário
            project_id: ID do projeto
            
        Returns:
            True se é membro ativo, False caso contrário
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            query = """
                SELECT COUNT(*) 
                FROM equipes 
                WHERE projeto_id = %s 
                  AND usuario_id = %s 
                  AND ativo = TRUE
            """
            cursor.execute(query, (project_id, user_id))
            count = cursor.fetchone()[0]
            return count > 0
        finally:
            cursor.close()
            conn.close()
    
    def get_user_role_in_project(self, user_id: int, project_id: int) -> Optional[str]:
        """
        Retorna o papel do usuário no projeto
        
        Args:
            user_id: ID do usuário
            project_id: ID do projeto
            
        Returns:
            Papel do usuário (gerente, engenheiro, etc) ou None
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            query = """
                SELECT papel 
                FROM equipes 
                WHERE projeto_id = %s 
                  AND usuario_id = %s 
                  AND ativo = TRUE
                LIMIT 1
            """
            cursor.execute(query, (project_id, user_id))
            result = cursor.fetchone()
            return result[0] if result else None
        finally:
            cursor.close()
            conn.close()
    
    def has_permission(
        self, 
        user_id: int, 
        project_id: int, 
        required_role: str = ROLE_COLLABORATOR
    ) -> bool:
        """
        Verifica se usuário tem permissão baseada em papel
        
        Args:
            user_id: ID do usuário
            project_id: ID do projeto
            required_role: Papel mínimo necessário
            
        Returns:
            True se tem permissão, False caso contrário
        """
        user_role = self.get_user_role_in_project(user_id, project_id)
        
        if not user_role:
            return False
        
        user_level = self.ROLE_HIERARCHY.get(user_role, 0)
        required_level = self.ROLE_HIERARCHY.get(required_role, 0)
        
        return user_level >= required_level
    
    def is_project_owner(self, user_id: int, project_id: int) -> bool:
        """
        Verifica se usuário é dono do projeto
        
        Args:
            user_id: ID do usuário
            project_id: ID do projeto
            
        Returns:
            True se é criador do projeto, False caso contrário
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            query = """
                SELECT COUNT(*) 
                FROM projetos 
                WHERE id = %s AND criador_id = %s
            """
            cursor.execute(query, (project_id, user_id))
            count = cursor.fetchone()[0]
            return count > 0
        finally:
            cursor.close()
            conn.close()
    
    def is_project_manager(self, user_id: int, project_id: int) -> bool:
        """
        Verifica se usuário é gerente do projeto
        
        Args:
            user_id: ID do usuário
            project_id: ID do projeto
            
        Returns:
            True se é gerente, False caso contrário
        """
        role = self.get_user_role_in_project(user_id, project_id)
        return role == self.ROLE_MANAGER
    
    def can_modify_project(self, user_id: int, project_id: int) -> bool:
        """
        Verifica se usuário pode modificar projeto
        Apenas gerente ou criador podem
        
        Args:
            user_id: ID do usuário
            project_id: ID do projeto
            
        Returns:
            True se pode modificar, False caso contrário
        """
        return (
            self.is_project_owner(user_id, project_id) or
            self.is_project_manager(user_id, project_id)
        )
    
    def can_delete_project(self, user_id: int, project_id: int) -> bool:
        """
        Verifica se usuário pode deletar projeto
        Apenas criador pode
        
        Args:
            user_id: ID do usuário
            project_id: ID do projeto
            
        Returns:
            True se pode deletar, False caso contrário
        """
        return self.is_project_owner(user_id, project_id)
    
    def get_user_projects(self, user_id: int) -> List[Dict]:
        """
        Retorna todos os projetos do usuário
        
        Args:
            user_id: ID do usuário
            
        Returns:
            Lista de projetos com papel do usuário
        """
        conn = self._get_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            query = """
                SELECT 
                    p.id,
                    p.nome,
                    p.status,
                    e.papel,
                    e.data_entrada,
                    (p.criador_id = %s) as is_owner
                FROM projetos p
                INNER JOIN equipes e ON p.id = e.projeto_id
                WHERE e.usuario_id = %s AND e.ativo = TRUE
                ORDER BY e.data_entrada DESC
            """
            cursor.execute(query, (user_id, user_id))
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()


# Instância global
permission_manager = PermissionManager()
