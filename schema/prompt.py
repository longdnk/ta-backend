from typing import Optional
from datetime import datetime
from pydantic import BaseModel

class PromptEntity(BaseModel):
    content: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None