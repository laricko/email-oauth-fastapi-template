from typing import Annotated

from fastapi import Depends
from fastapi.responses import RedirectResponse
from fastapi.routing import APIRouter
from pydantic import BaseModel

from db.models import ProviderType
from depends import get_oauth_service, get_token_service
from services.auth.dtos import GenerateTokenData
from services.auth.providers.base import OAuthProvider
from services.auth.tokens import AuthService

router = APIRouter(tags=["auth"], prefix="/auth")


@router.get("/{provider}/start")
async def auth_start(
    provider: ProviderType,
    oauth_service: Annotated[OAuthProvider, Depends(get_oauth_service)],
):
    return await oauth_service.get_auth_url()


@router.get("/{provider}/callback")
async def auth_callback(
    provider: str,
    oauth_service: Annotated[OAuthProvider, Depends(get_oauth_service)],
    code: str,
    state: str,
):
    url = await oauth_service.handle_callback(code, state)
    return RedirectResponse(url=url)


@router.post("/token")
async def token(
    data: GenerateTokenData,
    token_service: Annotated[AuthService, Depends(get_token_service)],
):
    return await token_service.issue_access_token(data)
