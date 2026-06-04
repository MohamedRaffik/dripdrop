from faker import Faker
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import User, YtdlpCookies

URL = "/api/ytdlp-cookies"


async def test_update_ytdlp_cookies_when_not_logged_in(
    client: AsyncClient, faker: Faker
):
    """
    Test updating yt-dlp cookies when not logged in. The
    endpoint should return a 401 status.
    """
    response = await client.post(URL, json={"cookies": faker.text()})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_update_ytdlp_cookies_creating(
    client: AsyncClient,
    db_session: AsyncSession,
    create_and_login_user,
    faker: Faker,
):
    """
    Test updating yt-dlp cookies when no configuration exists. The
    endpoint should create a new configuration and return a 200 status.
    """
    user: User = await create_and_login_user()
    new_data = {"cookies": faker.text()}

    response = await client.post(URL, json=new_data)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == new_data

    query = select(YtdlpCookies).where(YtdlpCookies.email == user.email)
    ytdlp_cookies = await db_session.scalar(query)
    assert ytdlp_cookies is not None
    assert ytdlp_cookies.cookies == new_data["cookies"]


async def test_update_ytdlp_cookies_with_existing(
    client: AsyncClient,
    db_session: AsyncSession,
    create_and_login_user,
    create_ytdlp_cookies,
    faker: Faker,
):
    """
    Test updating yt-dlp cookies when a configuration already exists. The
    endpoint should update the existing configuration and return a 200 status.
    """
    user: User = await create_and_login_user()

    ytdlp_cookies = await create_ytdlp_cookies(email=user.email)

    updated_data = {"cookies": faker.text()}
    response = await client.post(URL, json=updated_data)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == updated_data

    await db_session.refresh(ytdlp_cookies)
    assert ytdlp_cookies.cookies == updated_data["cookies"]
