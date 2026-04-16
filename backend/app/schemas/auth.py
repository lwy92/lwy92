from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str
    password: str
    ports: list[int] = Field(default_factory=lambda: [22])


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = 'bearer'
    session_id: str
    ip: str
