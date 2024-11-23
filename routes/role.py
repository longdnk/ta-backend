from fastapi import APIRouter, status, HTTPException, Request
from models.permission.permission import Permission
from models.role.role import Role, RoleEntity
from response.response_item import response
from database.database import db_dependency
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from datetime import datetime
from uuid import uuid4

role_router = APIRouter(prefix="/roles", tags=["roles"])


@role_router.get("", status_code=status.HTTP_200_OK)
async def get_roles(
    request: Request, db: db_dependency, skip: int = 0, limit: int = 100
):
    roles = (
        db.query(Role)
        .filter(Role.is_deleted == False)
        .order_by(Role.created_at.asc())
        .all()
    )

    if roles is None:
        return response(
            code=status.HTTP_404_NOT_FOUND,
            message="Cannot find role list",
            type="error",
            data=[],
        )

    return response(
        code=status.HTTP_200_OK,
        message="OK",
        type="info",
        data=roles[skip : skip + limit],
    )

@role_router.post("", status_code=status.HTTP_201_CREATED)
async def create_role(request: Request, role_entity: RoleEntity, db: db_dependency):
    try:
        # Kiểm tra tên vai trò không được rỗng
        if role_entity.name == "":
            return response(
                code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                message="Role name cannot be empty",
                type="error",
                data={"name": "Role name cannot be empty"},
            )

        # Kiểm tra tên vai trò đã tồn tại chưa
        existing_role = (
            db.query(Role)
            .filter(Role.name == role_entity.name, Role.is_deleted == False)
            .first()
        )
        if existing_role:
            return response(
                code=status.HTTP_409_CONFLICT,
                message="Role name already exists",
                type="error",
                data={"name": f"Role with name '{role_entity.name}' already exists"},
            )

        # Kiểm tra các permission_ids có tồn tại không
        invalid_permissions = [
            perm_id
            for perm_id in role_entity.permission_ids
            if not db.query(Permission).filter(Permission.id == perm_id).first()
        ]

        if invalid_permissions:
            return response(
                code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                message="Invalid permission IDs",
                type="error",
                data={"invalid_permission_ids": invalid_permissions},
            )

        # Tạo vai trò mới
        new_role = Role(**role_entity.dict())
        new_role.id = str(uuid4())

        db.add(new_role)
        db.commit()

        return response(
            code=status.HTTP_201_CREATED,
            message="Role created successfully",
            type="info",
            data={
                "id": new_role.id,
                "name": new_role.name,
                "permission_ids": new_role.permission_ids,
            },
        )
    except IntegrityError:
        db.rollback()
        return response(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Database error",
            type="error",
            data={"error": "Server Internal Error"},
        )

@role_router.get("/{role_id}", status_code=status.HTTP_200_OK)
async def get_role(role_id: str, db: db_dependency):
    role: Role = (
        db.query(Role).filter(Role.id == role_id, Role.is_deleted == False).first()
    )

    if not role:
        return response(
            code=status.HTTP_404_NOT_FOUND,
            message="Role not found",
            type="error",
            data={"error": "Cannot find role"},
        )

    return response(
        code=status.HTTP_200_OK,
        message="OK",
        type="info",
        data=role,
    )


@role_router.put("/{role_id}", status_code=status.HTTP_200_OK)
async def update_role(role_id: str, role_entity: RoleEntity, db: db_dependency):
    role: Role = db.query(Role).filter(Role.id == role_id).first()

    if not role:
        return response(
            code=status.HTTP_404_NOT_FOUND,
            message="Role not found",
            type="error",
            data={"error": f"Cannot find role with id {role_id}"},
        )

    # Kiểm tra tên vai trò không được rỗng
    if role_entity.name == "":
        return response(
            code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message="Role name cannot be empty",
            type="error",
            data={"name": "Role name cannot be empty"},
        )

    # Kiểm tra các permission_ids có tồn tại không
    invalid_permissions = [
        perm_id
        for perm_id in role_entity.permission_ids
        if not db.query(Permission).filter(Permission.id == perm_id).first()
    ]

    if invalid_permissions:
        return response(
            code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message="Invalid permission IDs",
            type="error",
            data={"invalid_permission_ids": invalid_permissions},
        )

    # Cập nhật thông tin vai trò
    role.name = role_entity.name
    role.permission_ids = role_entity.permission_ids
    role.is_deleted = role_entity.is_deleted
    role.updated_at = datetime.utcnow()

    db.commit()

    return response(
        code=status.HTTP_200_OK,
        message="Role updated successfully",
        type="info",
        data={"id": role.id, "name": role.name, "permission_ids": role.permission_ids},
    )


@role_router.delete("/{role_id}", status_code=status.HTTP_200_OK)
async def delete_role(role_id: str, db: db_dependency):
    role: Role = db.query(Role).filter(Role.id == role_id).first()

    if not role:
        return response(
            code=status.HTTP_404_NOT_FOUND,
            message="Role not found",
            type="error",
            data={"error": "Cannot find role item"},
        )

    # Đánh dấu Role là đã xóa
    role.is_deleted = True
    role.updated_at = datetime.utcnow()

    db.commit()

    return response(
        code=status.HTTP_200_OK,
        message="Role deleted successfully",
        type="info",
        data={"id": role_id},
    )
