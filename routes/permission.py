from models.permission.permission import Permission, PermissionEntity
from fastapi import APIRouter, status, HTTPException, Request
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from response.response_item import response
from database.database import db_dependency
from pydantic import ValidationError
from sqlalchemy.orm import Session
from datetime import datetime
from sqlalchemy import or_
from uuid import uuid4
import time

permission_router = APIRouter(prefix="/permissions", tags=["permissions"])


@permission_router.get("", status_code=status.HTTP_200_OK)
async def get_permissions(
    request: Request, db: db_dependency, skip: int = 0, limit: int = 100
):
    permission = (
        db.query(Permission)
        .filter(Permission.is_deleted == False)
        .order_by(Permission.created_at.asc())
        .all()
    )

    if permission is None:
        return response(
            code=status.HTTP_400_BAD_REQUEST,
            message="Cannot find permission list",
            type="error",
            data=[],
        )

    return response(
        code=status.HTTP_200_OK,
        message="OK",
        type="info",
        data=permission[skip : skip + limit],
    )


@permission_router.get("/{permission_id}", status_code=status.HTTP_200_OK)
async def get_permission_by_id(permission_id: str, db: db_dependency):
    # Lấy thông tin permission từ DB qua id
    permission = db.query(Permission).filter(Permission.id == permission_id).first()

    # Nếu không tìm thấy permission
    if not permission:
        return response(
            code=status.HTTP_404_NOT_FOUND,
            message="Permission not found",
            type="error",
            data={},
        )

    return response(
        code=status.HTTP_200_OK,
        message="Permission found",
        type="info",
        data=permission,
    )


@permission_router.post("", status_code=status.HTTP_201_CREATED)
async def create_permission(
    request: Request, permission: PermissionEntity, db: db_dependency
):
    try:
        # Kiểm tra trước khi thêm vào DB
        existing_permission = (
            db.query(Permission)
            .filter(
                (Permission.name == permission.name)
                | (Permission.route == permission.route)
            )
            .first()
        )

        errors = {}
        if permission.name == "" or permission.route == "":
            errors["name"] = "Name cannot empty" if permission.name == "" else ""
            errors["route"] = "Route cannot empty" if permission.route == "" else ""

            return response(
                code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                message="Unique constraint violation",
                type="error",
                data=errors,
            )

        if existing_permission:
            if existing_permission.name == permission.name:
                errors["name"] = "The name must be unique"
            if existing_permission.route == permission.route:
                errors["route"] = "The route must be unique"

            return response(
                code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                message="Unique constraint violation",
                type="error",
                data=errors,
            )

        # Nếu không có lỗi, thêm permission vào DB
        new_permission = Permission(**permission.dict())
        new_permission.id = str(uuid4())

        db.add(new_permission)
        db.commit()

        return response(
            code=status.HTTP_201_CREATED,
            message="Create permission success",
            type="info",
            data=permission,
        )

    except IntegrityError as e:
        db.rollback()
        return response(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Database error",
            type="error",
            data={"error": "Server Internal errror"},
        )


@permission_router.put("/{permission_id}", status_code=status.HTTP_200_OK)
async def update_permission(
    permission_id: str, permission: PermissionEntity, db: db_dependency
):
    # Lấy permission hiện tại từ DB
    db_permission = db.query(Permission).filter(Permission.id == permission_id).first()

    # Nếu không tìm thấy permission
    if not db_permission:
        return response(
            code=status.HTTP_404_NOT_FOUND,
            message="Permission not found",
            type="error",
            data={},
        )

    # Kiểm tra name và route không được trống và duy nhất
    errors = {}
    if permission.name == "" or permission.route == "":
        errors["name"] = "Name cannot be empty" if permission.name == "" else ""
        errors["route"] = "Route cannot be empty" if permission.route == "" else ""

        return response(
            code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message="Validation error",
            type="error",
            data=errors,
        )

    # Kiểm tra xem tên và route có trùng với bất kỳ permission nào đã tồn tại không
    existing_permission = (
        db.query(Permission)
        .filter(
            (Permission.name == permission.name) & (Permission.id != permission_id)
            | (Permission.route == permission.route) & (Permission.id != permission_id)
        )
        .first()
    )

    if existing_permission:
        if existing_permission.name == permission.name:
            errors["name"] = "The name must be unique"
        if existing_permission.route == permission.route:
            errors["route"] = "The route must be unique"

        return response(
            code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message="Unique constraint violation",
            type="error",
            data=errors,
        )

    # Cập nhật các trường của permission
    db_permission.name = permission.name
    db_permission.route = permission.route
    db_permission.is_deleted = (
        permission.is_deleted
    )  # Nếu có trường is_deleted thay đổi
    db_permission.updated_at = datetime.utcnow()  # Cập nhật thời gian

    db.commit()

    return response(
        code=status.HTTP_200_OK,
        message="Permission updated successfully",
        type="info",
        data=permission,
    )


@permission_router.delete("/{permission_id}", status_code=status.HTTP_200_OK)
async def delete_permission(permission_id: str, db: db_dependency):
    # Lấy permission hiện tại từ DB
    db_permission = db.query(Permission).filter(Permission.id == permission_id).first()

    # Nếu không tìm thấy permission
    if not db_permission:
        return response(
            code=status.HTTP_404_NOT_FOUND,
            message="Permission not found",
            type="error",
            data={"id": permission_id},
        )

    # Đánh dấu permission là đã xóa hoặc có thể xóa thực tế tùy theo yêu cầu
    db_permission.is_deleted = True  # Nếu không xóa trực tiếp mà chỉ đánh dấu
    db.commit()

    return response(
        code=status.HTTP_200_OK,
        message="Permission deleted successfully",
        type="info",
        data={"id": permission_id},
    )
