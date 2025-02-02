from typing import List
from models.user import User
from datetime import datetime
from schema.user import UserEntity
from helper.token import create_jwt_token
from database.database import db_dependency
from helper.password import create_password
from schema.response import ResponseMessage
from fastapi.exceptions import RequestValidationError
from fastapi import APIRouter, status, Depends, HTTPException

user_router = APIRouter(prefix="/users", tags=["users"])

@user_router.get("", status_code=status.HTTP_200_OK, name="Get all user")
async def fetch_all(db: db_dependency, skip: int = 0, limit: int = 100):
    try:
        query = (
            db.query(User).filter(User.is_deleted == False).offset(skip).limit(limit)
        )
        users: List[User] = query.all()

        return ResponseMessage(
            code=status.HTTP_200_OK, message="Fetch all user success", data=users
        )

    except Exception as e:
        db.rollback()
        return ResponseMessage(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"Database error: {str(e)}",
        )


@user_router.get("/{user_id}", status_code=status.HTTP_200_OK, name="Get user by id")
async def fetch_detail(user_id: int, db: db_dependency):
    try:
        user: User = (
            db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
        )

        if not user:
            return ResponseMessage(
                code=status.HTTP_404_NOT_FOUND,
                message=f"User with ID {user_id} not found.",
            )

        return ResponseMessage(
            code=status.HTTP_200_OK,
            message=f"Fetch user with id {user_id} success",
            data=user,
        )

    except Exception as e:
        db.rollback()
        return ResponseMessage(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"Database error: {str(e)}",
        )

@user_router.post("", status_code=status.HTTP_201_CREATED, name="Add new user")
async def create(user_item: UserEntity, db: db_dependency):
    try:
        IS_EMPTY_ENTITY = (
            user_item.user_name == ""
            or user_item.email == ""
            or user_item.password == ""
            or user_item.default_model == ""
            or user_item.default_prompt == ""
        )

        IS_UNDEFINED_ENTITY = (
            user_item.user_name is None
            or user_item.email is None
            or user_item.password is None
            or user_item.default_model is None
            or user_item.default_prompt is None
        )

        if IS_EMPTY_ENTITY or IS_UNDEFINED_ENTITY:
            return ResponseMessage(
                code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                message="Entity error",
                data={"error": "'user_name' | 'email' | 'password' | 'default_model' | 'default_prompt' cannot be empty"},
            )

        new_user = User(**user_item.dict())

        new_user.password = create_password(new_user.password)
        new_user.token = create_jwt_token({
            "user_name": new_user.user_name,
            "email": new_user.email,
            "password": new_user.password,
            "date": str(datetime.now())
        })

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return ResponseMessage(
            code=status.HTTP_201_CREATED,
            message="User created successfully",
            data=new_user
        )

    except Exception as e:
        db.rollback()
        return ResponseMessage(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"Database error: {str(e)}",
        )

@user_router.put("/{user_id}", status_code=status.HTTP_200_OK, name="Update user")
async def update(user_id: int, user_item: UserEntity, db: db_dependency):
    try:
        user: User = (
            db.query(User)
            .filter(User.id == user_id, User.is_deleted == False)
            .first()
        )

        if not user:
            return ResponseMessage(
                code=status.HTTP_404_NOT_FOUND,
                message=f"User with ID {user_id} not found.",
            )

        user.user_name = user_item.user_name
        user.email = user_item.email
        user.password = create_password(user_item.password)
        user.updated_at = datetime.now()
        user.default_prompt = user_item.default_prompt
        user.default_model = user_item.default_model
        user.role_id = user_item.role_id
        user.chat_ids = user_item.chat_ids
        user.prompt_ids = user_item.prompt_ids
        user.models = user_item.models

        db.commit()
        db.refresh(user)

        return ResponseMessage(
            code=status.HTTP_200_OK,
            message="User updated successfully",
            data=user,
        )

    except Exception as e:
        db.rollback()
        return ResponseMessage(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"Database error: {str(e)}",
        )

@user_router.delete("/{user_id}", status_code=status.HTTP_200_OK, name="Delete user")
async def delete(user_id: int, db: db_dependency):
    try:
        user: User = (
            db.query(User)
            .filter(User.id == user_id, User.is_deleted == False)
            .first()
        )

        if not user:
            return ResponseMessage(
                code=status.HTTP_404_NOT_FOUND,
                message=f"User with ID {user_id} not found.",
            )

        user.is_deleted = True
        db.commit()

        return ResponseMessage(
            code=status.HTTP_200_OK,
            message="User deleted successfully",
            data=user
        )

    except Exception as e:
        db.rollback()
        return ResponseMessage(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"Database error: {str(e)}",
        )