from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from db.models.product_category import ProductCategory
from backend.category.schemas.post import CreateCategoryRequest
from backend.category.schemas.patch import UpdateCategoryRequest
from backend.category.schemas.get import CategoryResponse


async def create_category_service(
    db: AsyncSession,
    payload: CreateCategoryRequest,
) -> CategoryResponse:
    stmt = select(ProductCategory).where(ProductCategory.name == payload.name)
    res = await db.execute(stmt)
    if res.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category with this name already exists"
        )

    category = ProductCategory(name=payload.name)
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return CategoryResponse.model_validate(category)


async def list_categories_service(
    db: AsyncSession,
) -> List[CategoryResponse]:
    stmt = select(ProductCategory).order_by(ProductCategory.id)
    res = await db.execute(stmt)
    categories = res.scalars().all()
    return [CategoryResponse.model_validate(c) for c in categories]


async def get_category_service(
    db: AsyncSession,
    category_id: int,
) -> CategoryResponse:
    stmt = select(ProductCategory).where(ProductCategory.id == category_id)
    res = await db.execute(stmt)
    category = res.scalar_one_or_none()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    return CategoryResponse.model_validate(category)


async def update_category_service(
    db: AsyncSession,
    category_id: int,
    payload: UpdateCategoryRequest,
) -> CategoryResponse:
    stmt = select(ProductCategory).where(ProductCategory.id == category_id)
    res = await db.execute(stmt)
    category = res.scalar_one_or_none()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    category.name = payload.name
    await db.commit()
    await db.refresh(category)
    return CategoryResponse.model_validate(category)


async def delete_category_service(
    db: AsyncSession,
    category_id: int,
) -> None:
    stmt = select(ProductCategory).where(ProductCategory.id == category_id)
    res = await db.execute(stmt)
    category = res.scalar_one_or_none()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    await db.delete(category)
    await db.commit()
