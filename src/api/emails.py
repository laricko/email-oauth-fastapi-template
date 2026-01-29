from typing import Annotated

from fastapi import Depends
from fastapi.routing import APIRouter
from pydantic import BaseModel

from db.models import UserEmail
from depends import get_current_user, get_email_service
from services.emails.sync import EmailService

router = APIRouter(prefix="/emails", tags=["emails"])


class EmailSyncData(BaseModel):
    email: str


@router.post("/sync")
async def sync_emails(
    data: EmailSyncData,
    current_user: Annotated[UserEmail, Depends(get_current_user)],
    email_service: Annotated[EmailService, Depends(get_email_service)],
):
    return await email_service.sync_emails(email=data.email, current_user=current_user)
     
