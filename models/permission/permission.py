from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    func,
    CheckConstraint,
    UniqueConstraint,
)
from database.database import Base
from pydantic import BaseModel
from datetime import datetime
import json


class Permission(Base):
    __tablename__ = "permission"

    id = Column(String(255), primary_key=True, index=True)
    name = Column(String(255), nullable=False)  # Không NULL
    route = Column(String(255), nullable=False)  # Không NULL
    is_deleted = Column(Boolean, default=False)  # Mặc định là False
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), default=datetime.utcnow
    )
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        UniqueConstraint(
            "name", "route", name="unique_name_route"
        ),  # Đảm bảo kết hợp name và route là duy nhất
        UniqueConstraint("name", name="unique_name"),  # Đảm bảo name là duy nhất
        UniqueConstraint("route", name="unique_route"),  # Đảm bảo route là duy nhất
        CheckConstraint("name <> ''", name="check_name_not_empty"),  # name không rỗng
        CheckConstraint(
            "route <> ''", name="check_route_not_empty"
        ),  # route không rỗng
    )


class PermissionEntity(BaseModel):
    name: str
    route: str
    is_deleted: bool = False