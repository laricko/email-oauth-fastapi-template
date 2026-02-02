from typing import Annotated

from fastapi import Depends
from fastapi.routing import APIRouter

from depends import get_current_user, get_email_service
from services.auth.dtos import EmailSyncData, UserOut
from services.emails.sync import EmailService

router = APIRouter(prefix="/emails", tags=["emails"])


@router.post("/sync")
async def sync_emails(
    data: EmailSyncData,
    current_user: Annotated[UserOut, Depends(get_current_user)],
    email_service: Annotated[EmailService, Depends(get_email_service)],
):
    return await email_service.sync_emails(data=data, current_user=current_user)


@router.get("/")
async def get_emails(
    current_user: Annotated[UserOut, Depends(get_current_user)],
):
    return current_user.emails
