from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from db.connection import get_async_db
from common import get_redis_db
from db.models.user import User
from backend.auth.schemas.post import RegisterRequest, LoginRequest, RefreshTokenRequest
from backend.auth.schemas.get import UserResponse
from backend.auth.schemas.token import TokenResponse
from backend.auth.service import register_user, login_user, refresh_tokens
from backend.auth.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register_endpoint(
    payload: RegisterRequest,
    db: AsyncSession = Depends(get_async_db),
    redis: Redis = Depends(get_redis_db),
):
    return await register_user(db=db, redis=redis, payload=payload)


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def login_endpoint(
    payload: LoginRequest,
    db: AsyncSession = Depends(get_async_db),
    redis: Redis = Depends(get_redis_db),
):
    return await login_user(db=db, redis=redis, payload=payload)


@router.post("/refresh", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def refresh_endpoint(
    payload: RefreshTokenRequest,
    db: AsyncSession = Depends(get_async_db),
):
    return await refresh_tokens(db=db, payload=payload)


@router.get("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_me_endpoint(
    current_user: User = Depends(get_current_user),
):
    return UserResponse.model_validate(current_user)
