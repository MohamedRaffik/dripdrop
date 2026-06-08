from unittest.mock import AsyncMock

import pytest
from fastapi import status

URL = "/api/music/metadata"


async def test_metadata_when_not_logged_in(client):
    """
    Test retrieving metadata for a video when the user
    is not logged in. The response should return a 401 error.
    """

    response = await client.get(
        URL, params={"video_url": "https://www.youtube.com/watch?v=FCrJNvJ-NIU"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_metadata_with_invalid_video_url(client, faker, create_and_login_user):
    """
    Test retrieving metadata for a video with an invalid url. The endpoint
    should return a 422 error.
    """

    await create_and_login_user()
    response = await client.get(URL, params={"video_url": faker.url([])})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


async def test_metadata_with_failed_to_retrieve(
    client, create_and_login_user, monkeypatch
):
    """
    Test retrieving metadata for a valid youtube video but with a
    failed response. The endpoint should return a 400 response.
    """

    mock_extract_video_info = AsyncMock(side_effect=Exception("yt-dlp failed"))
    monkeypatch.setattr(
        "app.routes.music.ytdlp.extract_video_info", mock_extract_video_info
    )

    await create_and_login_user()
    response = await client.get(
        URL,
        params={"video_url": "https://www.youtube.com/watch?v=FCrJNvJ-NIU"},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "Unable to get metadata."}


async def test_metadata_returns_fields_from_ytdlp(
    client, create_and_login_user, monkeypatch
):
    mock_extract_video_info = AsyncMock(
        return_value={
            "title": "Song Title",
            "artist": "Song Artist",
            "album": "Song Album",
            "uploader": "Channel Name",
        }
    )
    monkeypatch.setattr(
        "app.routes.music.ytdlp.extract_video_info", mock_extract_video_info
    )

    await create_and_login_user()
    response = await client.get(
        URL,
        params={"video_url": "https://vimeo.com/876518552"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "grouping": "Channel Name",
        "title": "Song Title",
        "artist": "Song Artist",
        "album": "Song Album",
    }


@pytest.mark.xfail(reason="yt-dlp fails to run in github actions")
async def test_metadata_with_youtube_video_url(client, create_and_login_user):
    """
    Test retrieving metadata for a valid youtube video. The endpoint
    should return a successful response.
    """

    await create_and_login_user()
    response = await client.get(
        URL,
        params={"video_url": "https://www.youtube.com/watch?v=FCrJNvJ-NIU"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"grouping": "Food Dip"}


@pytest.mark.xfail(reason="yt-dlp fails to run in github actions")
async def test_metadata_with_video_url(client, create_and_login_user):
    """
    Test retrieving metadata for a valid video supported by yt-dlp.
    The endpoint should return a successful response.
    """

    await create_and_login_user()
    response = await client.get(
        URL,
        params={"video_url": "https://vimeo.com/876518552"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"grouping": "McGloughlin Brothers"}
