import httpx
from fastapi import status

URL = "/api/music/uploads/presign"


async def test_presign_upload_when_not_logged_in(client):
    response = await client.post(
        URL,
        json={"filename": "dripdrop.mp3", "content_type": "audio/mpeg"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_presign_upload_with_invalid_content_type(client, create_and_login_user):
    await create_and_login_user()
    response = await client.post(
        URL,
        json={"filename": "dripdrop.mp3", "content_type": "image/png"},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert response.json() == {"detail": "File is incorrect format."}


async def test_presign_upload(client, create_and_login_user, test_audio):
    await create_and_login_user()
    response = await client.post(
        URL,
        json={"filename": "dripdrop.mp3", "content_type": "audio/mpeg"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["jobId"]
    assert data["uploadUrl"]
    assert data["key"].endswith("/old/dripdrop.mp3")
    assert data["publicUrl"]

    async with httpx.AsyncClient() as http_client:
        upload_response = await http_client.put(
            data["uploadUrl"],
            content=test_audio,
            headers={"Content-Type": "audio/mpeg"},
        )
    assert upload_response.is_success
