from fastapi import APIRouter, status, HTTPException, Request
from models.prompt.prompt import Prompt, PromptEntity
from response.response_item import response
from database.database import db_dependency
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from datetime import datetime
from uuid import uuid4

prompt_router = APIRouter(prefix="/prompts", tags=["prompts"])

@prompt_router.get("", status_code=status.HTTP_200_OK)
async def get_prompts(
    request: Request, db: db_dependency, skip: int = 0, limit: int = 100
):
    prompt = (
        db.query(Prompt)
        .filter(Prompt.is_deleted == False)
        .order_by(Prompt.created_at.asc())
        .all()
    )

    if prompt is None:
        return response(
            code=status.HTTP_400_BAD_REQUEST,
            message="Cannot find Prompt list",
            type="error",
            data=[],
        )

    return response(
        code=status.HTTP_200_OK,
        message="OK",
        type="info",
        data=prompt[skip : skip + limit],
    )


@prompt_router.post("", status_code=status.HTTP_201_CREATED)
async def create_prompt(
    request: Request, prompt_entity: PromptEntity, db: db_dependency
):
    try:
        # Kiểm tra dữ liệu đầu vào
        if prompt_entity.content == "":
            return response(
                code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                message="Content cannot be empty",
                type="error",
                data={"content": "Content cannot be empty"},
            )

        # Tạo Prompt mới
        new_prompt = Prompt(**prompt_entity.dict())
        new_prompt.id = str(uuid4())

        db.add(new_prompt)
        db.commit()

        return response(
            code=status.HTTP_201_CREATED,
            message="Prompt created successfully",
            type="info",
            data={
                "id": new_prompt.id,
                "content": new_prompt.content,
            },
        )
    except IntegrityError:
        db.rollback()
        return response(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Database error",
            type="error",
            data={"error": "Server Internal errror"},
        )


@prompt_router.get("/{prompt_id}", status_code=status.HTTP_200_OK)
async def get_prompt(prompt_id: str, db: db_dependency):
    prompt: Prompt = (
        db.query(Prompt)
        .filter(Prompt.id == prompt_id, Prompt.is_deleted == False)
        .first()
    )

    if not prompt:
        return response(
            code=status.HTTP_404_NOT_FOUND,
            message="Prompt not found",
            type="error",
            data={"error": "Cannot find prompt"},
        )

    return response(
        code=status.HTTP_200_OK,
        message="OK",
        type="info",
        data=prompt,
    )


@prompt_router.put("/{prompt_id}", status_code=status.HTTP_200_OK)
async def update_prompt(prompt_id: str, prompt_entity: PromptEntity, db: db_dependency):

    prompt: Prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()

    if not prompt:
        return response(
            code=status.HTTP_404_NOT_FOUND,
            message="Prompt not found",
            type="error",
            data={"error": f"Cannot find prompt with id {prompt_id}"},
        )

    # Kiểm tra dữ liệu đầu vào
    if prompt_entity.content == "":
        return response(
            code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message="Content cannot be empty",
            type="error",
            data={"content": "Content cannot be empty"},
        )

    # Cập nhật nội dung của Prompt
    prompt.content = prompt_entity.content
    prompt.is_deleted = prompt_entity.is_deleted
    prompt.updated_at = datetime.utcnow()

    db.commit()

    return response(
        code=status.HTTP_200_OK,
        message="Prompt updated successfully",
        type="info",
        data={"id": prompt.id, "content": prompt.content},
    )


@prompt_router.delete("/{prompt_id}", status_code=status.HTTP_200_OK)
async def delete_prompt(prompt_id: str, db: db_dependency):
    prompt: Prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()

    if not prompt:
        return response(
            code=status.HTTP_404_NOT_FOUND,
            message="Prompt not found",
            type="error",
            data={"error": "Cannot find prompt item"},
        )

    # Đánh dấu Prompt là đã xóa
    prompt.is_deleted = True
    prompt.updated_at = datetime.utcnow()

    db.commit()

    return response(
        code=status.HTTP_200_OK,
        message="Prompt deleted successfully",
        type="info",
        data={"id": prompt_id},
    )
