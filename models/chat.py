from database.database import Base
from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    Integer,
    ForeignKey,
    JSON,
    func,
    ForeignKeyConstraint
)
from sqlalchemy.orm import relationship
from datetime import datetime

class Chat(Base):
    __tablename__ = 'chat'

    id = Column(Integer, primary_key=True, index=True) 
    title = Column(String(255), nullable=False)
    conversation = Column(JSON, nullable=False, default=[])
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)  
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), default=datetime.now)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", backref="users", foreign_keys=[user_id])

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "conversation": self.conversation,
            "user_id": self.user_id,
            "is_deleted": self.is_deleted,
            "created_at": str(self.created_at),
            "updated_at": str(self.updated_at),
            "user": self.user.to_dict()
        }