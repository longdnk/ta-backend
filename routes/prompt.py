from typing import List
from models.prompt import Prompt 
from datetime import datetime
from schema.prompt import PromptEntity 
from database.database import db_dependency
from schema.response import ResponseMessage
from fastapi.exceptions import RequestValidationError
from fastapi import APIRouter, status, Depends, HTTPException

prompt_router = APIRouter(prefix="/prompts", tags=["prompts"])

@prompt_router.get("", status_code=status.HTTP_200_OK, name="Get all prompt")
async def fetch_all(db: db_dependency, skip: int = 0, limit: int = 100):
    try:
        query = (
            db.query(Prompt)
            .filter(Prompt.is_deleted == False)
            .offset(skip)
            .limit(limit)
        )
        prompts: List[Prompt] = query.all()

        return ResponseMessage(
            code=status.HTTP_200_OK,
            message="Fetch all role success",
            data=prompts
        )

    except Exception as e:
        db.rollback()
        return ResponseMessage(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"Database error: {str(e)}",
        )

@prompt_router.get("/{prompt_id}", status_code=status.HTTP_200_OK, name="Get prompt by id")
async def fetch_detail(prompt_id: int, db: db_dependency):
    try:
        prompt: Prompt = (
            db.query(Prompt)
            .filter(Prompt.id == prompt_id, Prompt.is_deleted == False)
            .first()
        )

        if not prompt:
            return ResponseMessage(
                code=status.HTTP_404_NOT_FOUND,
                message=f"Prompt with ID {prompt_id} not found.",
            )

        return ResponseMessage(
            code=status.HTTP_200_OK,
            message=f"Fetch prompt with id {prompt_id} success",
            data=prompt,
        )

    except Exception as e:
        db.rollback()
        return ResponseMessage(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"Database error: {str(e)}",
        )

@prompt_router.post("", status_code=status.HTTP_201_CREATED, name="Add new prompt")
async def create(prompt_item: PromptEntity, db: db_dependency):
    try:
        if prompt_item.content == "":
            return ResponseMessage(
                code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                message="Entity error",
                data={"error": "Content cannot be empty"},
            )

        new_prompt = Prompt(**prompt_item.dict())

        db.add(new_prompt)
        db.commit()
        db.refresh(new_prompt)

        return ResponseMessage(
            code=status.HTTP_201_CREATED,
            message="Prompt created successfully",
            data=new_prompt,
        )

    except Exception as e:
        db.rollback()
        return ResponseMessage(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"Database error: {str(e)}",
        )

@prompt_router.put("/{prompt_id}", status_code=status.HTTP_200_OK, name="Update prompt")
async def update(prompt_id: int, prompt_item: PromptEntity, db: db_dependency):
    try:
        prompt: Prompt = (
            db.query(Prompt)
            .filter(Prompt.id == prompt_id, Prompt.is_deleted == False)
            .first()
        )

        if not prompt:
            return ResponseMessage(
                code=status.HTTP_404_NOT_FOUND,
                message=f"Prompt with ID {prompt_id} not found.",
            )

        prompt.content = prompt_item.content
        prompt.updated_at = datetime.now()

        db.commit()
        db.refresh(prompt)

        return ResponseMessage(
            code=status.HTTP_200_OK,
            message="Prompt updated successfully",
            data=prompt,
        )

    except Exception as e:
        db.rollback()
        return ResponseMessage(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"Database error: {str(e)}",
        )

@prompt_router.delete("/{prompt_id}", status_code=status.HTTP_200_OK, name="Delete prompt")
async def delete(prompt_id: int, db: db_dependency):
    try:
        prompt: Prompt = (
            db.query(Prompt)
            .filter(Prompt.id == prompt_id, Prompt.is_deleted == False)
            .first()
        )

        if not prompt:
            return ResponseMessage(
                code=status.HTTP_404_NOT_FOUND,
                message=f"Prompt with ID {prompt_id} not found.",
            )
        
        prompt.is_deleted = True
        db.commit()

        return ResponseMessage(
            code=status.HTTP_200_OK,
            message="Prompt deleted successfully",
            data=prompt,
        )

    except Exception as e:
        db.rollback()
        return ResponseMessage(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"Database error: {str(e)}",
        )