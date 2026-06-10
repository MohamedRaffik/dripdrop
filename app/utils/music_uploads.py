import re

from fastapi import HTTPException, status

from app.services import s3
from app.settings import settings


def parse_music_upload_job_id(upload_key: str) -> str | None:
    match = re.match(
        rf"^{re.escape(settings.aws_s3_music_folder)}/([^/]+)/old/.+",
        upload_key,
    )
    return match.group(1) if match else None


async def validate_music_upload_key(upload_key: str) -> str:
    job_id = parse_music_upload_job_id(upload_key)
    if not job_id:
        raise HTTPException(
            detail="Invalid upload_key.",
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        )
    if not await s3.object_exists(filename=upload_key):
        raise HTTPException(
            detail="Uploaded file not found.",
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        )
    return job_id
