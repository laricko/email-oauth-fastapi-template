from datetime import datetime, timedelta, timezone

import jwt
import redis.asyncio as redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import UserEmail

ACCESS_TOKEN_EXPIRES_IN_MINUTES = 15
JWT_ALGORITHM = "HS256"


class JWTTokens:

    def __init__(self, secret_key: str, redis: redis.Redis, session: AsyncSession):
        self.session = session
        self.secret_key = secret_key
        self.redis = redis

    async def generate_access_jwt_token(self, sub: str) -> str:
        email = await self.redis.get(sub)
        if not email:
            raise ValueError("Email not found in Redis")

        stmt = select(UserEmail).where(UserEmail.email == email.decode().lower())
        result = await self.session.execute(stmt)
        user_obj = result.scalar_one_or_none()
        if not user_obj:
            raise ValueError("User not found in database")

        expiration = datetime.now() + timedelta(
            minutes=ACCESS_TOKEN_EXPIRES_IN_MINUTES
        )
        payload = {"sub": user_obj.email, "exp": expiration}
        token = jwt.encode(payload, self.secret_key, algorithm=JWT_ALGORITHM)
        return {"access_token": token}
