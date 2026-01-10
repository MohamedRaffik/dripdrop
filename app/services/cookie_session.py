from contextlib import asynccontextmanager
from datetime import datetime
from uuid import uuid4

from redis.asyncio import Redis

from app.services import jwt
from app.settings import settings


@asynccontextmanager
async def _get_redis():
    redis = Redis.from_url(settings.redis_url)
    try:
        yield redis
    finally:
        await redis.aclose()


async def create(jwt_token: str):
    if payload := await jwt.decode(jwt_token):
        expires = payload.exp
        token_exp = expires - datetime.now().timestamp()
        token_id = str(uuid4())
        async with _get_redis() as redis:
            await redis.set(token_id, jwt_token, ex=int(token_exp))
            return token_id
    return None


async def get(token: str) -> str | None:
    async with _get_redis() as redis:
        return await redis.get(token)
