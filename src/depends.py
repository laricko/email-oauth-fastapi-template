from typing import Annotated, AsyncGenerator

from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from config import Settings, get_settings
from db.utils import sessionmaker
from services.auth.provider_registry import get_oauth_provider
from services.auth.providers.base import OAuthProvider


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with sessionmaker() as session:
        yield session


async def get_auth_service(
    provider: str,
    settings: Annotated[Settings, Depends(get_settings)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> OAuthProvider:
    try:
        return get_oauth_provider(provider, settings, session)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
