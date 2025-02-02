from enum import Enum
from typing import Optional
from datetime import datetime
from pydantic import BaseModel

class ModelTypeEnum(str, Enum):
    cloud='cloud'
    local='local'

class ModelEntity(BaseModel):
    name: str
    detail_name: str
    type: ModelTypeEnum 
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None