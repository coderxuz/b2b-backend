from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from db.connection import get_async_db
from db.models.user import User
from backend.auth.dependencies import get_current_user, get_admin_user
from backend.category.schemas.post import CreateCategoryRequest
from backend.category.schemas.patch import UpdateCategoryRequest
from backend.category.schemas.get import CategoryResponse
from backend.category.service import (
    create_category_service,
    list_categories_service,
    get_category_service,
    update_category_service,
    delete_category_service,
)

router = APIRouter(prefix="/admin/categories", tags=["Admin Category"])


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category_endpoint(
    payload: CreateCategoryRequest,
    db: AsyncSession = Depends(get_async_db),
    admin_user: User = Depends(get_admin_user),
):
    return await create_category_service(db=db, payload=payload)


@router.get("", response_model=List[CategoryResponse], status_code=status.HTTP_200_OK)
async def list_categories_endpoint(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    return await list_categories_service(db=db)


@router.get("/{category_id}", response_model=CategoryResponse, status_code=status.HTTP_200_OK)
async def get_category_endpoint(
    category_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    return await get_category_service(db=db, category_id=category_id)


@router.patch("/{category_id}", response_model=CategoryResponse, status_code=status.HTTP_200_OK)
async def update_category_endpoint(
    category_id: int,
    payload: UpdateCategoryRequest,
    db: AsyncSession = Depends(get_async_db),
    admin_user: User = Depends(get_admin_user),
):
    return await update_category_service(db=db, category_id=category_id, payload=payload)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category_endpoint(
    category_id: int,
    db: AsyncSession = Depends(get_async_db),
    admin_user: User = Depends(get_admin_user),
):
    await delete_category_service(db=db, category_id=category_id)
