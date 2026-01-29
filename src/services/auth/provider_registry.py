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
) -> OAuthProvider:
    provider_class = _PROVIDER_REGISTRY.get(provider_name)
    if not provider_class:
        raise ValueError(f"Unknown provider: {provider_name}")
    return provider_class(settings, session)
