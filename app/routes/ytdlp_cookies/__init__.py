from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy import select

from app.db import YtdlpCookies
from app.dependencies import AuthUser, DatabaseSession, get_authenticated_user
from app.models.ytdlp_cookies import UpdateYtdlpCookies, YtdlpCookiesResponse

router = APIRouter(
    prefix="/ytdlp-cookies",
    tags=["yt-dlp Cookies"],
    dependencies=[Depends(get_authenticated_user)],
)


@router.get(
    "",
    response_model=YtdlpCookiesResponse,
    responses={status.HTTP_404_NOT_FOUND: {"description": "yt-dlp cookies not found."}},
)
async def get_ytdlp_cookies(user: AuthUser, db_session: DatabaseSession):
    query = select(YtdlpCookies).where(YtdlpCookies.email == user.email)
    if ytdlp_cookies := await db_session.scalar(query):
        return YtdlpCookiesResponse.model_validate(ytdlp_cookies)
    raise HTTPException(
        detail="yt-dlp cookies not found.", status_code=status.HTTP_404_NOT_FOUND
    )


@router.post("", response_model=YtdlpCookiesResponse)
async def update_ytdlp_cookies(
    user: AuthUser,
    db_session: DatabaseSession,
    body: Annotated[UpdateYtdlpCookies, Body()],
):
    query = select(YtdlpCookies).where(YtdlpCookies.email == user.email)
    if ytdlp_cookies := await db_session.scalar(query):
        ytdlp_cookies.cookies = body.cookies
        await db_session.commit()
    else:
        ytdlp_cookies = YtdlpCookies(email=user.email, cookies=body.cookies)
        db_session.add(ytdlp_cookies)
        await db_session.commit()
    return YtdlpCookiesResponse.model_validate(body)


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ytdlp_cookies(user: AuthUser, session: DatabaseSession):
    query = select(YtdlpCookies).where(YtdlpCookies.email == user.email)
    if ytdlp_cookies := await session.scalar(query):
        await session.delete(ytdlp_cookies)
        await session.commit()
    return None
