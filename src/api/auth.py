from typing import Annotated

from fastapi import Depends
from fastapi.responses import RedirectResponse
from fastapi.routing import APIRouter

from db.models import ProviderType
from depends import get_auth_service
from services.auth.providers.base import OAuthProvider

router = APIRouter()


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
