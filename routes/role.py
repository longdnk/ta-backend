from typing import List
from models.role import Role
from datetime import datetime
from schema.role import RoleEntity
from models.permission import Permission
from database.database import db_dependency
from schema.response import ResponseMessage
from fastapi.exceptions import RequestValidationError
from fastapi import APIRouter, status, Depends, HTTPException

role_router = APIRouter(prefix="/roles", tags=["roles"])

@role_router.get("", status_code=status.HTTP_200_OK, name="Get all role")
async def fetch_all(db: db_dependency, skip: int = 0, limit: int = 100):
    try:
        query = (
            db.query(Role)
            .filter(Role.is_deleted == False)
            .offset(skip)
            .limit(limit)
        )
        roles: List[Role] = query.all()

        return ResponseMessage(
            code=status.HTTP_200_OK,
            message="Fetch all role success",
            data=roles
        )

    except Exception as e:
        db.rollback()
        return ResponseMessage(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"Database error: {str(e)}",
        )

@role_router.get("/{role_id}", status_code=status.HTTP_200_OK, name="Get role by id")
async def fetch_detail(role_id: int, db: db_dependency):
    try:
        role: Role = (
            db.query(Role)
            .filter(Role.id == role_id, Role.is_deleted == False)
            .first()
        )

        if not role:
            return ResponseMessage(
                code=status.HTTP_404_NOT_FOUND,
                message=f"Role with ID {role_id} not found.",
            )

        permissions = (
            db.query(Permission)
            .filter(Permission.id.in_(role.permission_ids))
            .all()
        )

        role_data = role.to_dict()
        role_data['permissions'] = [permission.to_dict() for permission in permissions]

        return ResponseMessage(
            code=status.HTTP_200_OK,
            message=f"Fetch role with id {role_id} success",
            data=role_data,
        )

    except Exception as e:
        db.rollback()
        return ResponseMessage(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"Database error: {str(e)}",
        )

@role_router.post("", status_code=status.HTTP_201_CREATED, name="Add new role")
async def create(role_item: RoleEntity, db: db_dependency):
    try:
        existing_role = db.query(Role).filter(Role.name == role_item.name).first()
        if existing_role:
            return ResponseMessage(
                code=status.HTTP_400_BAD_REQUEST,
                message=f"Role {role_item.name} already exists.",
            )

        permission_ids = role_item.permission_ids if role_item.permission_ids else [] 
        existing_permissions = db.query(Permission).filter(Permission.id.in_(permission_ids)).all()
        existing_permission_ids = [permission.id for permission in existing_permissions]

        missing_permission_ids = set(permission_ids) - set(existing_permission_ids)
        if missing_permission_ids:
            return ResponseMessage(
                code=status.HTTP_400_BAD_REQUEST,
                message="Permission id is not exist",
                data={"detail":f"Permissions with IDs {missing_permission_ids} do not exist."}
            )

        new_role = Role(**role_item.dict())

        db.add(new_role)
        db.commit()
        db.refresh(new_role)
        return ResponseMessage(
            code=status.HTTP_201_CREATED,
            message="Role created successfully",
            data=new_role,
        )

    except Exception as e:
        db.rollback()
        return ResponseMessage(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"Database error: {str(e)}",
        )

@role_router.put("/{role_id}", status_code=status.HTTP_200_OK, name="Update role")
async def update_role(role_id: int, role_item: RoleEntity, db: db_dependency):
    role: Role = db.query(Role).filter(Role.id == role_id, Role.is_deleted == False).first()
    if not role:
        return ResponseMessage(
            code=status.HTTP_404_NOT_FOUND,
            message=f"Role with ID {role_id} not found.",
        )

    existing_role = db.query(Role).filter(Role.name == role_item.name).first()
    if existing_role and existing_role.id != role_id:
        return ResponseMessage(
            code=status.HTTP_400_BAD_REQUEST,
            message=f"Role with name '{role_item.name}' already exists."
        )

    permission_ids = role_item.permission_ids if role_item.permission_ids else []  # Đảm bảo sử dụng permission_ids
    existing_permissions = db.query(Permission).filter(Permission.id.in_(permission_ids)).all()
    existing_permission_ids = [permission.id for permission in existing_permissions]

    missing_permission_ids = set(permission_ids) - set(existing_permission_ids)
    if missing_permission_ids:
        return ResponseMessage(
            code=status.HTTP_400_BAD_REQUEST,
            message=f"Permissions with IDs {missing_permission_ids} do not exist."
        )

    role.name = role_item.name
    role.permission_ids = permission_ids  
    role.updated_at = datetime.now()

    db.commit()
    db.refresh(role)

    return ResponseMessage(
        code=status.HTTP_200_OK,
        message="Role updated successfully.",
        data=role.to_dict()
    )

@role_router.delete("/{role_id}", status_code=status.HTTP_200_OK, name="Delete role")
async def delete(role_id: int, db: db_dependency):
    try:
        role: Role = db.query(Role).filter(Role.id == role_id, Role.is_deleted == False).first()
        if not role:
            return ResponseMessage(
                code=status.HTTP_404_NOT_FOUND,
                message=f"Role with ID {role_id} not found."
            )

        role.is_deleted = True
        db.commit()
        db.refresh(role)

        return ResponseMessage(
            code=status.HTTP_200_OK,
            message=f"Role with ID {role_id} has been soft deleted successfully.",
            data=role
        )
    except Exception as e:
        db.rollback()
        return ResponseMessage(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"Database error: {str(e)}",
        )