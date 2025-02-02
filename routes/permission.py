from typing import List
from datetime import datetime
from typing import List, Optional
from models.permission import Permission
from database.database import db_dependency
from schema.response import ResponseMessage
from schema.permission import PermissionEntity
from fastapi import APIRouter, status, Depends, HTTPException

permission_router = APIRouter(prefix="/permissions", tags=["permissions"])

@permission_router.get("", status_code=status.HTTP_200_OK, name="Get all permission")
async def fetch_all(db: db_dependency, skip: int = 0, limit: int = 100):
    try:
        query = (
            db.query(Permission)
            .filter(Permission.is_deleted == False)
            .offset(skip)
            .limit(limit)
        )

        permissions: List[Permission] = query.all()

        return ResponseMessage(
            code=status.HTTP_200_OK,
            message="Fetch all permission success",
            data=permissions,
        )

    except Exception as e:
        db.rollback()
        return ResponseMessage(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"Database error: {str(e)}",
        )

@permission_router.get("/{permission_id}", status_code=status.HTTP_200_OK, name="Get permission by id")
async def fetch_detail(permission_id: int, db: db_dependency):
    try:
        permission: Permission = (
            db.query(Permission)
            .filter(Permission.id == permission_id, Permission.is_deleted == False)
            .first()
        )

        if not permission:
            return ResponseMessage(
                code=status.HTTP_404_NOT_FOUND,
                message=f"Permission with ID {permission_id} not found.",
            )

        return ResponseMessage(
            code=status.HTTP_200_OK,
            message=f"Fetch permission with id {permission_id} success",
            data=permission,
        )

    except Exception as e:
        db.rollback()
        return ResponseMessage(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"Database error: {str(e)}",
        )

@permission_router.post("", status_code=status.HTTP_201_CREATED, name="Add new permission")
async def create(permission_item: PermissionEntity, db: db_dependency):
    try:
        existing_permission = (
            db.query(Permission)
            .filter(
                Permission.name == permission_item.name,
                Permission.route == permission_item.route,
            )
            .first()
        )

        if existing_permission:
            return ResponseMessage(
                code=status.HTTP_400_BAD_REQUEST,
                message="Permission with this name and route already exists.",
            )

        new_permission = Permission(**permission_item.dict())

        db.add(new_permission)
        db.commit()
        db.refresh(new_permission)

        return ResponseMessage(
            code=status.HTTP_201_CREATED,
            message="Permission created successfully",
            data=new_permission,
        )

    except Exception as e:
        db.rollback()
        return ResponseMessage(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"Database error: {str(e)}",
        )

@permission_router.put("/{permission_id}", status_code=status.HTTP_200_OK, name="Update permission")
async def update(
    permission_id: int, permission_item: PermissionEntity, db: db_dependency
):
    try:
        permission: Permission = (
            db.query(Permission)
            .filter(Permission.id == permission_id, Permission.is_deleted == False)
            .first()
        )

        if not permission:
            return ResponseMessage(
                code=status.HTTP_404_NOT_FOUND,
                message=f"Permission with ID {permission_id} not found.",
            )

        permission.name = permission_item.name
        permission.updated_at = datetime.now()

        db.commit()
        db.refresh(permission)

        return ResponseMessage(
            code=status.HTTP_200_OK,
            message="Permission updated successfully",
            data=permission,
        )

    except Exception as e:
        db.rollback()
        return ResponseMessage(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"Database error: {str(e)}",
        )

@permission_router.delete("/{permission_id}", status_code=status.HTTP_200_OK, name="Delete permission")
async def delete(permission_id: int, db: db_dependency):
    try:
        permission: Permission = (
            db.query(Permission)
            .filter(Permission.id == permission_id, Permission.is_deleted == False)
            .first()
        )

        if not permission:
            return ResponseMessage(
                code=status.HTTP_404_NOT_FOUND,
                message=f"Permission with ID {permission_id} not found.",
            )
        
        permission.is_deleted = True
        db.commit()

        return ResponseMessage(
            code=status.HTTP_200_OK,
            message="Permission deleted successfully",
            data=permission,
        )

    except Exception as e:
        db.rollback()
        return ResponseMessage(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"Database error: {str(e)}",
        )