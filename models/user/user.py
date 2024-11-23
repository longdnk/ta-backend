from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    JSON,
    func,
    ForeignKey,
    CheckConstraint,
)
from sqlalchemy.orm import relationship
from database.database import Base
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class User(Base):
    __tablename__ = "user"

    id = Column(String(255), primary_key=True, index=True)
    user_name = Column(String(255), nullable=False)  # Không NULL
    email = Column(String(255), nullable=False, unique=True)  # Không NULL, UNIQUE
    password = Column(String(255), nullable=False)  # Không NULL
    image = Column(String(255), nullable=True)
    token = Column(String(255), nullable=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), default=datetime.utcnow
    )
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    chat_ids = Column(JSON, nullable=True)  # Lưu danh sách chat_ids dưới dạng JSON
    prompt_ids = Column(JSON, nullable=True)  # Lưu danh sách prompt_ids dưới dạng JSON
    default_prompt = Column(
        String(255), ForeignKey("prompt.id"), nullable=True
    )  # Liên kết với bảng prompt
    role_id = Column(
        String(255), ForeignKey("role.id"), nullable=True
    )  # Liên kết với bảng role
    is_deleted = Column(Boolean, default=False)  # Mặc định là False

    # Quan hệ với bảng Role
    role = relationship("Role", backref="users", foreign_keys=[role_id])

    # Quan hệ với bảng Prompt
    default_prompt_item = relationship(
        "Prompt", backref="users", foreign_keys=[default_prompt]
    )

    __table_args__ = (
        CheckConstraint(
            "email <> ''", name="check_email_not_empty"
        ),  # Đảm bảo email không rỗng
        CheckConstraint(
            "user_name <> ''", name="check_user_name_not_empty"
        ),  # Đảm bảo user_name không rỗng
    )


class UserEntity(BaseModel):
    user_name: str
    email: str
    password: str
    image: Optional[str] = None
    token: Optional[str] = None
    chat_ids: Optional[List[str]] = []
    prompt_ids: Optional[List[str]] = []
    default_prompt: Optional[str] = None
    role_id: Optional[str] = None
    is_deleted: bool = False

    class Config:
        orm_mode = True

class UserUpdate(BaseModel):
    user_name: str
    email: str
    image: Optional[str] = None
    token: Optional[str] = None
    chat_ids: Optional[List[str]] = []
    prompt_ids: Optional[List[str]] = []
    default_prompt: Optional[str] = None
    role_id: Optional[str] = None
    is_deleted: bool = False

    class Config:
        orm_mode = True
