from pydantic import BaseModel
from typing import Optional

class ChatInput(BaseModel):
    user_id: int
    message: str
    session_id: Optional[int] = None