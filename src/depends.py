from typing import Annotated, AsyncGenerator

import redis.asyncio as redis
from fastapi import Depends
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from config import Settings, get_settings
from db.models import ProviderType
from db.utils import sessionmaker
from services.auth.dtos import UserOut
from services.auth.callback import OAuthCallbackService, get_oauth_provider
from services.auth.providers.base import OAuthProvider
from services.auth.tokens import AuthService
from services.emails.sync import EmailService


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


async def get_token_service(
    settings: Annotated[Settings, Depends(get_settings)],
    redis: Annotated[redis.Redis, Depends(get_redis_client)],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    return AuthService(
        secret_key=settings.secret_key,
        redis=redis,
        session=session,
    )


async def get_current_user(
    credentials: Annotated[str, Depends(HTTPBearer())],
    auth_service: Annotated[AuthService, Depends(get_token_service)],
) -> UserOut:
    return await auth_service.get_current_user(credentials.credentials)


async def get_oauth_service(
    provider: ProviderType,
    settings: Annotated[Settings, Depends(get_settings)],
) -> OAuthProvider:
    return get_oauth_provider(provider, settings)


async def get_oauth_callback_service(
    provider: ProviderType,
    settings: Annotated[Settings, Depends(get_settings)],
    redis: Annotated[redis.Redis, Depends(get_redis_client)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> OAuthCallbackService:
    oauth_provider = get_oauth_provider(provider, settings)
    return OAuthCallbackService(
        provider=oauth_provider,
        session=session,
        redis=redis,
    )


async def get_email_service(
    session: Annotated[AsyncSession, Depends(get_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> EmailService:
    return EmailService(session, settings)
