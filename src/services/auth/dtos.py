from datetime import datetime

from pydantic import BaseModel


class UserEmailOut(BaseModel):
    email: str
    provider: str
    last_synced_at: datetime | None


class UserOut(BaseModel):
    id: int
    emails: list[UserEmailOut]


class EmailSyncData(BaseModel):
    email: str
    count: int = 10


class OAuthTokens(BaseModel):
    access_token: str
    refresh_token: str | None
    expires_in: int
