from pydantic import BaseModel


class User(BaseModel):
    username: str
    password_hash: str
    is_active: bool = True
    is_admin: bool = False
