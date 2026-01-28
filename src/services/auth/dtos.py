from pydantic import BaseModel


class OAuthTokens(BaseModel):
    access_token: str
    refresh_token: str | None
    expires_in: int
