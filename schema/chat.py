from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List, Dict

class ChatEntity(BaseModel):
    title: str
    conversation: List[Dict]
    user_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None