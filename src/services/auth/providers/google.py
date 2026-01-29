import secrets
from urllib.parse import urlencode

import httpx
import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession

from config import Settings
from services.auth.crud import CreateUser
from services.auth.dtos import OAuthTokens
from services.auth.providers.base import OAuthProvider


class GoogleOAuthProvider(OAuthProvider):
    def __init__(self, settings: Settings, session: AsyncSession, redis: redis.Redis):
        self.settings = settings
        self.session = session
        self.redis = redis

    async def get_auth_url(self) -> str:
        state = secrets.token_urlsafe(16)
        params = {
            "client_id": self.settings.google_client_id,
            "redirect_uri": self.settings.google_redirect_uri,
            "response_type": "code",
            "scope": " ".join(self.settings.google_scopes),
            "access_type": "offline",
            "prompt": "select_account",
            "state": state,
        }

        return f"{self.settings.google_auth_url}?{urlencode(params)}"

    async def handle_callback(self, code: str, state: str) -> str:
        tokens = await self._exchange_code(code)
        user_info = await self._get_user_info(tokens.access_token)
        await self._create_user(user_info, tokens)
        await self.redis.setex(
            state,
            self.STATE_EXPIRATION_SECONDS,
            user_info["email"],
        )
        return "http://localhost:8000/me?state=" + state

    async def _exchange_code(self, code: str) -> OAuthTokens:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": self.settings.google_client_id,
                    "client_secret": self.settings.google_client_secret,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": self.settings.google_redirect_uri,
                },
                headers={
                    "Content-Type": "application/x-www-form-urlencoded"
                },
            )
        response.raise_for_status()
        response_data = response.json()
        return OAuthTokens(
            access_token=response_data["access_token"],
            refresh_token=response_data.get("refresh_token"),
            expires_in=response_data["expires_in"],
        )

    async def _get_user_info(self, access_token: str):
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://openidconnect.googleapis.com/v1/userinfo",
                headers={
                    "Authorization": f"Bearer {access_token}"
                },
            )

        response.raise_for_status()
        return response.json()

    async def _create_user(self, user_info, tokens: OAuthTokens):
        create_user = CreateUser(self.session)
        await create_user.execute(user_info["email"], tokens)
