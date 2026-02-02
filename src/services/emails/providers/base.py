from typing import Protocol


class EmailProviderProtocol(Protocol):
    @classmethod
    async def fetch_emails(cls, user_email_id: int, access_token: str, count: int) -> list[Email]:
        ...
