from typing import List
from models.chat import Chat 
from datetime import datetime
from schema.chat import ChatEntity 
from database.database import db_dependency
from schema.response import ResponseMessage
from fastapi.exceptions import RequestValidationError
from fastapi import APIRouter, status, Depends, HTTPException

chat_router = APIRouter(prefix="/chats", tags=["chats"])

@chat_router.get("", status_code=status.HTTP_200_OK, name="Get all chat")
async def fetch_all(db: db_dependency, skip: int = 0, limit: int = 100):
    try:
        query = (
            db.query(Chat)
            .filter(Chat.is_deleted == False)
            .offset(skip)
            .limit(limit)
        )
        chat: List[Chat] = query.all()

        return ResponseMessage(
            code=status.HTTP_200_OK,
            message="Fetch all chat success",
            data=chat
        )

    except Exception as e:
        db.rollback()
        return ResponseMessage(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"Database error: {str(e)}",
        )

@chat_router.get("/{chat_id}", status_code=status.HTTP_200_OK, name="Get chat by id")
async def fetch_detail(chat_id: int, db: db_dependency):
    try:
        chat: Chat = (
            db.query(Chat)
            .filter(Chat.id == chat_id, Chat.is_deleted == False)
            .first()
        )

        if not chat:
            return ResponseMessage(
                code=status.HTTP_404_NOT_FOUND,
                message=f"Chat with ID {chat_id} not found.",
            )

        return ResponseMessage(
            code=status.HTTP_200_OK,
            message=f"Fetch chat with id {chat_id} success",
            data=chat
        )

    except Exception as e:
        db.rollback()
        return ResponseMessage(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"Database error: {str(e)}",
        )

@chat_router.post("", status_code=status.HTTP_201_CREATED, name="Add new chat")
async def create(chat_item: ChatEntity, db: db_dependency):
    try:
        IS_EMPTY_ENTITY = chat_item.title == ""
        IS_UNDEFINED_ENTITY = chat_item.title is None
        if IS_EMPTY_ENTITY or IS_UNDEFINED_ENTITY:
            return ResponseMessage(
                code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                message="Entity error",
                data={"error": "Title cannot be empty"},
            )

        new_chat = Chat(**chat_item.dict())

        db.add(new_chat)
        db.commit()
        db.refresh(new_chat)

        return ResponseMessage(
            code=status.HTTP_201_CREATED,
            message="Chat created successfully",
            data=new_chat,
        )

    except Exception as e:
        db.rollback()
        return ResponseMessage(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"Database error: {str(e)}",
        )

@chat_router.put("/{chat_id}", status_code=status.HTTP_200_OK, name="Update chat")
async def update(chat_id: int, chat_item: ChatEntity, db: db_dependency):
    try:
        chat: Chat = (
            db.query(Chat)
            .filter(Chat.id == chat_id, Chat.is_deleted == False)
            .first()
        )

        if not chat:
            return ResponseMessage(
                code=status.HTTP_404_NOT_FOUND,
                message=f"Chat with ID {chat_id} not found.",
            )

        chat.conversation = chat_item.conversation
        chat.title = chat_item.title
        chat.updated_at = datetime.now()

        db.commit()
        db.refresh(chat)

        return ResponseMessage(
            code=status.HTTP_200_OK,
            message="Prompt updated successfully",
            data=chat,
        )

    except Exception as e:
        db.rollback()
        return ResponseMessage(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"Database error: {str(e)}",
        )

@chat_router.delete("/{chat_id}", status_code=status.HTTP_200_OK, name="Delete prompt")
async def delete(chat_id: int, db: db_dependency):
    try:
        chat: Chat = (
            db.query(Chat)
            .filter(Chat.id == chat_id, Chat.is_deleted == False)
            .first()
        )

        if not chat:
            return ResponseMessage(
                code=status.HTTP_404_NOT_FOUND,
                message=f"Chat with ID {chat_id} not found.",
            )

        chat.is_deleted = True
        db.commit()

        return ResponseMessage(
            code=status.HTTP_200_OK,
            message="Prompt deleted successfully",
            data=chat,
        )

    except Exception as e:
        db.rollback()
        return ResponseMessage(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"Database error: {str(e)}",
        )