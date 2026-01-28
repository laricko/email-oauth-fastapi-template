from functools import cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    google_client_id: str
    google_client_secret: str
    google_redirect_uri: str
    google_auth_url: str = "https://accounts.google.com/o/oauth2/v2/auth"
    google_token_url: str = "https://oauth2.googleapis.com/token"
    google_userinfo_url: str = "https://openidconnect.googleapis.com/v1/userinfo"

    google_scopes: list[str] = [
        "openid",
        "email",
        "profile",
        "https://www.googleapis.com/auth/gmail.readonly",
    ]

    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "mailzen"
    postgres_password: str = "mailzen"
    postgres_db: str = "mailzen"

    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0

    @property
    def pg_dsn(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:"
            f"{self.postgres_password}@{self.postgres_host}:"
            f"{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def redis_dsn(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"


@cache
def get_settings():
    return Settings()
