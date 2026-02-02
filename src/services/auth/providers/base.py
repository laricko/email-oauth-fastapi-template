from abc import ABC, abstractmethod

from services.auth.dtos import OAuthTokens


class OAuthProvider(ABC):

    STATE_EXPIRATION_SECONDS = 600

    @abstractmethod
    async def get_auth_url(self) -> str:
        raise NotImplementedError

    @abstractmethod
    async def handle_callback(self, code: str) -> tuple[dict, OAuthTokens]:
        raise NotImplementedError
