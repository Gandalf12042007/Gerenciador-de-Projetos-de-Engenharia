from database.db_helper import DatabaseHelper


class UserRepository:
    def __init__(self):
        self.db = DatabaseHelper()

    def get_by_email(self, email: str):
        result = self.db.execute_query(
            "SELECT id, nome, email, senha_hash, role FROM usuarios WHERE email = %s",
            (email,),
            fetch=True
        )
        return result[0] if result else None

    def get_by_id(self, user_id: int):
        result = self.db.execute_query(
            "SELECT id, nome, email, senha_hash, role FROM usuarios WHERE id = %s",
            (user_id,),
            fetch=True
        )
        return result[0] if result else None

    def create(self, name: str, email: str, senha_hash: str, role: str = "user"):
        return self.db.execute_query(
            "INSERT INTO usuarios (nome, email, senha_hash, role, criado_em) VALUES (%s, %s, %s, %s, NOW())",
            (name, email, senha_hash, role)
        )
