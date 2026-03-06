from datetime import datetime, timedelta
from jose import jwt
import bcrypt
from app.core.config import settings

# Usar bcrypt diretamente (passlib tem problemas de compatibilidade)
def verify_password(plain: str, hashed: str) -> bool:
    """Verifica senha usando bcrypt diretamente"""
    try:
        return bcrypt.checkpw(plain.encode('utf-8'), hashed.encode('utf-8'))
    except Exception:
        return False

def get_password_hash(password: str) -> str:
    """Gera hash bcrypt da senha"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(12)).decode('utf-8')

def create_access_token(subject: str):
    expire = datetime.utcnow() + timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_HOURS)
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded = jwt.encode(to_encode, settings.JWT_SECRET, algorithm="HS256")
    return encoded

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        return payload.get("sub")
    except Exception:
        return None
