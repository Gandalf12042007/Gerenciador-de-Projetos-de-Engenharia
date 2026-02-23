from pydantic import BaseModel, EmailStr
from datetime import datetime


class User(BaseModel):
    id: int | None = None
    name: str
    email: EmailStr
    password_hash: str
    role: str = "user"
    created_at: datetime | None = None
