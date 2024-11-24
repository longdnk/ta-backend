from fastapi import APIRouter, status, HTTPException, Request, Depends
from response.response_item import response
from database.database import db_dependency
from helper.token import create_jwt_token
from helper.encrypt import encrypt_password
from models.user.user import User
from pydantic import BaseModel
from datetime import datetime


# Pydantic model for login payload
class Auth(BaseModel):
    identifier: str
    password: str


auth_router = APIRouter(prefix="/auths", tags=["auths"])


@auth_router.post("/login", status_code=status.HTTP_200_OK)
async def login_user(request: Request, login_info: Auth, db: db_dependency):
    """
    Login bằng email hoặc user_name và kiểm tra mật khẩu.
    """
    # Step 1: Truy vấn người dùng dựa trên email hoặc user_name
    user: User = (
        db.query(User)
        .filter(
            (
                (User.email == login_info.identifier)
                | (User.user_name == login_info.identifier)
            )  # Kiểm tra nếu email hoặc username trùng khớp
            & (User.is_deleted == False)  # Kiểm tra không bị xóa
        )
        .first()
    )

    # Step 2: Kiểm tra xem user có tồn tại không
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email/username",
        )

    # Step 3: Kiểm tra mật khẩu
    if not encrypt_password(login_info.password) == user.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password",
        )

    # Step 4: Tạo JWT token
    access_token = create_jwt_token(user.id, user.user_name, user.email)
    user.token = access_token  # Lưu token vào DB
    user.updated_at = datetime.utcnow()
    db.commit()

    # Step 5: Trả kết quả
    return response(
        code=status.HTTP_200_OK,
        message="Login successful",
        type="info",
        data={
            "user": {
                "id": user.id,
                "user_name": user.user_name,
                "email": user.email,
                "image": user.image,
                "token": user.token,
                "chat_ids": user.chat_ids,
                "prompt_ids": user.prompt_ids,
                "default_prompt": user.default_prompt,
                "role": user.role,
            }
        },
    )


@auth_router.get("/valid-token", status_code=status.HTTP_200_OK)
async def verify_token(request: Request, db: db_dependency):
    """
    Kiểm tra token có tồn tại trong DB hay không.
    """
    # Step 1: Lấy token từ header
    authorization: str = request.headers.get("Authorization")
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing or invalid Authorization header",
        )

    token = authorization.replace("Bearer ", "")  # Tách lấy phần token

    # Step 2: Kiểm tra token trong DB
    user: User = (
        db.query(User).filter(User.token == token, User.is_deleted == false).first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Token not found in database",
        )

    # Step 3: Trả kết quả
    return response(
        code=status.HTTP_200_OK,
        message="Token is valid",
        type="info",
        data={
            "user": {
                "id": user.id,
                "user_name": user.user_name,
                "email": user.email,
                "role": user.role,
            }
        },
    )
