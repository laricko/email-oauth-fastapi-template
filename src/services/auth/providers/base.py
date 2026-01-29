from abc import ABC, abstractmethod


class OAuthProvider(ABC):

    STATE_EXPIRATION_SECONDS = 600

    @abstractmethod
    async def get_auth_url(self) -> str:
        raise NotImplementedError

    @abstractmethod
    async def handle_callback(self, code: str, state: str) -> str:
        raise NotImplementedError
