from datetime import datetime

from pydantic import BaseModel


class UserEmailOut(BaseModel):
    email: str
    provider: str
    last_synced_at: datetime | None


class UserOut(BaseModel):
    id: int
    emails: list[UserEmailOut]


class OAuthTokens(BaseModel):
    access_token: str
    refresh_token: str | None
    expires_in: int
