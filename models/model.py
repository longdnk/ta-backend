from database.database import Base
from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    Integer,
    func,
)
from datetime import datetime

class Model(Base):
    __tablename__ = 'model'

    id = Column(Integer, primary_key=True, index=True)  
    name = Column(String(255), nullable=False, unique=True)
    detail_name = Column(String(255), nullable=False, unique=True)
    type = Column(String(255), nullable=False)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), default=datetime.now)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "detail_name": self.detail_name,
            "is_deleted": self.is_deleted,
            "created_at": str(self.created_at),
            "updated_at": str(self.updated_at)
        }