from fastapi import status

from app.db import User

URL = "/api/auth/session"


async def test_session_when_not_logged_in(client):
    """
    Test getting user details from session when not logged in. The endpoint should
    return a 401 error.
    """

    response = await client.get(URL)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_session_when_logged_in(client, create_and_login_user):
    """
    Test getting user details from session when logged in. The endpoint should return a 200
    response with a json object containing the user email and not an admin.
    """

    user: User = await create_and_login_user()
    response = await client.get(URL)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "email": user.email,
        "admin": user.admin,
        "webdavConfigured": False,
    }


async def test_session_when_logged_in_with_webdav(
    client, create_and_login_user, create_webdav
):
    user = await create_and_login_user()
    await create_webdav(email=user.email)

    response = await client.get(URL)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "email": user.email,
        "admin": user.admin,
        "webdavConfigured": True,
    }


async def test_session_when_logged_in_as_admin(client, create_and_login_user):
    """
    Test getting user details from session when logged in. The endpoint should return a 200
    response with a json object containing the user email and an admin.
    """

    user: User = await create_and_login_user(admin=True)
    response = await client.get(URL)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "email": user.email,
        "admin": user.admin,
        "webdavConfigured": False,
    }
