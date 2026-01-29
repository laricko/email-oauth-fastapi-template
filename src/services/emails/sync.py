import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import UserEmail
from services.auth.dtos import UserOut

GMAIL_API_BASE = "https://gmail.googleapis.com/gmail/v1"


class EmailService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def sync_emails(self, email: str, current_user: UserOut):
        if email not in [e.email for e in current_user.emails]:
            raise ValueError("Email does not belong to the user.")

        stmt = select(UserEmail).where(UserEmail.email == email.lower())
        result = await self.session.execute(stmt)
        user_email = result.scalar_one_or_none()

        if not user_email:
            raise ValueError("UserEmail not found.")
        if user_email.id != current_user.id:
            raise ValueError("UserEmail does not belong to the current user.")

        access_token = user_email.access_token

        headers = {
            "Authorization": f"Bearer {access_token}"
        }

        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{GMAIL_API_BASE}/users/me/messages",
                headers=headers,
                params={"maxResults": 10}
            )
            resp.raise_for_status()

            messages = resp.json().get("messages", [])
            if not messages:
                return []

            emails = []
            for msg in messages:
                msg_resp = await client.get(
                    f"{GMAIL_API_BASE}/users/me/messages/{msg['id']}",
                    headers=headers,
                    params={"format": "metadata"}
                )
                msg_resp.raise_for_status()
                emails.append(msg_resp.json())

            return emails
