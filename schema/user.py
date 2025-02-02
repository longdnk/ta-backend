from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List

class UserEntity(BaseModel):
    user_name: str
    email: str
    password: str
    image: Optional[str] = None
    token: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    chat_ids: List[str]
    prompt_ids: List[str]
    default_prompt: int
    default_model: int
    role_id: int
    models: List[str]

class LoginEntity(BaseModel):
    user_name: str
    password: str