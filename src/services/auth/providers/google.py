import secrets
from urllib.parse import urlencode

import httpx
from config import Settings
from services.auth.dtos import OAuthTokens
from services.auth.providers.base import OAuthProvider


class GoogleOAuthProvider(OAuthProvider):
    def __init__(self, settings: Settings):
        self.settings = settings

    async def get_auth_url(self) -> str:
        state = secrets.token_urlsafe(16)
        params = {
            "client_id": self.settings.google_client_id,
            "redirect_uri": self.settings.google_redirect_uri,
            "response_type": "code",
            "scope": " ".join(self.settings.google_scopes),
            "access_type": "offline",
            "prompt": "consent",
            "state": state,
        }

        return f"{self.settings.google_auth_url}?{urlencode(params)}"

    async def handle_callback(self, code: str) -> tuple[dict, OAuthTokens]:
        tokens = await self._exchange_code(code)
        user_info = await self._get_user_info(tokens.access_token)
        return user_info, tokens

    async def refresh_token(self, refresh_token: str) -> OAuthTokens:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.settings.google_token_url,
                data={
                    "client_id": self.settings.google_client_id,
                    "client_secret": self.settings.google_client_secret,
                    "refresh_token": refresh_token,
                    "grant_type": "refresh_token",
                },
                headers={
                    "Content-Type": "application/x-www-form-urlencoded"
                },
            )
        response.raise_for_status()
        response_data = response.json()
        return OAuthTokens(
            access_token=response_data["access_token"],
            refresh_token=refresh_token,
            expires_in=response_data["expires_in"],
        )

    async def _exchange_code(self, code: str) -> OAuthTokens:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.settings.google_token_url,
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
