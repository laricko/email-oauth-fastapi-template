from typing import Annotated, AsyncGenerator

import redis.asyncio as redis
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from config import Settings, get_settings
from db.models import ProviderType
from db.utils import sessionmaker
from services.auth.provider_registry import get_oauth_provider
from services.auth.providers.base import OAuthProvider


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with sessionmaker() as session:
        yield session


async def get_redis_client(
    settings: Annotated[Settings, Depends(get_settings)],
) -> AsyncGenerator[redis.Redis, None]:
    redis_client = redis.Redis.from_url(settings.redis_dsn)
    try:
        yield redis_client
    finally:
        await redis_client.close()


async def get_auth_service(
    provider: ProviderType,
    settings: Annotated[Settings, Depends(get_settings)],
    redis: Annotated[redis.Redis, Depends(get_redis_client)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> OAuthProvider:
    return get_oauth_provider(provider, settings, session, redis)
