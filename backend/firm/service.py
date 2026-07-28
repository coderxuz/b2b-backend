from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from db.models.user import User, UserRole
from db.models.tariff import Tariff
from db.models.firm import Firm
from backend.firm.schemas.post import CreateFirmRequest
from backend.firm.schemas.get import FirmDetailResponse
from backend.firm.schemas.patch import UpdateFirmStatusRequest


async def create_firm_service(
    db: AsyncSession,
    user: User,
    payload: CreateFirmRequest,
) -> FirmDetailResponse:
    if user.role != UserRole.DISTRIBUTOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only users with distributor role can create a firm"
        )

    # Check if firm already exists for user
    existing_stmt = select(Firm).where(Firm.owner_id == user.id)
    res = await db.execute(existing_stmt)
    if res.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already have a firm created"
        )

    # Get or create default Free Tariff
    tariff_stmt = select(Tariff).where(Tariff.name == "Free")
    tariff_res = await db.execute(tariff_stmt)
    tariff = tariff_res.scalar_one_or_none()
    if not tariff:
        tariff = Tariff(name="Free", max_shops=50)
        db.add(tariff)
        await db.flush()

    firm = Firm(
        owner_id=user.id,
        tariff_id=tariff.id,
        name=payload.name,
        inn=payload.inn,
        mfo=payload.mfo,
        address=payload.address,
        location=payload.location,
        firm_category=payload.firm_category,
        description=payload.description,
        additional_phones=payload.additional_phones,
        is_active=True,
    )
    db.add(firm)
    await db.commit()
    await db.refresh(firm)

    return FirmDetailResponse.model_validate(firm)


async def get_my_firm_service(
    db: AsyncSession,
    user: User,
) -> FirmDetailResponse:
    stmt = select(Firm).where(Firm.owner_id == user.id)
    res = await db.execute(stmt)
    firm = res.scalar_one_or_none()
    if not firm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Firm not found for this user"
        )
    return FirmDetailResponse.model_validate(firm)


async def list_firms_admin_service(
    db: AsyncSession,
    limit: int = 10,
    offset: int = 0,
) -> List[FirmDetailResponse]:
    stmt = select(Firm).order_by(Firm.id).limit(limit).offset(offset)
    res = await db.execute(stmt)
    firms = res.scalars().all()
    return [FirmDetailResponse.model_validate(f) for f in firms]


async def get_firm_by_id_service(
    db: AsyncSession,
    firm_id: int,
) -> FirmDetailResponse:
    stmt = select(Firm).where(Firm.id == firm_id)
    res = await db.execute(stmt)
    firm = res.scalar_one_or_none()
    if not firm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Firm not found"
        )
    return FirmDetailResponse.model_validate(firm)


async def update_firm_status_service(
    db: AsyncSession,
    firm_id: int,
    payload: UpdateFirmStatusRequest,
) -> FirmDetailResponse:
    stmt = select(Firm).where(Firm.id == firm_id)
    res = await db.execute(stmt)
    firm = res.scalar_one_or_none()
    if not firm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Firm not found"
        )

    firm.is_active = payload.is_active
    await db.commit()
    await db.refresh(firm)

    return FirmDetailResponse.model_validate(firm)
