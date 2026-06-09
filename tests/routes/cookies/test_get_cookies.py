from fastapi import status
from httpx import AsyncClient

from app.db import Cookies, User

URL = "/api/cookies"


async def test_get_cookies_when_not_logged_in(client: AsyncClient):
    """
    Test getting cookies when not logged in. The endpoint should
    return a 401 response.
    """
    response = await client.get(URL)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_get_cookies_not_found(client: AsyncClient, create_and_login_user):
    """
    Test getting cookies when they do not exist. The endpoint should
    return a 404 response.
    """
    await create_and_login_user()
    response = await client.get(URL)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Cookies not found."}


async def test_get_cookies(
    client: AsyncClient,
    create_and_login_user,
    create_cookies,
):
    """
    Test getting cookies when they exist. The endpoint should
    return a 200 response.
    """
    user: User = await create_and_login_user()
    stored_cookies: Cookies = await create_cookies(email=user.email)

    response = await client.get(URL)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["content"] == Cookies.decrypt_value(stored_cookies.content)
