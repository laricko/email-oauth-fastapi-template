from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Email, ProviderType, UserEmail
from errors import ClientError
from services.auth.dtos import EmailSyncData, UserOut
from services.emails.providers.google import GoogleEmailProvider

GMAIL_API_BASE = "https://gmail.googleapis.com/gmail/v1"


class EmailService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def sync_emails(self, data: EmailSyncData, current_user: UserOut):
        self._check_email_in_users_email(data, current_user)
        user_email = await self._get_user_email(data)
        self._check_user_email(current_user, user_email)
        emails = await self._fetch_emails(data, user_email)
        await self._save_emails(emails)
        return emails

    async def _save_emails(self, emails: list[Email]):
        stmt = select(Email).where(
            Email.external_id.in_([email.external_id for email in emails]),
            Email.user_email_id == emails[0].user_email_id
        )
        print(stmt.compile(compile_kwargs={"literal_binds": True}))
        result = await self.session.execute(stmt)
        existing_emails = result.scalars().all()
        existing_external_ids = {email.external_id for email in existing_emails}
        emails_to_insert = [email for email in emails if email.external_id not in existing_external_ids]
        self.session.add_all(emails_to_insert)
        await self.session.commit()

    async def _fetch_emails(self, data, user_email):
        if user_email.provider == ProviderType.google:
            def fetch(token): return GoogleEmailProvider.fetch_emails(
                user_email.id,
                token,
                data.count
            )

        emails = await fetch(user_email.access_token)
        return emails

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
