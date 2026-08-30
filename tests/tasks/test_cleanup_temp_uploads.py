from datetime import timedelta
from unittest.mock import AsyncMock

from app.tasks.music import cleanup_temp_music_uploads
from app.utils.music_uploads import (
    TEMP_UPLOAD_MAX_AGE_HOURS,
    cleanup_temp_uploads,
    music_temp_folder,
)


async def test_cleanup_temp_uploads(monkeypatch):
    mock_delete = AsyncMock(return_value=["music/temp/old/file.mp3"])
    monkeypatch.setattr(
        "app.utils.music_uploads.s3.delete_objects_older_than",
        mock_delete,
    )

    deleted = await cleanup_temp_uploads()

    assert deleted == ["music/temp/old/file.mp3"]
    mock_delete.assert_awaited_once_with(
        prefix=f"{music_temp_folder()}/",
        max_age=timedelta(hours=TEMP_UPLOAD_MAX_AGE_HOURS),
    )


async def test_cleanup_temp_music_uploads_task(monkeypatch):
    mock_cleanup = AsyncMock(return_value=["music/temp/old/file.mp3"])
    monkeypatch.setattr("app.tasks.music.cleanup_temp_uploads", mock_cleanup)

    deleted_count = await cleanup_temp_music_uploads()

    assert deleted_count == 1
    mock_cleanup.assert_awaited_once_with()
