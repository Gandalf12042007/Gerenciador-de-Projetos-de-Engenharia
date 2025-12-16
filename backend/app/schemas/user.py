from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    nome: str
    email: EmailStr
    cargo: Optional[str] = None

class UserCreate(UserBase):
    senha: str

class UserOut(UserBase):
    id_usuario: int
    telefone: Optional[str]
    especialidade: Optional[str]
    bio: Optional[str]
    foto_url: Optional[str]

    class Config:
        orm_mode = True
