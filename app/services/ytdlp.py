import asyncio
import os
import tempfile

import yt_dlp


def _write_cookies_to_tempfile(cookies: str) -> str:
    fd, cookie_file_path = tempfile.mkstemp(suffix=".txt")
    with os.fdopen(fd, "w") as temp_file:
        temp_file.write(cookies)
    return cookie_file_path


def _build_ydl_opts(download_path: str, cookies: str | None = None) -> tuple[dict, str | None]:
    ydl_opts = {
        "format": "best",
        "fixup": "never",
        "noplaylist": True,
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
    cookie_file_path = None
    if cookies:
        cookie_file_path = _write_cookies_to_tempfile(cookies)
        ydl_opts["cookiefile"] = cookie_file_path
    return ydl_opts, cookie_file_path


async def download_audio_from_video(
    download_path: str, url: str, cookies: str | None = None
):
    def _download_audio_from_video():
        ydl_opts, cookie_file_path = _build_ydl_opts(download_path, cookies)
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download(url)
        finally:
            if cookie_file_path:
                os.unlink(cookie_file_path)

    return await asyncio.to_thread(_download_audio_from_video)


async def extract_video_info(url: str, cookies: str | None = None):
    def _extract_video_info():
        ydl_opts = {"noplaylist": True}
        cookie_file_path = None
        if cookies:
            cookie_file_path = _write_cookies_to_tempfile(cookies)
            ydl_opts["cookiefile"] = cookie_file_path
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                return ydl.extract_info(url, download=False)
        finally:
            if cookie_file_path:
                os.unlink(cookie_file_path)

    return await asyncio.to_thread(_extract_video_info)
