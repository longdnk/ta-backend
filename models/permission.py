from datetime import datetime
from database.database import Base
from sqlalchemy.orm import validates
from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    Text,
    Integer,
    UniqueConstraint,
    func,
    ForeignKey,
)

from sqlalchemy.orm import relationship 

class Permission(Base):
    __tablename__ = 'permission'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    route = Column(String(255), nullable=False)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), default=datetime.now)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    @validates('name')
    def validate_name(self, key, value):
        if not value:
            raise ValueError("name cannot be empty")
        return value

    @validates('route')
    def validate_route(self, key, value):
        if not value:
            raise ValueError("route cannot be empty")
        return value

    __table_args__ = (
        UniqueConstraint("name", "route", name="unique_name_route"),  # Vẫn cần UniqueConstraint cho tính duy nhất trong CSDL
        UniqueConstraint("name", name="unique_name"),
        UniqueConstraint("route", name="unique_route"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "route": self.route,
            "is_deleted": self.is_deleted,
            "created_at": str(self.created_at),
            "updated_at": str(self.updated_at),
        }
