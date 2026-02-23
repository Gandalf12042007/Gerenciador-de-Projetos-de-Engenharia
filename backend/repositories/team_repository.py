from database.db_helper import DatabaseHelper


class TeamRepository:
    def __init__(self):
        self.db = DatabaseHelper()

    def is_member(self, project_id: int, user_id: int) -> bool:
        result = self.db.execute_query(
            "SELECT id FROM equipes WHERE projeto_id = %s AND usuario_id = %s AND ativo = 1",
            (project_id, user_id),
            fetch=True
        )
        return bool(result and len(result) > 0)

    def add_member(self, project_id: int, user_id: int, papel: str = 'colaborador') -> int:
        from datetime import date
        return self.db.execute_query(
            """
            INSERT INTO equipes (projeto_id, usuario_id, papel, data_entrada, ativo)
            VALUES (%s, %s, %s, %s, 1)
            """,
            (project_id, user_id, papel, str(date.today()))
        )

    def remove_member(self, project_id: int, user_id: int) -> bool:
        self.db.execute_query(
            "UPDATE equipes SET ativo = 0 WHERE projeto_id = %s AND usuario_id = %s",
            (project_id, user_id)
        )
        return True
