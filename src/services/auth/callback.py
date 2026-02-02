import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession

from config import Settings
from services.auth.crud import CreateUser
from services.auth.providers.base import OAuthProvider
from services.auth.providers.google import GoogleOAuthProvider

_PROVIDER_REGISTRY = {
    "google": GoogleOAuthProvider,
}


class OAuthCallbackService:
    def __init__(
        self,
        provider: OAuthProvider,
        session: AsyncSession,
        redis: redis.Redis,
    ):
        self.provider = provider
        self.session = session
        self.redis = redis

    async def handle_callback(self, code: str, state: str) -> str:
        user_info, tokens = await self.provider.handle_callback(code)
        await CreateUser(self.session).execute(user_info["email"], tokens)
        await self.redis.setex(
            state,
            self.provider.STATE_EXPIRATION_SECONDS,
            user_info["email"],
        )
        return "http://localhost:3000/your-frontend?state=" + state


def get_oauth_provider(
    provider_name: str,
    settings: Settings,
) -> OAuthProvider:
    return _PROVIDER_REGISTRY[provider_name](settings)
