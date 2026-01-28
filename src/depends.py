from typing import Annotated

from fastapi import Depends

from config import Settings, get_settings
from services.auth.google import GoogleAuthService


async def get_db():
    pass


async def get_redis():
    pass


async def get_google_auth_service(
    settings: Annotated[Settings, Depends(get_settings)]
    # db
    # redis
) -> GoogleAuthService:
    return GoogleAuthService(settings)
