from datetime import datetime, timedelta

import jwt
import redis.asyncio as redis
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import UserEmail
from errors import ClientError
from services.auth.dtos import GenerateTokenData, UserOut

ACCESS_TOKEN_EXPIRES_IN_MINUTES = 15
JWT_ALGORITHM = "HS256"


class AuthService:

    def __init__(self, secret_key: str, redis: redis.Redis, session: AsyncSession):
        self.session = session
        self.secret_key = secret_key
        self.redis = redis

    async def issue_access_token(self, data: GenerateTokenData) -> dict:
        email = await self.redis.get(data.state)
        if not email:
            raise ClientError("Invalid or expired state token")

        user = await self._get_user_email(email.decode())
        expiration = datetime.now() + timedelta(
            minutes=ACCESS_TOKEN_EXPIRES_IN_MINUTES
        )
        payload = {"sub": user.email, "exp": expiration}
        token = jwt.encode(payload, self.secret_key, algorithm=JWT_ALGORITHM)
        return {"access_token": token}

    async def get_current_user(self, token: str) -> UserOut:
        payload = await self._decode_access_token(token)
        email = payload["sub"]
        return await self._get_user(email)

    async def _decode_access_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(
                token, self.secret_key, algorithms=[JWT_ALGORITHM]
            )
            return payload
        except jwt.PyJWTError as e:
            raise ClientError("Token decoding failed") from e

    async def _get_user_email(self, email: str) -> UserEmail:
        stmt = select(UserEmail).where(UserEmail.email == email.lower())
        result = await self.session.execute(stmt)
        user_obj = result.scalar_one_or_none()
        if not user_obj:
            raise ClientError("User not found in database")
        return user_obj

    async def _get_user(self, email: str) -> UserOut:
        sql = """
        SELECT ue.user_id AS id, array_agg(
            jsonb_build_object(
                'email', ue.email,
                'provider', ue.provider,
                'last_synced_at', ue.last_synced_at
            )
        ) AS emails
        FROM user_emails ue
        WHERE user_id = (
            SELECT user_id
            FROM user_emails
            WHERE email = :email
        )
        GROUP BY ue.user_id
        """
        result = await self.session.execute(text(sql), {"email": email})
        return UserOut(**result.mappings().first())
