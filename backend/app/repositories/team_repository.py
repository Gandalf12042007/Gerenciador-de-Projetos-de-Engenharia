"""
TeamRepository - Repositório para operações de Equipes
"""

import logging
from typing import List, Dict, Any, Optional
from .base_repository import BaseRepository

logger = logging.getLogger(__name__)


class TeamRepository(BaseRepository):
    """Repositório para gerenciamento de equipes"""
    
    def __init__(self):
        super().__init__()
        self.table_name = "equipes"
        self.primary_key = "id"
    
    def find_members(self, project_id: int) -> List[Dict[str, Any]]:
        """Lista membros de um projeto"""
        query = """
            SELECT e.id, e.papel, e.ativo, e.criado_em,
                   u.id as usuario_id, u.nome, u.email
            FROM equipes e
            INNER JOIN usuarios u ON e.usuario_id = u.id
            WHERE e.projeto_id = %s AND e.ativo = 1
            ORDER BY e.papel, u.nome
        """
        
        try:
            return self.execute_raw(query, (project_id,), fetch=True) or []
        except Exception as e:
            logger.error(f"Error finding team members for project {project_id}: {str(e)}")
            raise
    
    def find_user_role(self, project_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        """Busca papel do usuário em um projeto"""
        query = """
            SELECT e.id, e.papel, e.ativo
            FROM equipes e
            WHERE e.projeto_id = %s AND e.usuario_id = %s AND e.ativo = 1
        """
        
        try:
            result = self.execute_raw(query, (project_id, user_id), fetch=True)
            return result[0] if result else None
        except Exception as e:
            logger.error(f"Error finding user role: {str(e)}")
            raise
    
    def add_member(self, project_id: int, user_id: int, cargo: str = "colaborador") -> int:
        """Adiciona membro ao projeto"""
        # Verificar se já existe (ativo ou inativo)
        existing = self.execute_raw(
            "SELECT id, ativo FROM equipes WHERE projeto_id = %s AND usuario_id = %s",
            (project_id, user_id),
            fetch=True
        )
        
        if existing:
            # Reativar se estava inativo
            if not existing[0]['ativo']:
                self.update(existing[0]['id'], {'ativo': 1, 'papel': cargo})
            return existing[0]['id']
        
        # Criar novo membro
        return self.create({
            'projeto_id': project_id,
            'usuario_id': user_id,
            'papel': cargo,
            'data_entrada': 'date("now")',
            'ativo': 1
        })
    
    def remove_member(self, project_id: int, user_id: int) -> bool:
        """Remove membro do projeto (soft delete)"""
        query = """
            UPDATE equipes SET ativo = 0 
            WHERE projeto_id = %s AND usuario_id = %s
        """
        
        try:
            self.execute_raw(query, (project_id, user_id))
            logger.info(f"Removed user {user_id} from project {project_id}")
            return True
        except Exception as e:
            logger.error(f"Error removing team member: {str(e)}")
            raise
    
    def update_role(self, project_id: int, user_id: int, new_role: str) -> bool:
        """Atualiza papel do membro"""
        query = """
            UPDATE equipes SET papel = ?
            WHERE projeto_id = ? AND usuario_id = ? AND ativo = 1
        """
        
        try:
            self.execute_raw(query, (new_role, project_id, user_id))
            logger.info(f"Updated role for user {user_id} in project {project_id} to {new_role}")
            return True
        except Exception as e:
            logger.error(f"Error updating team role: {str(e)}")
            raise
    
    def is_member(self, project_id: int, user_id: int) -> bool:
        """Verifica se usuário é membro do projeto"""
        role = self.find_user_role(project_id, user_id)
        return role is not None
    
    def is_manager(self, project_id: int, user_id: int) -> bool:
        """Verifica se usuário é gerente do projeto"""
        role = self.find_user_role(project_id, user_id)
        return bool(role and role.get('papel') in ['gerente', 'coordenador', 'admin'])
    
    def get_user_projects_count(self, user_id: int) -> int:
        """Conta projetos do usuário"""
        query = "SELECT COUNT(*) as total FROM equipes WHERE usuario_id = %s AND ativo = 1"
        
        try:
            result = self.execute_raw(query, (user_id,), fetch=True)
            return result[0]['total'] if result else 0
        except Exception as e:
            logger.error(f"Error counting user projects: {str(e)}")
            raise
    
    def transfer_ownership(self, project_id: int, from_user: int, to_user: int) -> bool:
        """Transfere propriedade do projeto"""
        try:
            # Rebaixar o antigo dono
            self.update_role(project_id, from_user, 'colaborador')
            # Promover o novo dono
            self.update_role(project_id, to_user, 'gerente')
            logger.info(f"Transferred ownership of project {project_id} from {from_user} to {to_user}")
            return True
        except Exception as e:
            logger.error(f"Error transferring ownership: {str(e)}")
            raise
