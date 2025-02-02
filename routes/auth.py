import json
from typing import List
from models.user import User
from datetime import datetime
from schema.user import LoginEntity
from helper.token import create_jwt_token
from database.database import db_dependency
from helper.password import create_password
from schema.response import ResponseMessage
from fastapi.exceptions import RequestValidationError
from fastapi import APIRouter, status, Depends, HTTPException

auth_router = APIRouter(prefix="/auth", tags=["auth"])

@auth_router.post("/login", status_code=status.HTTP_200_OK, name="Add new user")
async def login(auth_info: LoginEntity, db: db_dependency):
    try:
        password = create_password(auth_info.password)
        user: User = db.query(User).filter(
            User.user_name == auth_info.user_name,
            User.password == password,
            User.is_deleted == False,
        ).first()

        if not user:
            return ResponseMessage(
                code=status.HTTP_404_NOT_FOUND,
                message=f"User with name {auth_info.user_name} not exist."
            )

        user.token = create_jwt_token({
            "user_name": user.user_name,
            "email": user.email,
            "password": user.password,
            "date": str(datetime.now())
        })

        db.commit()

        return ResponseMessage(
            code=status.HTTP_200_OK,
            message=f"Login success",
            data=user
        )

    except Exception as e:
        db.rollback()
        return ResponseMessage(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"Database error: {str(e)}"
        )

@auth_router.post("/refresh-token", status_code=status.HTTP_200_OK, name="Add new user")
async def refresh_token(auth_info: LoginEntity, db: db_dependency):
    try:
        login_response = await login(auth_info, db)

        if login_response.status_code != status.HTTP_200_OK:
            return login_response
        response = json.loads(login_response.body.decode("utf-8"))
        user_data = response['data']

        return ResponseMessage(
            code=status.HTTP_200_OK,
            message="Token refreshed successfully.",
            data={
                "user_id": user_data["id"],
                "username": user_data["user_name"],
                "token": user_data["token"] 
            }
        )

    except Exception as e:
        db.rollback()
        return ResponseMessage(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"Database error: {str(e)}"
        )