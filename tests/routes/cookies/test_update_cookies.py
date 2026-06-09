from faker import Faker
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import Cookies, User

URL = "/api/cookies"


async def test_update_cookies_when_not_logged_in(client: AsyncClient, faker: Faker):
    """
    Test updating cookies when not logged in. The
    endpoint should return a 401 status.
    """
    response = await client.post(URL, json={"content": faker.text()})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_update_cookies_creating(
    client: AsyncClient,
    db_session: AsyncSession,
    create_and_login_user,
    faker: Faker,
):
    """
    Test updating cookies when no configuration exists. The
    endpoint should create a new configuration and return a 200 status.
    """
    user: User = await create_and_login_user()
    new_data = {"content": faker.text()}

    response = await client.post(URL, json=new_data)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == new_data

    query = select(Cookies).where(Cookies.email == user.email)
    stored_cookies = await db_session.scalar(query)
    assert stored_cookies is not None
    assert stored_cookies.content == new_data["content"]


async def test_update_cookies_with_existing(
    client: AsyncClient,
    db_session: AsyncSession,
    create_and_login_user,
    create_cookies,
    faker: Faker,
):
    """
    Test updating cookies when a configuration already exists. The
    endpoint should update the existing configuration and return a 200 status.
    """
    user: User = await create_and_login_user()

    stored_cookies = await create_cookies(email=user.email)

    updated_data = {"content": faker.text()}
    response = await client.post(URL, json=updated_data)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == updated_data

    await db_session.refresh(stored_cookies)
    assert stored_cookies.content == updated_data["content"]
