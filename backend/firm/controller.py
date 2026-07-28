from typing import List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from db.connection import get_async_db
from db.models.user import User
from backend.auth.dependencies import get_current_user, get_admin_user
from backend.firm.schemas.post import CreateFirmRequest
from backend.firm.schemas.get import FirmDetailResponse
from backend.firm.schemas.patch import UpdateFirmStatusRequest
from backend.firm.service import (
    create_firm_service,
    get_my_firm_service,
    list_firms_admin_service,
    get_firm_by_id_service,
    update_firm_status_service,
)

router = APIRouter(prefix="/firm", tags=["Firm"])


@router.post("", response_model=FirmDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_firm_endpoint(
    payload: CreateFirmRequest,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    return await create_firm_service(db=db, user=current_user, payload=payload)


@router.get("/me", response_model=FirmDetailResponse, status_code=status.HTTP_200_OK)
async def get_my_firm_endpoint(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    return await get_my_firm_service(db=db, user=current_user)


@router.get("/admin/all", response_model=List[FirmDetailResponse], status_code=status.HTTP_200_OK)
async def list_all_firms_admin_endpoint(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_async_db),
    admin_user: User = Depends(get_admin_user),
):
    return await list_firms_admin_service(db=db, limit=limit, offset=offset)


@router.get("/admin/{firm_id}", response_model=FirmDetailResponse, status_code=status.HTTP_200_OK)
async def get_firm_by_id_admin_endpoint(
    firm_id: int,
    db: AsyncSession = Depends(get_async_db),
    admin_user: User = Depends(get_admin_user),
):
    return await get_firm_by_id_service(db=db, firm_id=firm_id)


@router.patch("/{firm_id}/status", response_model=FirmDetailResponse, status_code=status.HTTP_200_OK)
async def update_firm_status_endpoint(
    firm_id: int,
    payload: UpdateFirmStatusRequest,
    db: AsyncSession = Depends(get_async_db),
    admin_user: User = Depends(get_admin_user),
):
    return await update_firm_status_service(db=db, firm_id=firm_id, payload=payload)
