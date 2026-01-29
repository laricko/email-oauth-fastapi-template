from typing import Annotated

import redis.asyncio as redis
from fastapi import Depends
from fastapi.responses import RedirectResponse
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from config import Settings, get_settings
from db.models import ProviderType
from depends import get_auth_service, get_redis_client, get_session
from services.auth.providers.base import OAuthProvider
from services.auth.tokens import JWTTokens

router = APIRouter(tags=["auth"])


@router.get("/auth/{provider}/start")
async def auth_start(
    provider: ProviderType,
    auth_service: Annotated[OAuthProvider, Depends(get_auth_service)],
):
    return await auth_service.get_auth_url()


@router.get("/auth/{provider}/callback")
async def auth_callback(
    provider: str,
    auth_service: Annotated[OAuthProvider, Depends(get_auth_service)],
    code: str,
    state: str,
):
    url = await auth_service.handle_callback(code, state)
    return RedirectResponse(url=url)


@router.post("/auth/token")
async def token(
    state: str,
    session: Annotated[AsyncSession, Depends(get_session)],
    redis: Annotated[redis.Redis, Depends(get_redis_client)],
    settings: Annotated[Settings, Depends(get_settings)],
):
    return await JWTTokens(
        secret_key=settings.secret_key, 
        session=session, 
        redis=redis
    ).generate_access_jwt_token(sub=state)
