"""
Testes de Autenticação e utilitários
"""

from utils.auth import hash_password, verify_password, create_access_token, decode_access_token
from services.auth_service import AuthService


def test_hash_and_verify():
    pwd = "Teste1234"
    hashed = hash_password(pwd)
    assert hashed != pwd
    assert verify_password(pwd, hashed)
    assert not verify_password("erro", hashed)


def test_jwt_roundtrip():
    data = {"user_id": 1, "email": "foo@bar.com"}
    token = create_access_token(data)
    payload = decode_access_token(token)
    assert payload is not None
    assert payload["user_id"] == 1


def test_auth_service_authenticate(monkeypatch):
    # criar um repositório fake que retorne um usuário com senha hash
    fake_hash = hash_password("secret123")
    class DummyRepo:
        def get_by_email(self, email):
            if email == "a@b.com":
                return {"id": 1, "email": email, "senha_hash": fake_hash}
            return None

    monkeypatch.setattr(
        "repositories.user_repository.UserRepository",
        lambda: DummyRepo()
    )

    auth = AuthService()
    assert auth.authenticate_user("a@b.com", "secret123")
    assert auth.authenticate_user("a@b.com", "errado") is None
    assert auth.authenticate_user("x@y.com", "secret123") is None
