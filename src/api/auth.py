from typing import Annotated

from fastapi import Depends
from fastapi.routing import APIRouter

from depends import get_google_auth_service
from services.auth.google import GoogleAuthService

router = APIRouter()


@router.get("/auth/google/start")
async def auth_google_start(
    google_auth_service: Annotated[GoogleAuthService, Depends(get_google_auth_service)],
):
    return await google_auth_service.generate_auth_google()


@router.get("/auth/google/callback")
async def auth_google_callback(
    google_auth_service: Annotated[GoogleAuthService, Depends(get_google_auth_service)],
    code: str,
):
    return await google_auth_service.handle_callback(code)
