from typing import Annotated, AsyncGenerator

import redis.asyncio as redis
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from config import Settings, get_settings
from db.utils import sessionmaker
from services.auth.google import GoogleAuthService


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with sessionmaker() as session:
        yield session


async def get_redis(
    settings: Annotated[Settings, Depends(get_settings)]
) -> AsyncGenerator[redis.Redis, None]:
    redis_client = redis.Redis.from_url(settings.redis_dsn)
    try:
        yield redis_client
    finally:
        await redis_client.aclose()


async def get_google_auth_service(
    settings: Annotated[Settings, Depends(get_settings)],
    session: Annotated[AsyncSession, Depends(get_session)],
    redis: Annotated[redis.Redis, Depends(get_redis)]
) -> GoogleAuthService:
    return GoogleAuthService(settings, session, redis)
