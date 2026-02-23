from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from utils.auth import decode_access_token
from repositories.user_repository import UserRepository


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_active_user(token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado"
        )
    user_id = payload.get("user_id")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )
    user = UserRepository().get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    return user
