import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession

from config import Settings
from services.auth.providers.base import OAuthProvider
from services.auth.providers.google import GoogleOAuthProvider

_PROVIDER_REGISTRY = {
    "google": GoogleOAuthProvider,
}


def get_oauth_provider(
    provider_name: str,
    settings: Settings,
    session: AsyncSession,
    redis: redis.Redis
) -> OAuthProvider:
    return _PROVIDER_REGISTRY[provider_name](settings, session, redis)
