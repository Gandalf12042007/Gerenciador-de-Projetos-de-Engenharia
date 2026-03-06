import os
import sys

# Adicionar path do database
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'database'))
from db_helper import DatabaseHelper


class ProjectRepository:
    def __init__(self):
        self.db = DatabaseHelper()

    def exists_code(self, code: str) -> bool:
        result = self.db.execute_query(
            "SELECT id FROM projetos WHERE project_code = %s",
            (code,),
            fetch=True
        )
        return bool(result and len(result) > 0)

    def create(self, data: dict):
        # Inserção dinâmica baseado nas chaves do dict
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['%s'] * len(data))
        query = f"INSERT INTO projetos ({columns}) VALUES ({placeholders})"
        return self.db.execute_query(query, tuple(data.values()))

    def get_by_id(self, project_id: int):
        result = self.db.execute_query(
            "SELECT id, nome as name, descricao as description, project_code, criador_id as created_by FROM projetos WHERE id = %s",
            (project_id,),
            fetch=True
        )
        return result[0] if result else None
