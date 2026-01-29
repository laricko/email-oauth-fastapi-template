from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import ProviderType, User, UserEmail
from services.auth.dtos import OAuthTokens


class CreateUser:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def execute(self, email: str, tokens: OAuthTokens) -> None:
        stmt = select(UserEmail).where(UserEmail.email == email.lower())
        result = await self.session.execute(stmt)
        user_obj = result.scalars().first()
        if user_obj:
            now = datetime.now()
            user_obj.access_token = tokens.access_token
            user_obj.refresh_token = tokens.refresh_token
            user_obj.expires_at = now + timedelta(seconds=tokens.expires_in)
            user_obj.obtained_at = now
            await self.session.commit()
            return

        user = User()
        self.session.add(user)
        await self.session.flush()

        _, provider = email.lower().split("@")

        if "gmail" in provider:
            provider_type = ProviderType.google

        now = datetime.now()
        user_email = UserEmail(
            user_id=user.id,
            email=email,
            provider=provider_type.value,
            access_token=tokens.access_token,
            refresh_token=tokens.refresh_token,
            expires_at=now + timedelta(seconds=tokens.expires_in),
            obtained_at=now,
        )
        self.session.add(user_email)
        await self.session.commit()
