from fastapi import status
from httpx import AsyncClient

from app.db import User, YtdlpCookies

URL = "/api/ytdlp-cookies"


async def test_get_ytdlp_cookies_when_not_logged_in(client: AsyncClient):
    """
    Test getting yt-dlp cookies when not logged in. The endpoint should
    return a 401 response.
    """
    response = await client.get(URL)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_get_ytdlp_cookies_not_found(client: AsyncClient, create_and_login_user):
    """
    Test getting yt-dlp cookies when they do not exist. The endpoint should
    return a 404 response.
    """
    await create_and_login_user()
    response = await client.get(URL)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "yt-dlp cookies not found."}


async def test_get_ytdlp_cookies(
    client: AsyncClient,
    create_and_login_user,
    create_ytdlp_cookies,
):
    """
    Test getting yt-dlp cookies when they exist. The endpoint should
    return a 200 response.
    """
    user: User = await create_and_login_user()
    ytdlp_cookies: YtdlpCookies = await create_ytdlp_cookies(email=user.email)

    response = await client.get(URL)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["cookies"] == YtdlpCookies.decrypt_value(ytdlp_cookies.cookies)
