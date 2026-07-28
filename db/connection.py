from os import getenv
from dotenv import load_dotenv, find_dotenv
from sqlalchemy import BigInteger, create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, mapped_column, Mapped
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool
from typing import AsyncGenerator

load_dotenv(find_dotenv(usecwd=True))

DB_URL = getenv("DB_URL")
assert DB_URL, "DB_URL is required"

ASYNC_DB_URL = getenv("ASYNC_DB_URL")
assert ASYNC_DB_URL, "ASYNC_DB_URL is required"

engine = create_engine(DB_URL)
async_engine = create_async_engine(ASYNC_DB_URL, poolclass=NullPool)

SessionLocal = sessionmaker(bind=engine)
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine, expire_on_commit=False, class_=AsyncSession
)


class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
