from fastapi import status

from app.services import s3

PRESIGN_URL = "/api/music/uploads/presign"


async def presign_and_upload(client, test_audio):
    presign_response = await client.post(
        PRESIGN_URL,
        json={"filename": "dripdrop.mp3", "content_type": "audio/mpeg"},
    )
    assert presign_response.status_code == status.HTTP_200_OK
    presign_data = presign_response.json()
    await s3.upload_file(
        filename=presign_data["key"],
        body=test_audio,
        content_type="audio/mpeg",
    )
    return presign_data
