from fastapi import status
from sqlalchemy import select

from app.db import User, YtdlpCookies

URL = "/api/ytdlp-cookies"


async def test_delete_ytdlp_cookies_when_not_logged_in(client):
    """
    Test delete yt-dlp cookies when not logged in. The endpoint should
    return a 401 response.
    """

    response = await client.delete(URL)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_delete_non_existent_ytdlp_cookies(client, create_and_login_user):
    """
    Test delete yt-dlp cookies that don't exist. The endpoint
    should return a 204 response.
    """

    await create_and_login_user()

    response = await client.delete(URL)
    assert response.status_code == status.HTTP_204_NO_CONTENT


async def test_delete_ytdlp_cookies(
    client, create_and_login_user, create_ytdlp_cookies, db_session
):
    """
    Test delete yt-dlp cookies. The endpoint should return a 204 response.
    """

    user: User = await create_and_login_user()
    await create_ytdlp_cookies(email=user.email)

    response = await client.delete(URL)
    assert response.status_code == status.HTTP_204_NO_CONTENT

    query = select(YtdlpCookies).where(YtdlpCookies.email == user.email)
    ytdlp_cookies = await db_session.scalar(query)
    assert ytdlp_cookies is None
