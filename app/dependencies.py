from typing import Annotated

from fastapi import Cookie, Depends, Header, HTTPException, WebSocket, status
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import User, session_maker
from app.services import cookie_session, jwt
from app.settings import settings


async def provide_session():
    async with session_maker() as session:
        yield session


DatabaseSession = Annotated[AsyncSession, Depends(provide_session)]


async def provide_redis():
    redis = Redis.from_url(settings.redis_url)
    try:
        yield redis
    except Exception as e:
        await redis.aclose()
        raise e


RedisClient = Annotated[Redis, Depends(provide_redis)]


async def get_user_from_jwt(token: str | None, db_session: AsyncSession):
    if token:
        if (payload := await jwt.decode(token)) and (email := payload.sub):
            query = select(User).where(User.email == email)
            user = await db_session.scalar(query)
            return user
    return None


async def get_user_from_header(
    db_session: DatabaseSession, authorization: Annotated[str | None, Header()] = None
):
    if authorization:
        token_parts = authorization.trim().split(" ")
        if len(token_parts) == 2:
            token_type, token = token_parts
            if token_type.strip() == "Bearer":
                return await get_user_from_jwt(token=token, db_session=db_session)
    return None


HeaderUser = Annotated[User | None, Depends(get_user_from_header)]


async def get_user_from_cookie(
    db_session: DatabaseSession, token: Annotated[str | None, Cookie()] = None
):
    if token:
        jwt_token = await cookie_session.get(token=token)
        return await get_user_from_jwt(token=jwt_token, db_session=db_session)
    return None


CookieUser = Annotated[User | None, Depends(get_user_from_cookie)]


async def get_authenticated_user(
    header_user: HeaderUser,
    cookie_user: CookieUser,
    websocket: WebSocket = None,
):
    if user := header_user or cookie_user:
        return user
    if websocket:
        await websocket.close()
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


AuthUser = Annotated[User, Depends(get_authenticated_user)]


async def get_admin_user(
    user: AuthUser,
    websocket: WebSocket = None,
):
    if user.admin:
        return user
    if websocket:
        websocket.close()
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)


AdminUser = Annotated[User, Depends(get_admin_user)]
