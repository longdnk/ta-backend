from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    Text,
    func,
    CheckConstraint,
)
from database.database import Base
from pydantic import BaseModel
from datetime import datetime

class Prompt(Base):
    __tablename__ = "prompt"

    id = Column(String(255), primary_key=True, index=True)
    content = Column(Text, nullable=False)  # Không NULL
    is_deleted = Column(Boolean, default=False)  # Mặc định là False
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), default=datetime.utcnow
    )
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class PromptEntity(BaseModel):
    content: str
    is_deleted: bool = False