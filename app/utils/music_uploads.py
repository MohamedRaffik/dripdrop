import re

from fastapi import HTTPException, status

from app.services import s3
from app.settings import settings


def music_temp_folder() -> str:
    return f"{settings.aws_s3_music_folder}/temp"


def build_temp_upload_key(upload_id: str, filename: str) -> str:
    return f"{music_temp_folder()}/{upload_id}/{filename}"


def build_job_audio_key(job_id: str, filename: str) -> str:
    return f"{settings.aws_s3_music_folder}/{job_id}/old/{filename}"


def is_temp_upload_key(upload_key: str) -> bool:
    return bool(
        re.match(rf"^{re.escape(music_temp_folder())}/[^/]+/.+", upload_key)
    )


async def validate_temp_upload_key(upload_key: str):
    if not is_temp_upload_key(upload_key):
        raise HTTPException(
            detail="Invalid upload_key.",
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        )
    if not await s3.object_exists(filename=upload_key):
        raise HTTPException(
            detail="Uploaded file not found.",
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        )
