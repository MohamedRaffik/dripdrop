from unittest.mock import patch

import pytest

from app.services import ytdlp


@pytest.mark.asyncio
async def test_download_audio_from_video_embeds_metadata():
    captured_opts = {}

    class FakeYoutubeDL:
        def __init__(self, ydl_opts):
            captured_opts.update(ydl_opts)

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def download(self, url):
            assert url == "https://example.com/watch?v=test"

    with patch("app.services.ytdlp.yt_dlp.YoutubeDL", FakeYoutubeDL):
        await ytdlp.download_audio_from_video(
            download_path="/tmp/test", url="https://example.com/watch?v=test"
        )

    postprocessors = captured_opts["postprocessors"]
    assert postprocessors[0]["key"] == "FFmpegExtractAudio"
    assert postprocessors[1] == {"key": "FFmpegMetadata", "add_metadata": True}
