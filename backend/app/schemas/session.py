from datetime import datetime
from pydantic import BaseModel


class SessionView(BaseModel):
    session_id: str
    username: str
    ip: str
    ports: list[int]
    expires_at: datetime
