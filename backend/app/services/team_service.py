"""
TeamService - Lógica de negócio para Equipes
"""

import logging
from typing import List, Dict, Any, Optional

from app.repositories import TeamRepository, UserRepository, ProjectRepository

logger = logging.getLogger(__name__)


class TeamService:
    """Service para operações de equipes"""
    
    def __init__(self):
        self.team_repo = TeamRepository()
        self.user_repo = UserRepository()
        self.project_repo = ProjectRepository()
    
    def list_members(self, project_id: int, user_id: int) -> List[Dict[str, Any]]:
        """
        Lista membros de um projeto com verificação de acesso
        """
        # Verificar se usuário tem acesso ao projeto
        if not self.team_repo.is_member(project_id, user_id):
            logger.warning(f"User {user_id} tried to list members of project {project_id}")
            return []
        
        return self.team_repo.find_members(project_id)
    
    def add_member(
        self, 
        project_id: int, 
        user_email: str, 
        cargo: str,
        requester_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Adiciona membro ao projeto (apenas gerentes)
        """
        # Verificar permissão
        if not self.team_repo.is_manager(project_id, requester_id):
            raise PermissionError("Apenas gerentes podem adicionar membros")
        
        # Buscar usuário por email
        user = self.user_repo.find_by_email(user_email)
        if not user:
            raise ValueError(f"Usuário com email {user_email} não encontrado")
        
        # Verificar se já é membro
        if self.team_repo.is_member(project_id, user['id']):
            raise ValueError("Usuário já é membro do projeto")
        
        # Validar cargo
        valid_cargos = ['gerente', 'coordenador', 'engenheiro', 'tecnico', 'membro']
        if cargo not in valid_cargos:
            cargo = 'membro'
        
        # Adicionar membro
        member_id = self.team_repo.add_member(project_id, user['id'], cargo)
        
        logger.info(f"User {user['id']} added to project {project_id} as {cargo}")
        
        return {
            'id': member_id,
            'usuario_id': user['id'],
            'nome': user['nome'],
            'email': user['email'],
            'cargo': cargo
        }
    
    def remove_member(
        self, 
        project_id: int, 
        member_user_id: int, 
        requester_id: int
    ) -> bool:
        """
        Remove membro do projeto
        """
        # Verificar permissão
        if not self.team_repo.is_manager(project_id, requester_id):
            raise PermissionError("Apenas gerentes podem remover membros")
        
        # Não pode remover a si mesmo se for o único gerente
        project = self.project_repo.find_by_id(project_id)
        if project and project.get('criador_id') == member_user_id:
            raise ValueError("Não é possível remover o criador do projeto")
        
        self.team_repo.remove_member(project_id, member_user_id)
        logger.info(f"User {member_user_id} removed from project {project_id}")
        
        return True
    
    def update_member_role(
        self, 
        project_id: int, 
        member_user_id: int, 
        new_role: str,
        requester_id: int
    ) -> bool:
        """
        Atualiza cargo do membro
        """
        # Verificar permissão
        if not self.team_repo.is_manager(project_id, requester_id):
            raise PermissionError("Apenas gerentes podem alterar cargos")
        
        # Validar cargo
        valid_roles = ['gerente', 'coordenador', 'engenheiro', 'tecnico', 'membro']
        if new_role not in valid_roles:
            raise ValueError(f"Cargo inválido. Use: {', '.join(valid_roles)}")
        
        self.team_repo.update_role(project_id, member_user_id, new_role)
        logger.info(f"User {member_user_id} role updated to {new_role} in project {project_id}")
        
        return True
    
    def get_member_role(self, project_id: int, user_id: int) -> Optional[str]:
        """
        Retorna cargo do usuário no projeto
        """
        role_info = self.team_repo.find_user_role(project_id, user_id)
        return role_info.get('cargo') if role_info else None
    
    def check_permission(
        self, 
        project_id: int, 
        user_id: int, 
        required_role: str = 'membro'
    ) -> bool:
        """
        Verifica se usuário tem permissão mínima
        """
        role = self.get_member_role(project_id, user_id)
        if not role:
            return False
        
        # Hierarquia de cargos
        role_hierarchy = {
            'membro': 1,
            'tecnico': 2,
            'engenheiro': 3,
            'coordenador': 4,
            'gerente': 5
        }
        
        user_level = role_hierarchy.get(role, 0)
        required_level = role_hierarchy.get(required_role, 0)
        
        return user_level >= required_level
    
    def invite_member(
        self, 
        project_id: int, 
        email: str, 
        cargo: str,
        requester_id: int
    ) -> Dict[str, Any]:
        """
        Envia convite para novo membro (se não existir no sistema)
        """
        # Verificar permissão
        if not self.team_repo.is_manager(project_id, requester_id):
            raise PermissionError("Apenas gerentes podem convidar membros")
        
        # Verificar se usuário existe
        user = self.user_repo.find_by_email(email)
        
        if user:
            # Usuário existe, adicionar diretamente
            return self.add_member(project_id, email, cargo, requester_id)
        
        # Criar convite pendente (em produção, salvaria no banco e enviaria email)
        logger.info(f"Invite sent to {email} for project {project_id}")
        
        return {
            'status': 'invited',
            'email': email,
            'cargo': cargo,
            'message': f'Convite enviado para {email}'
        }
    
    def transfer_ownership(
        self, 
        project_id: int, 
        new_owner_id: int, 
        current_owner_id: int
    ) -> bool:
        """
        Transfere propriedade do projeto
        """
        project = self.project_repo.find_by_id(project_id)
        if not project:
            raise ValueError("Projeto não encontrado")
        
        # Verificar se é o dono atual
        if project.get('criador_id') != current_owner_id:
            raise PermissionError("Apenas o criador pode transferir propriedade")
        
        # Verificar se novo dono é membro
        if not self.team_repo.is_member(project_id, new_owner_id):
            raise ValueError("Novo proprietário deve ser membro do projeto")
        
        # Transferir
        self.team_repo.transfer_ownership(project_id, current_owner_id, new_owner_id)
        
        # Atualizar criador_id no projeto
        self.project_repo.update(project_id, {'criador_id': new_owner_id})
        
        logger.info(f"Project {project_id} ownership transferred from {current_owner_id} to {new_owner_id}")
        
        return True
    
    def get_team_statistics(self, project_id: int) -> Dict[str, Any]:
        """
        Retorna estatísticas da equipe
        """
        members = self.team_repo.find_members(project_id)
        
        role_count = {}
        for member in members:
            role = member.get('cargo', 'membro')
            role_count[role] = role_count.get(role, 0) + 1
        
        return {
            'total_membros': len(members),
            'por_cargo': role_count
        }
