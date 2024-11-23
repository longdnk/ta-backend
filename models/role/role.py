from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    Text,
    JSON,
    func,
    CheckConstraint,
)
from database.database import Base
from pydantic import BaseModel
from typing import List
from datetime import datetime


class Role(Base):
    __tablename__ = "role"

    id = Column(String(255), primary_key=True, index=True)
    name = Column(String(255), nullable=False)  # Không NULL
    permission_ids = Column(JSON, nullable=False)  # Lưu danh sách permission_id
    is_deleted = Column(Boolean, default=False)  # Mặc định là False
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), default=datetime.utcnow
    )
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        CheckConstraint(
            "name <> ''", name="check_name_not_empty"
        ),  # Đảm bảo name không rỗng
    )


class RoleEntity(BaseModel):
    name: str
    permission_ids: List[str]  # Lưu danh sách permission_id dưới dạng List
    is_deleted: bool = False