from fastapi import APIRouter, status, HTTPException, Request
from database.database import db_dependency
from models.chat.chat import Chat, ChatEntity
from response.response_item import response
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from models.user.user import User
from datetime import datetime
from uuid import uuid4

chat_router = APIRouter(prefix="/chats", tags=["chats"])

# Endpoint lấy danh sách chat
@chat_router.get("", status_code=status.HTTP_200_OK)
async def get_chats(
    request: Request, db: db_dependency, skip: int = 0, limit: int = 100
):
    chats = (
        db.query(Chat)
        .filter(Chat.is_deleted == False)
        .order_by(Chat.created_at.asc())
        .all()
    )

    if chats is None:
        return response(
            code=status.HTTP_400_BAD_REQUEST,
            message="Cannot find chat list",
            type="error",
            data=[],
        )

    return response(
        code=status.HTTP_200_OK,
        message="OK",
        type="info",
        data=chats[skip : skip + limit],
    )


# Endpoint tạo mới chat
@chat_router.post("", status_code=status.HTTP_201_CREATED)
async def create_chat(request: Request, chat_entity: ChatEntity, db: db_dependency):
    # Kiểm tra xem user_id có tồn tại trong DB không
    user = (
        db.query(User)
        .filter(User.id == chat_entity.user_id, User.is_deleted == False)
        .first()
    )

    if not user:
        return response(
            code=status.HTTP_400_BAD_REQUEST,
            message="User ID not found or is deleted",
            type="error",
            data={"user_id": "User ID does not exist or is deleted"},
        )

    try:
        # Tạo mới chat
        new_chat = Chat(**chat_entity.dict())
        new_chat.id = str(uuid4())

        db.add(new_chat)
        db.commit()

        return response(
            code=status.HTTP_201_CREATED,
            message="Chat created successfully",
            type="info",
            data={
                "id": new_chat.id,
                "title": new_chat.title,
                "chunks": new_chat.chunks,
                "user_id": new_chat.user_id,
            },
        )
    except IntegrityError:
        db.rollback()
        return response(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Database error",
            type="error",
            data={"error": "Server Internal error"},
        )


# Endpoint lấy thông tin chat theo ID
@chat_router.get("/{chat_id}", status_code=status.HTTP_200_OK)
async def get_chat(chat_id: str, db: db_dependency):
    chat = db.query(Chat).filter(Chat.id == chat_id, Chat.is_deleted == False).first()

    if not chat:
        return response(
            code=status.HTTP_404_NOT_FOUND,
            message="Chat not found",
            type="error",
            data={},
        )

    return response(
        code=status.HTTP_200_OK,
        message="OK",
        type="info",
        data=chat,
    )


# Endpoint cập nhật thông tin chat
@chat_router.put("/{chat_id}", status_code=status.HTTP_200_OK)
async def update_chat(chat_id: str, chat_entity: ChatEntity, db: db_dependency):
    chat = db.query(Chat).filter(Chat.id == chat_id).first()

    if not chat:
        return response(
            code=status.HTTP_404_NOT_FOUND,
            message="Chat not found",
            type="error",
            data={"error": f"Cannot find chat with id {chat_id}"},
        )

    # Kiểm tra xem user_id có tồn tại trong DB không
    user = (
        db.query(User)
        .filter(User.id == chat_entity.user_id, User.is_deleted == False)
        .first()
    )

    if not user:
        return response(
            code=status.HTTP_400_BAD_REQUEST,
            message="User ID not found or is deleted",
            type="error",
            data={"user_id": "User ID does not exist or is deleted"},
        )

    # Cập nhật chat
    chat.title = chat_entity.title
    chat.chunks = chat_entity.chunks
    chat.user_id = chat_entity.user_id
    chat.is_deleted = chat_entity.is_deleted
    chat.updated_at = datetime.utcnow()

    db.commit()

    return response(
        code=status.HTTP_200_OK,
        message="Chat updated successfully",
        type="info",
        data={"id": chat.id, "title": chat.title, "chunks": chat.chunks},
    )


# Endpoint xóa chat (đánh dấu là đã xóa)
@chat_router.delete("/{chat_id}", status_code=status.HTTP_200_OK)
async def delete_chat(chat_id: str, db: db_dependency):
    chat = db.query(Chat).filter(Chat.id == chat_id).first()

    if not chat:
        return response(
            code=status.HTTP_404_NOT_FOUND,
            message="Chat not found",
            type="error",
            data={"error": "Cannot find chat item"},
        )

    # Đánh dấu chat là đã xóa
    chat.is_deleted = True
    chat.updated_at = datetime.utcnow()

    db.commit()

    return response(
        code=status.HTTP_200_OK,
        message="Chat deleted successfully",
        type="info",
        data={"id": chat_id},
    )