import re
import logging
from repositories.user_repository import UserRepository
from utils.auth import hash_password

logger = logging.getLogger(__name__)


class UserService:
    def __init__(self):
        self.repo = UserRepository()

    @staticmethod
    def validate_password(password: str) -> bool:
        """Verifica força da senha: 8+, 1 maiúscula, 1 número"""
        if len(password) < 8:
            return False
        if not re.search(r"[A-Z]", password):
            return False
        if not re.search(r"\d", password):
            return False
        return True

    def create_user(self, nome: str, email: str, senha: str, telefone: str = None, cargo: str = None, role: str = "user"):
        """Cria um novo usuário validando regras e retornando o id gerado."""
        if not self.validate_password(senha):
            raise ValueError("Senha fraca. Requisitos: mín. 8 caracteres, 1 maiúscula, 1 número")
        if len(nome.strip()) < 3:
            raise ValueError("Nome deve ter no mínimo 3 caracteres")

        existing = self.repo.get_by_email(email.lower())
        if existing:
            logger.warning(f"Tentativa de registro com email já existente: {email}")
            raise ValueError("Email já cadastrado no sistema")

        senha_hash = hash_password(senha)
        user_id = self.repo.create(nome.strip(), email.lower(), senha_hash, role)
        return user_id
