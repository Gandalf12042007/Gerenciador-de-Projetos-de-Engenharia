import random
import string
import logging
from typing import Optional, Dict, Any

from repositories.project_repository import ProjectRepository
from repositories.team_repository import TeamRepository

logger = logging.getLogger(__name__)


def generate_project_code(length: int = 4) -> str:
    charset = string.ascii_uppercase + string.digits
    return ''.join(random.choices(charset, k=length))


class ProjectService:
    def __init__(self):
        self.repo = ProjectRepository()
        self.team_repo = TeamRepository()

    def _generate_unique_code(self) -> str:
        # loop until unique code found
        while True:
            code = generate_project_code()
            if not self.repo.exists_code(code):
                return code

    def create_project(self, name: str, description: str | None, created_by: int, **kwargs) -> int:
        # build data dictionary for repository
        data = {
            'nome': name,
            'descricao': description,
            'criador_id': created_by,
            'project_code': self._generate_unique_code()
        }
        project_id = self.repo.create(data)
        # add creator to team as gerente
        self.team_repo.add_member(project_id, created_by, papel='gerente')
        return project_id

    def list_user_projects(self, user_id: int, status: str = None) -> list[dict]:
        """Retorna lista de projetos visíveis para usuário (via DBHelper query)."""
        # Admin sees all
        # We'll detect admin by a flag in team repo maybe or skip for now
        db = self.repo.db
        if status:
            query = "SELECT p.* FROM projetos p WHERE p.status = %s"
            params = (status,)
        else:
            query = "SELECT p.* FROM projetos p"
            params = ()
        # if not admin join with equipes
        if not self.team_repo.is_member(0, user_id):
            query = "SELECT DISTINCT p.* FROM projetos p INNER JOIN equipes e ON p.id=e.projeto_id WHERE e.usuario_id=%s AND e.ativo=1" + (" AND p.status=%s" if status else "")
            params = (user_id,) + ((status,) if status else ())
        projects = db.execute_query(query, params, fetch=True) or []
        return projects

    def get_project(self, project_id: int, user_id: int) -> Optional[dict]:
        if not self.team_repo.is_member(project_id, user_id):
            return None
        return self.repo.get_by_id(project_id)

    def update_project(self, project_id: int, data: dict, user_id: int) -> bool:
        if not self.team_repo.is_manager(project_id, user_id):
            return False
        # simple update using repository (which accepts dict)
        self.repo.db.execute_query(
            f"UPDATE projetos SET " + ", ".join([f"{k}=%s" for k in data.keys()]) + " WHERE id=%s",
            tuple(data.values()) + (project_id,)
        )
        return True

    def delete_project(self, project_id: int, user_id: int) -> bool:
        # only creator or manager
        if not self.team_repo.is_manager(project_id, user_id):
            return False
        self.repo.db.execute_query("DELETE FROM projetos WHERE id = %s", (project_id,))
        return True

    def join_project_by_code(self, user_id: int, code: str) -> Optional[Dict[str, Any]]:
        project = self.repo.find_by_code(code)
        if not project:
            return None
        pid = project['id']
        if not self.team_repo.is_member(pid, user_id):
            self.team_repo.add_member(pid, user_id)
        return project

    def get_project_code(self, project_id: int, user_id: int) -> str | None:
        project = self.repo.get_by_id(project_id)
        if not project:
            return None
        if not self.team_repo.is_manager(project_id, user_id):
            return None
        code = project.get('project_code')
        if not code:
            code = self._generate_unique_code()
            self.repo.db.execute_query("UPDATE projetos SET project_code=%s WHERE id=%s", (code, project_id))
        return code

    def regenerate_project_code(self, project_id: int, user_id: int) -> str | None:
        if not self.team_repo.is_manager(project_id, user_id):
            return None
        new_code = self._generate_unique_code()
        self.repo.db.execute_query("UPDATE projetos SET project_code=%s WHERE id=%s", (new_code, project_id))
        return new_code

    def check_code_exists(self, code: str) -> bool:
        return self.repo.exists_code(code)
