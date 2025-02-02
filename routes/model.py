from typing import List
from datetime import datetime
from models.model import Model 
from schema.model import ModelEntity 
from database.database import db_dependency
from schema.response import ResponseMessage
from fastapi.exceptions import RequestValidationError
from fastapi import APIRouter, status, Depends, HTTPException

model_router = APIRouter(prefix="/models", tags=["models"])

@model_router.get("", status_code=status.HTTP_200_OK, name="Get all model")
async def fetch_all(db: db_dependency, skip: int = 0, limit: int = 100):
    try:
        query = (
            db.query(Model)
            .filter(Model.is_deleted == False)
            .offset(skip)
            .limit(limit)
        )
        model: List[Model] = query.all()

        return ResponseMessage(
            code=status.HTTP_200_OK,
            message="Fetch all model success",
            data=model
        )

    except Exception as e:
        db.rollback()
        return ResponseMessage(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"Database error: {str(e)}",
        )

@model_router.get("/{model_id}", status_code=status.HTTP_200_OK, name="Get model by id")
async def fetch_detail(model_id: int, db: db_dependency):
    try:
        model: Model = (
            db.query(Model)
            .filter(Model.id == model_id, Model.is_deleted == False)
            .first()
        )

        if not model:
            return ResponseMessage(
                code=status.HTTP_404_NOT_FOUND,
                message=f"Prompt with ID {model_id} not found.",
            )

        return ResponseMessage(
            code=status.HTTP_200_OK,
            message=f"Fetch prompt with id {model_id} success",
            data=model,
        )

    except Exception as e:
        db.rollback()
        return ResponseMessage(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"Database error: {str(e)}",
        )

@model_router.post("", status_code=status.HTTP_201_CREATED, name="Add new model")
async def create(model_item: ModelEntity, db: db_dependency):
    try:
        IS_EMPTY_ENTITY = model_item.name == "" or model_item.detail_name == "" or model_item.type == ""
        IS_UNDEFINED_ENTITY = model_item.name is None or model_item.detail_name is None or model_item.type is None
        if IS_EMPTY_ENTITY or IS_UNDEFINED_ENTITY: 
            return ResponseMessage(
                code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                message="Entity error",
                data={"error": "Model 'name' or 'detail name' cannot be empty"},
            )

        new_model = Model(**model_item.dict())

        db.add(new_model)
        db.commit()
        db.refresh(new_model)

        return ResponseMessage(
            code=status.HTTP_201_CREATED,
            message="Model created successfully",
            data=new_model,
        )

    except Exception as e:
        db.rollback()
        return ResponseMessage(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"Database error: {str(e)}",
        )

@model_router.put("/{model_id}", status_code=status.HTTP_200_OK, name="Update model")
async def update(model_id: int, model_item: ModelEntity, db: db_dependency):
    try:
        model: Model = (
            db.query(Model)
            .filter(Model.id == model_id, Model.is_deleted == False)
            .first()
        )

        if not model:
            return ResponseMessage(
                code=status.HTTP_404_NOT_FOUND,
                message=f"Prompt with ID {prompt_id} not found.",
            )

        model.name = model_item.name
        model.detail_name = model_item.detail_name
        model.type = model_item.type
        model.updated_at = datetime.now()

        db.commit()
        db.refresh(model)

        return ResponseMessage(
            code=status.HTTP_200_OK,
            message="Model updated successfully",
            data=model
        )

    except Exception as e:
        db.rollback()
        return ResponseMessage(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"Database error: {str(e)}",
        )

@model_router.delete("/{model_id}", status_code=status.HTTP_200_OK, name="Delete prompt")
async def delete(model_id: int, db: db_dependency):
    try:
        model: Model = (
            db.query(Model)
            .filter(Model.id == model_id, Model.is_deleted == False)
            .first()
        )

        if not model:
            return ResponseMessage(
                code=status.HTTP_404_NOT_FOUND,
                message=f"Model {model.name} not found.",
            )
        
        model.is_deleted = True
        db.commit()

        return ResponseMessage(
            code=status.HTTP_200_OK,
            message="Model deleted successfully",
            data=model
        )

    except Exception as e:
        db.rollback()
        return ResponseMessage(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"Database error: {str(e)}",
        )