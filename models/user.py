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
    ForeignKey,
    Text
)
from sqlalchemy.orm import relationship 

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, index=True)  # Chuyển từ String sang Integer
    user_name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    password = Column(Text, nullable=False)
    image = Column(String(255), nullable=True)
    is_deleted = Column(Boolean, default=False)
    token = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    chat_ids = Column(JSON, nullable=True, default=[])
    prompt_ids = Column(JSON, nullable=True, default=[])
    default_prompt = Column(Integer, ForeignKey("prompt.id"), nullable=False)
    role_id = Column(Integer, ForeignKey('role.id'))
    models = Column(JSON, nullable=True, default=[])
    default_model = Column(Integer, ForeignKey('model.id'), nullable=False)
    role = relationship("Role", foreign_keys=[role_id])
    detail_default_prompt = relationship("Prompt", foreign_keys=[default_prompt])
    detail_default_model = relationship("Model", foreign_keys=[default_model])

    def to_dict(self):
        return {
            "id": self.id,
            "user_name": self.user_name,
            "email": self.email,
            "image": self.image,
            "is_deleted": self.is_deleted,
            "token": self.token,
            "created_at": str(self.created_at),
            "updated_at": str(self.updated_at),
            "prompt_ids": self.prompt_ids,
            "chat_ids": self.chat_ids,
            "models": self.models,
            "role": self.role.to_dict(),
            "default_prompt": self.detail_default_prompt.to_dict(),
            "default_model": self.detail_default_model.to_dict(),
        }