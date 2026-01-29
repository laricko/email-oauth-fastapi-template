from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Email
from services.auth.dtos import UserOut


class EmailService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def sync_emails(self, email: str, current_user: UserOut) -> None:
        assert email in [e.email for e in current_user.emails], "Email does not belong to the user."
