from typing import Optional
from datetime import datetime
from pydantic import BaseModel

class PermissionEntity(BaseModel):
    name: str
    route: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None