from unittest.mock import MagicMock

import pytest
from fastapi import status
from sqlalchemy import select

from app.db import MusicJob
from app.services import s3
from app.utils.music_uploads import build_job_audio_key, music_temp_folder

from .conftest import PRESIGN_URL, presign_and_upload

URL = "/api/music/jobs/create"


async def test_create_job_when_not_logged_in(client):
    """
    Test creating a music job when not logged in. The endpoint should return a
    401 status.
    """

    response = await client.post(URL)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_create_job_with_upload_key_and_video_url(
    client, create_and_login_user, test_video_url, test_audio
):
    """
    Test creating a music job when logged in with an upload_key and video_url.
    The endpoint should return a 422 status.
    """

    await create_and_login_user()
    presign_data = await presign_and_upload(client, test_audio)
    response = await client.post(
        URL,
        data={
            "title": "title",
            "artist": "artist",
            "album": "album",
            "grouping": "grouping",
            "video_url": test_video_url,
            "upload_key": presign_data["key"],
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert response.json() == {
        "detail": "'upload_key' and 'video_url' cannot both be defined."
    }


async def test_create_job_without_upload_key_and_video_url(client, create_and_login_user):
    """
    Test creating a music job when logged in without an upload_key or video_url.
    The endpoint should return a 422 status.
    """

    await create_and_login_user()
    response = await client.post(
        URL,
        data={
            "title": "title",
            "artist": "artist",
            "album": "album",
            "grouping": "grouping",
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert response.json() == {"detail": "'upload_key' or 'video_url' must be defined."}


async def test_create_job_with_missing_uploaded_file(client, create_and_login_user):
    await create_and_login_user()
    presign_response = await client.post(
        PRESIGN_URL,
        json={"filename": "dripdrop.mp3", "content_type": "audio/mpeg"},
    )
    presign_data = presign_response.json()
    response = await client.post(
        URL,
        data={
            "title": "title",
            "artist": "artist",
            "album": "album",
            "grouping": "grouping",
            "upload_key": presign_data["key"],
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert response.json() == {"detail": "Uploaded file not found."}


async def test_create_job_with_invalid_upload_key(client, create_and_login_user):
    await create_and_login_user()
    response = await client.post(
        URL,
        data={
            "title": "title",
            "artist": "artist",
            "album": "album",
            "grouping": "grouping",
            "upload_key": "music/not-temp/test.mp3",
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert response.json() == {"detail": "Invalid upload_key."}


@pytest.mark.long
async def test_create_job_with_upload_key(
    client, create_and_login_user, test_audio, db_session
):
    """
    Test creating a job with a presigned upload. The endpoint should return a
    201 status.
    """

    await create_and_login_user()
    presign_data = await presign_and_upload(client, test_audio)
    temp_key = presign_data["key"]
    response = await client.post(
        URL,
        data={
            "title": "title",
            "artist": "artist",
            "album": "album",
            "grouping": "grouping",
            "upload_key": temp_key,
        },
    )
    assert response.status_code == status.HTTP_201_CREATED

    query = select(MusicJob)
    music_jobs = (await db_session.scalars(query)).all()
    assert len(music_jobs) == 1
    music_job = music_jobs[0]
    assert music_job.title == "title"
    assert music_job.artist == "artist"
    assert music_job.album == "album"
    assert music_job.grouping == "grouping"
    expected_key = build_job_audio_key(job_id=music_job.id, filename="dripdrop.mp3")
    assert music_job.original_filename == expected_key
    assert music_job.filename_url == s3.resolve_url(filename=expected_key)
    assert temp_key.startswith(f"{music_temp_folder()}/")
    assert not await s3.object_exists(filename=temp_key)


async def test_create_job_with_video_url_without_metadata(
    client, create_and_login_user, test_video_url
):
    """
    Test creating a job with a video url and no metadata fields. The endpoint
    should return a 422 status.
    """

    await create_and_login_user()
    response = await client.post(
        URL,
        data={
            "video_url": test_video_url,
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


@pytest.mark.parametrize(
    "upload_to_webdav,expected",
    [
        (None, False),
        ("true", True),
        ("false", False),
    ],
)
async def test_create_job_upload_to_webdav(
    client,
    create_and_login_user,
    create_webdav,
    test_video_url,
    monkeypatch,
    upload_to_webdav,
    expected,
):
    user = await create_and_login_user()
    await create_webdav(email=user.email)
    mock_task = MagicMock()
    monkeypatch.setattr("app.routes.music.jobs.run_music_job.delay", mock_task)

    data = {
        "title": "title",
        "artist": "artist",
        "album": "album",
        "grouping": "grouping",
        "video_url": test_video_url,
    }
    if upload_to_webdav is not None:
        data["upload_to_webdav"] = upload_to_webdav

    response = await client.post(URL, data=data)
    assert response.status_code == status.HTTP_201_CREATED

    mock_task.assert_called_once()
    assert mock_task.call_args.kwargs["upload_to_webdav"] is expected


async def test_create_job_with_video_url(
    client, create_and_login_user, db_session, test_video_url
):
    """
    Test creating a job with a video url. The endpoint should return a 201 status.
    """

    await create_and_login_user()
    response = await client.post(
        URL,
        data={
            "title": "title",
            "artist": "artist",
            "album": "album",
            "grouping": "grouping",
            "video_url": test_video_url,
        },
    )
    assert response.status_code == status.HTTP_201_CREATED

    query = select(MusicJob)
    music_jobs = (await db_session.scalars(query)).all()
    assert len(music_jobs) == 1
    music_job = music_jobs[0]
    assert music_job.title == "title"
    assert music_job.artist == "artist"
    assert music_job.album == "album"
    assert music_job.grouping == "grouping"
