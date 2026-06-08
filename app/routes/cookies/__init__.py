from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy import select

from app.db import Cookies
from app.dependencies import AuthUser, DatabaseSession, get_authenticated_user
from app.models.cookies import CookiesResponse, UpdateCookies

router = APIRouter(
    prefix="/cookies",
    tags=["Cookies"],
    dependencies=[Depends(get_authenticated_user)],
)


@router.get(
    "",
    response_model=CookiesResponse,
    responses={status.HTTP_404_NOT_FOUND: {"description": "Cookies not found."}},
)
async def get_cookies(user: AuthUser, db_session: DatabaseSession):
    query = select(Cookies).where(Cookies.email == user.email)
    if cookies := await db_session.scalar(query):
        return CookiesResponse.model_validate(cookies)
    raise HTTPException(
        detail="Cookies not found.", status_code=status.HTTP_404_NOT_FOUND
    )


@router.post("", response_model=CookiesResponse)
async def update_cookies(
    user: AuthUser,
    db_session: DatabaseSession,
    body: Annotated[UpdateCookies, Body()],
):
    query = select(Cookies).where(Cookies.email == user.email)
    if cookies := await db_session.scalar(query):
        cookies.cookies = body.cookies
        await db_session.commit()
    else:
        cookies = Cookies(email=user.email, cookies=body.cookies)
        db_session.add(cookies)
        await db_session.commit()
    return CookiesResponse.model_validate(body)


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cookies(user: AuthUser, session: DatabaseSession):
    query = select(Cookies).where(Cookies.email == user.email)
    if cookies := await session.scalar(query):
        await session.delete(cookies)
        await session.commit()
    return None
