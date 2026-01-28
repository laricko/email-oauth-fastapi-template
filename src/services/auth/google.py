import secrets
from urllib.parse import urlencode

import httpx
from sqlalchemy.orm import Session

from config import Settings
from services.auth.dtos import OAuthTokens


class GoogleAuthService:
    def __init__(self, settings: Settings, db: Session):
        self.settings = settings

    async def generate_auth_google(self) -> str:
        params = {
            "client_id": self.settings.google_client_id,
            "redirect_uri": self.settings.google_redirect_uri,
            "response_type": "code",
            "scope": " ".join(self.settings.google_scopes),
            "access_type": "offline",
            "prompt": "select_account",
        }

        return f"{self.settings.google_auth_url}?{urlencode(params)}"

    async def handle_callback(self, code: str):
        tokens = await self._exchange_code(code)
        return tokens

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
                }
            )
        response.raise_for_status()
        response_data = response.json()
        return OAuthTokens(
            access_token=response_data["access_token"],
            refresh_token=response_data.get("refresh_token"),
            expires_in=response_data["expires_in"],
        )

    # async def get_user_info(access_token: str):
    #     access_token = "***REMOVED***"
    #     async with httpx.AsyncClient() as client:
    #         response = await client.get(
    #             "https://openidconnect.googleapis.com/v1/userinfo",
    #             headers={
    #                 "Authorization": f"Bearer {access_token}"
    #             }
    #         )

    #     response.raise_for_status()
    #     return response.json()
