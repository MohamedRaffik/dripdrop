from unittest.mock import MagicMock, patch

import pytest

from app.services import ytdlp


@pytest.mark.parametrize(
    "function_name,expected_opts",
    [
        ("download_audio_from_video", {"noplaylist": True}),
        ("extract_video_info", {"noplaylist": True}),
    ],
)
async def test_ytdlp_uses_noplaylist(function_name, expected_opts):
    captured_opts = {}

    def capture_opts(opts):
        captured_opts.update(opts)
        mock_ydl = MagicMock()
        if function_name == "download_audio_from_video":
            mock_ydl.download.return_value = None
        else:
            mock_ydl.extract_info.return_value = {"uploader": "test"}
        mock_ydl.__enter__.return_value = mock_ydl
        mock_ydl.__exit__.return_value = None
        return mock_ydl

    with patch("app.services.ytdlp.yt_dlp.YoutubeDL", side_effect=capture_opts):
        if function_name == "download_audio_from_video":
            await ytdlp.download_audio_from_video("/tmp/test", "https://example.com")
        else:
            await ytdlp.extract_video_info("https://example.com")

    for key, value in expected_opts.items():
        assert captured_opts.get(key) == value
