from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    JSON,
    func,
    ForeignKeyConstraint,
)
from sqlalchemy.sql import expression
from database.database import Base
from pydantic import BaseModel
from datetime import datetime


class Chat(Base):
    __tablename__ = "chat"

    id = Column(String(255), primary_key=True, index=True)
    title = Column(String(255), nullable=False)  # Không NULL
    chunks = Column(JSON, nullable=False, default=expression.literal_column("[]"))  # Mảng JSON trống mặc định
    user_id = Column(String(255), nullable=False)  # Trường user_id bắt buộc
    is_deleted = Column(Boolean, default=False)  # Mặc định là False
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), default=datetime.utcnow
    )
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

class ChatEntity(BaseModel):
    title: str
    chunks: list = []  # Dữ liệu dạng JSON
    user_id: str
    is_deleted: bool = False
