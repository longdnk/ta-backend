from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional

class RoleEntity(BaseModel):
    name: str
    permission_ids: List[int]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None