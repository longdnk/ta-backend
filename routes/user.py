from fastapi import APIRouter, status, HTTPException, Request
from models.user.user import User, UserEntity, UserUpdate
from response.response_item import response
from database.database import db_dependency
from fastapi.responses import FileResponse
from helper.token import create_jwt_token
from sqlalchemy.exc import IntegrityError
from models.prompt.prompt import Prompt
from sqlalchemy.orm import Session
from models.role.role import Role
from datetime import datetime
from helper import encrypt
from uuid import uuid4
from os import path

user_router = APIRouter(prefix="/users", tags=["users"])


@user_router.get("", status_code=status.HTTP_200_OK)
async def get_users(
    request: Request, db: db_dependency, skip: int = 0, limit: int = 100
):
    users = (
        db.query(User)
        .filter(User.is_deleted == False)
        .order_by(User.created_at.asc())
        .all()
    )

    if users is None:
        return response(
            code=status.HTTP_400_BAD_REQUEST,
            message="Cannot find User list",
            type="error",
            data=[],
        )

    return response(
        code=status.HTTP_200_OK,
        message="OK",
        type="info",
        data=users[skip : skip + limit],
    )


@user_router.post("", status_code=status.HTTP_201_CREATED)
async def create_user(request: Request, user_entity: UserEntity, db: db_dependency):
    try:
        # Kiểm tra dữ liệu đầu vào: user_name, email, và password là bắt buộc
        if (
            not user_entity.user_name
            or not user_entity.email
            or not user_entity.password
        ):
            return response(
                code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                message="Username, email, and password are required",
                type="error",
                data={
                    "user_name": "Username cannot be empty",
                    "email": "Email cannot be empty",
                    "password": "Password cannot be empty",
                },
            )

        # Kiểm tra xem user_name và email đã tồn tại trong DB chưa
        existing_user = (
            db.query(User)
            .filter(
                (User.user_name == user_entity.user_name)
                | (User.email == user_entity.email)
            )
            .first()
        )

        if existing_user:
            return response(
                code=status.HTTP_409_CONFLICT,
                message="User with this username or email already exists",
                type="error",
                data={
                    "user_name": "Username already exists",
                    "email": "Email already exists",
                },
            )

        # Kiểm tra xem default_prompt có tồn tại không
        if user_entity.default_prompt:
            prompt = (
                db.query(Prompt).filter(Prompt.id == user_entity.default_prompt).first()
            )
            if not prompt:
                return response(
                    code=status.HTTP_404_NOT_FOUND,
                    message="Default prompt not found",
                    type="error",
                    data={"default_prompt": "Default prompt does not exist"},
                )

        # Kiểm tra xem role_id có tồn tại trong DB không
        if not user_entity.role_id:
            return response(
                code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                message="Role ID cannot be empty",
                type="error",
                data={"role_id": "Role ID cannot be empty"},
            )

        role: Role = db.query(Role).filter(Role.id == user_entity.role_id).first()
        if not role:
            return response(
                code=status.HTTP_404_NOT_FOUND,
                message="Role not found",
                type="error",
                data={"role_id": "Role does not exist"},
            )

        # Tạo người dùng mới
        new_user = User(**user_entity.dict())
        new_user.id = str(uuid4())
        new_user.password = encrypt.encrypt_password(new_user.password)
        new_user.token = create_jwt_token(new_user.id, new_user.user_name, new_user.email)
        db.add(new_user)
        db.commit()

        return response(
            code=status.HTTP_201_CREATED,
            message="User created successfully",
            type="info",
            data={
                "id": new_user.id,
                "user_name": new_user.user_name,
                "email": new_user.email,
                "image": new_user.image,
                "chat_ids": new_user.chat_ids,
                "prompt_ids": new_user.prompt_ids,
                "default_prompt": new_user.default_prompt,
                "role_id": new_user.role_id,
                "role": role.name,
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


@user_router.get("/{user_id}", status_code=status.HTTP_200_OK)
async def get_user(user_id: str, db: db_dependency):
    user: User = (
        db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
    )

    if not user:
        return response(
            code=status.HTTP_404_NOT_FOUND,
            message="User not found",
            type="error",
            data={"error": "Cannot find user"},
        )

    return response(
        code=status.HTTP_200_OK,
        message="OK",
        type="info",
        data={
            "id": user.id,
            "user_name": user.user_name,
            "email": user.email,
            "image": user.image,
            "chat_ids": user.chat_ids,
            "prompt_ids": user.prompt_ids,
            "default_prompt": user.default_prompt,
            "role_id": user.role_id,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
        },
    )


@user_router.put("/{user_id}", status_code=status.HTTP_200_OK)
async def update_user(user_id: str, user_entity: UserUpdate, db: db_dependency):
    user: User = db.query(User).filter(User.id == user_id).first()

    if not user:
        return response(
            code=status.HTTP_404_NOT_FOUND,
            message="User not found",
            type="error",
            data={"error": f"Cannot find user with id {user_id}"},
        )

    # Kiểm tra dữ liệu đầu vào: user_name, email, và password là bắt buộc
    if not user_entity.user_name or not user_entity.email:
        return response(
            code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message="Username, email, and password are required",
            type="error",
            data={
                "user_name": "Username cannot be empty",
                "email": "Email cannot be empty",
                "password": "Password cannot be empty",
            },
        )

    # Kiểm tra xem email và username đã tồn tại trong DB chưa
    existing_user = (
        db.query(User)
        .filter(
            (User.user_name == user_entity.user_name)
            | (User.email == user_entity.email)
        )
        .first()
    )

    if existing_user and existing_user.id != user.id:
        return response(
            code=status.HTTP_409_CONFLICT,
            message="User with this username or email already exists",
            type="error",
            data={
                "user_name": "Username already exists",
                "email": "Email already exists",
            },
        )

    # Cập nhật thông tin người dùng
    user.user_name = user_entity.user_name
    user.email = user_entity.email
    user.image = user_entity.image
    user.token = user_entity.token if user_entity.token else user.token
    user.chat_ids = user_entity.chat_ids if user_entity.chat_ids else []
    user.prompt_ids = user_entity.prompt_ids if user_entity.prompt_ids else []
    user.default_prompt = user_entity.default_prompt
    user.role_id = user_entity.role_id
    user.is_deleted = user_entity.is_deleted
    user.updated_at = datetime.utcnow()

    db.commit()

    return response(
        code=status.HTTP_200_OK,
        message="User updated successfully",
        type="info",
        data={
            "id": user.id,
            "user_name": user.user_name,
            "email": user.email,
            "image": user.image,
            "chat_ids": user.chat_ids,
            "prompt_ids": user.prompt_ids,
            "default_prompt": user.default_prompt,
            "role_id": user.role_id,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
        },
    )


@user_router.delete("/{user_id}", status_code=status.HTTP_200_OK)
async def delete_user(user_id: str, db: db_dependency):
    user: User = db.query(User).filter(User.id == user_id).first()

    if not user:
        return response(
            code=status.HTTP_404_NOT_FOUND,
            message="User not found",
            type="error",
            data={"error": "Cannot find user item"},
        )

    # Đánh dấu người dùng là đã xóa
    user.is_deleted = True
    user.updated_at = datetime.utcnow()

    db.commit()

    return response(
        code=status.HTTP_200_OK,
        message="User deleted successfully",
        type="info",
        data={"id": user_id},
    )


@user_router.get("/image/{filename}", status_code=status.HTTP_200_OK)
async def get_image(filename: str):
    image_path = path.join("images", filename)  # Đường dẫn đến thư mục chứa hình ảnh

    if not path.exists(image_path):  # Kiểm tra xem file có tồn tại không
        raise HTTPException(status_code=404, detail="Image not found")

    return FileResponse(image_path)  # Trả về hình ảnh
