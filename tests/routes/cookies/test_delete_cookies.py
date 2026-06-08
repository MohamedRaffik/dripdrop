from fastapi import status
from sqlalchemy import select

from app.db import Cookies, User

URL = "/api/cookies"


async def test_delete_cookies_when_not_logged_in(client):
    """
    Test delete cookies when not logged in. The endpoint should
    return a 401 response.
    """

    response = await client.delete(URL)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_delete_non_existent_cookies(client, create_and_login_user):
    """
    Test delete cookies that don't exist. The endpoint
    should return a 204 response.
    """

    await create_and_login_user()

    response = await client.delete(URL)
    assert response.status_code == status.HTTP_204_NO_CONTENT


async def test_delete_cookies(client, create_and_login_user, create_cookies, db_session):
    """
    Test delete cookies. The endpoint should return a 204 response.
    """

    user: User = await create_and_login_user()
    await create_cookies(email=user.email)

    response = await client.delete(URL)
    assert response.status_code == status.HTTP_204_NO_CONTENT

    query = select(Cookies).where(Cookies.email == user.email)
    stored_cookies = await db_session.scalar(query)
    assert stored_cookies is None
