from sqlalchemy import (
    Column,
    Boolean,
    DateTime,
    Text,
    Integer,
    func
)
from datetime import datetime
from database.database import Base

class Prompt(Base):
    __tablename__ = 'prompt'

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), default=datetime.now)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "content": self.content,
            "is_deleted": self.is_deleted,
            "created_at": str(self.created_at),
            "updated_at": str(self.updated_at)
        }