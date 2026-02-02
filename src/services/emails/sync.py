from datetime import datetime, timedelta
from functools import partial

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config import Settings
from db.models import Email, ProviderType, UserEmail
from errors import ClientError, EmailAuthError
from services.auth.dtos import EmailSyncData, UserOut
from services.auth.providers.google import GoogleOAuthProvider
from services.emails.providers.google import GoogleEmailProvider


class EmailService:
    def __init__(self, session: AsyncSession, settings: Settings):
        self.session = session
        self.settings = settings

    async def sync_emails(self, data: EmailSyncData, current_user: UserOut):
        self._check_email_in_users_email(data, current_user)
        user_email = await self._get_user_email(data)
        self._check_user_email(current_user, user_email)
        emails = await self._fetch_emails(data, user_email)
        await self._save_emails(emails)
        return emails

    async def get_emails(self, user_email_str: str) -> list[Email]:
        stmt = select(UserEmail).where(UserEmail.email == user_email_str.lower())
        result = await self.session.execute(stmt)
        user_email = result.scalar_one_or_none()
        if not user_email:
            raise ClientError("UserEmail not found.")

        stmt = select(Email).where(Email.user_email_id == user_email.id) \
            .order_by(Email.created_at.desc())
        result = await self.session.execute(stmt)
        emails = result.scalars().all()
        return emails

    async def _save_emails(self, emails: list[Email]):
        stmt = select(Email).where(
            Email.external_id.in_([email.external_id for email in emails]),
            Email.user_email_id == emails[0].user_email_id
        )
        result = await self.session.execute(stmt)
        existing_emails = result.scalars().all()
        existing_external_ids = {email.external_id for email in existing_emails}
        emails_to_insert = [email for email in emails if email.external_id not in existing_external_ids]
        self.session.add_all(emails_to_insert)
        await self.session.commit()

    async def _fetch_emails(self, data, user_email):
        fetcher, provider = self._get_provider_strategy(data, user_email)
        try:
            return await fetcher(user_email.access_token)
        except EmailAuthError as exc:
            if not user_email.refresh_token:
                raise ClientError("Failed to fetch emails.") from exc

            try:
                tokens = await provider.refresh_token(user_email.refresh_token)
            except Exception as refresh_exc:
                raise ClientError("Failed to refresh token.") from refresh_exc

            now = datetime.now()
            user_email.access_token = tokens.access_token
            user_email.expires_at = now + timedelta(seconds=tokens.expires_in)
            user_email.obtained_at = now
            if tokens.refresh_token:
                user_email.refresh_token = tokens.refresh_token
            await self.session.commit()

            try:
                return await fetcher(tokens.access_token)
            except EmailAuthError as final_exc:
                raise ClientError("Failed to fetch emails.") from final_exc
            except Exception as final_exc:
                raise ClientError("Failed to fetch emails.") from final_exc
        except Exception as exc:
            raise ClientError("Failed to fetch emails.") from exc

    def _get_provider_strategy(self, data, user_email):
        if user_email.provider == ProviderType.google:
            fetcher = partial(
                GoogleEmailProvider.fetch_emails,
                user_email.id,
                count=data.count,
            )
            provider = GoogleOAuthProvider(self.settings)
            return fetcher, provider
        raise ClientError("Unsupported email provider.")

    def _check_user_email(self, current_user, user_email):
        if not user_email:
            raise ClientError("UserEmail not found.")
        if user_email.user_id != current_user.id:
            raise ClientError("UserEmail does not belong to the current user.")

    async def _get_user_email(self, data):
        stmt = select(UserEmail).where(UserEmail.email == data.email.lower())
        result = await self.session.execute(stmt)
        user_email = result.scalar_one_or_none()
        return user_email

    def _check_email_in_users_email(self, data, current_user):
        if data.email not in [e.email for e in current_user.emails]:
            raise ClientError("Email does not belong to the user.")
