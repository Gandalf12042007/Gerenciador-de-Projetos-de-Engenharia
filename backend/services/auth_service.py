from datetime import timedelta
from repositories.user_repository import UserRepository
from utils.auth import verify_password, create_access_token
from config import settings


class AuthService:
    def __init__(self):
        self.user_repo = UserRepository()

    def authenticate_user(self, email: str, password: str):
        user = self.user_repo.get_by_email(email)
        if not user:
            return None
        if not verify_password(password, user.get('senha_hash') or user.get('password_hash')):
            return None
        return user

    def create_access_token_for_user(self, user: dict) -> str:
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        return create_access_token(
            data={
                "user_id": user['id'],
                "email": user['email'],
                "role": user.get('role', 'user')
            },
            expires_delta=access_token_expires
        )
