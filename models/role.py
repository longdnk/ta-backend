from database.database import Base
from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    Integer,
    UniqueConstraint,
    JSON,
    func,
    Table,
    ForeignKey
)
from sqlalchemy.orm import relationship 

class Role(Base):
    __tablename__ = "role"

    id = Column(Integer, primary_key=True, index=True)  # Chuyển từ String sang Integer
    name = Column(String(255), nullable=False)
    permission_ids = Column(JSON, nullable=False)  # Lưu dưới dạng JSON
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "permission_ids": self.permission_ids,
            "created_at": str(self.created_at),
            "updated_at": str(self.updated_at),
        }
