import asyncio
import os
import tempfile

import yt_dlp


def _build_ydl_opts(download_path: str, cookies: str | None = None) -> tuple[dict, str | None]:
    ydl_opts = {
        "format": "best",
        "fixup": "never",
        "writethumbnail": True,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "0",
            },
            {
                "key": "FFmpegMetadata",
                "add_metadata": True,
            },
            {
                "key": "EmbedThumbnail",
            },
        ],
        "outtmpl": download_path,
    }
    cookiefile = None
    if cookies:
        cookiefile_fd, cookiefile = tempfile.mkstemp(suffix=".txt")
        with os.fdopen(cookiefile_fd, "w") as cookie_file:
            cookie_file.write(cookies)
        ydl_opts["cookiefile"] = cookiefile
    return ydl_opts, cookiefile


async def download_audio_from_video(
    download_path: str, url: str, cookies: str | None = None
):
    def _download_audio_from_video():
        ydl_opts, cookiefile = _build_ydl_opts(download_path, cookies)
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download(url)
        finally:
            if cookiefile:
                os.unlink(cookiefile)

    return await asyncio.to_thread(_download_audio_from_video)


async def extract_video_info(url: str, cookies: str | None = None):
    def _extract_video_info():
        ydl_opts = {}
        cookiefile = None
        if cookies:
            cookiefile_fd, cookiefile = tempfile.mkstemp(suffix=".txt")
            with os.fdopen(cookiefile_fd, "w") as cookie_file:
                cookie_file.write(cookies)
            ydl_opts["cookiefile"] = cookiefile
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                return ydl.extract_info(url, download=False)
        finally:
            if cookiefile:
                os.unlink(cookiefile)

    return await asyncio.to_thread(_extract_video_info)
