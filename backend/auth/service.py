import random
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from db.models.user import User
from backend.auth.schemas.post import RegisterRequest, LoginRequest, RefreshTokenRequest
from backend.auth.schemas.get import UserResponse
from backend.auth.schemas.token import TokenResponse
from backend.auth.security import create_access_token, create_refresh_token, decode_token
from backend.auth.dependencies import check_user_account_age


async def generate_and_store_otp(redis: Redis, phone: str) -> str:
    otp = f"{random.randint(100000, 999999)}"
    # Store OTP in Redis with 180s (3-minute) TTL
    await redis.set(name=f"otp:{phone}", value=otp, ex=180)
    return otp


async def register_user(db: AsyncSession, redis: Redis, payload: RegisterRequest) -> TokenResponse:
    # 1. Verify OTP
    stored_otp = await redis.get(f"otp:{payload.phone}")
    if not stored_otp or stored_otp != payload.otp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP code"
        )

    # 2. Check if phone already registered
    stmt = select(User).where(User.phone == payload.phone)
    res = await db.execute(stmt)
    existing_user = res.scalar_one_or_none()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this phone number is already registered"
        )

    # 3. Create User only
    user = User(
        first_name=payload.first_name,
        last_name=payload.last_name,
        age=payload.age,
        phone=payload.phone,
        role=payload.role,
        is_active=True,
    )
    db.add(user)
    await db.commit()

    # Reload user with firm relationship
    user_stmt = select(User).options(selectinload(User.firm)).where(User.id == user.id)
    user_res = await db.execute(user_stmt)
    user = user_res.scalar_one()

    # Consume OTP
    await redis.delete(f"otp:{payload.phone}")

    # Generate tokens
    access_token = create_access_token(subject=user.id)
    refresh_token = create_refresh_token(subject=user.id)

    user_resp = UserResponse.model_validate(user)
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=user_resp,
    )


async def login_user(db: AsyncSession, redis: Redis, payload: LoginRequest) -> TokenResponse:
    # 1. Verify OTP
    stored_otp = await redis.get(f"otp:{payload.phone}")
    if not stored_otp or stored_otp != payload.otp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP code"
        )

    # 2. Fetch User
    stmt = select(User).options(selectinload(User.firm)).where(User.phone == payload.phone)
    res = await db.execute(stmt)
    user = res.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found or account is deactivated"
        )

    # 3. Check 9-month account age limit
    check_user_account_age(user)

    # Consume OTP
    await redis.delete(f"otp:{payload.phone}")

    # Generate tokens
    access_token = create_access_token(subject=user.id)
    refresh_token = create_refresh_token(subject=user.id)

    user_resp = UserResponse.model_validate(user)
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=user_resp,
    )


async def refresh_tokens(db: AsyncSession, payload: RefreshTokenRequest) -> TokenResponse:
    decoded = decode_token(payload.refresh_token)
    if not decoded or decoded.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )

    user_id_str = decoded.get("sub")
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )

    user_id = int(user_id_str)
    stmt = select(User).options(selectinload(User.firm)).where(User.id == user_id)
    res = await db.execute(stmt)
    user = res.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or deactivated"
        )

    check_user_account_age(user)

    access_token = create_access_token(subject=user.id)
    new_refresh_token = create_refresh_token(subject=user.id)

    user_resp = UserResponse.model_validate(user)
    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        user=user_resp,
    )
