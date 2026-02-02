from email.utils import parsedate_to_datetime

import httpx

from db.models import Email
from errors import EmailAuthError

GMAIL_API_BASE = "https://gmail.googleapis.com/gmail/v1"


class GoogleEmailProvider:

    @classmethod
    async def fetch_emails(
        cls,
        user_email_id: int,
        access_token: str,
        count: int,
    ) -> list[Email]:
        headers = {
            "Authorization": f"Bearer {access_token}"
        }

        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{GMAIL_API_BASE}/users/me/messages",
                headers=headers,
                params={"maxResults": count}
            )
            if resp.status_code == 401:
                raise EmailAuthError("Email access token is unauthorized.")
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
                if msg_resp.status_code == 401:
                    raise EmailAuthError("Email access token is unauthorized.")
                msg_resp.raise_for_status()
                email_data = msg_resp.json()
                for data in email_data["payload"]["headers"]:
                    if data["name"] == "From":
                        from_email = data["value"]
                    elif data["name"] == "Subject":
                        subject = data["value"]
                    elif data["name"] == "Date":
                        recieved_at = data["value"]
                dt_recieved_at = parsedate_to_datetime(recieved_at).replace(tzinfo=None)
                emails.append(
                    Email(
                        user_email_id=user_email_id,
                        external_id=msg["id"],
                        from_email=from_email,
                        subject=subject,
                        snippet=email_data["snippet"],
                        recieved_at=dt_recieved_at,
                        is_read="UNREAD" not in email_data["labelIds"],
                    )
                )

            return emails
