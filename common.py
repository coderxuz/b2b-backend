import os
from dotenv import load_dotenv, find_dotenv
from redis.asyncio import Redis

load_dotenv(find_dotenv(usecwd=True))


def get_redis_client() -> Redis:
    host = os.getenv("REDIS_HOST", "localhost")
    port = int(os.getenv("REDIS_PORT", 6380))
    password = os.getenv("REDIS_PASSWORD")
    return Redis(
        host=host,
        port=port,
        password=password,
        decode_responses=True,
    )


async def get_redis_db():
    client = get_redis_client()
    try:
        yield client
    finally:
        await client.aclose()
