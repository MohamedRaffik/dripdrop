import logging
import re
import traceback
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import HttpUrl

from app.dependencies import get_authenticated_user
from app.models.music import (
    MetadataResponse,
    PresignUploadRequest,
    PresignUploadResponse,
    ResolvedArtworkResponse,
    TagsRequest,
    TagsResponse,
)
from app.services import s3
from app.routes.music.jobs import router as jobs_router
from app.services import audiotags, google, imagedownloader, ytdlp
from app.utils.music_uploads import build_temp_upload_key, validate_temp_upload_key
from app.utils.youtube import parse_youtube_video_id

logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/music",
    tags=["Music"],
    dependencies=[Depends(get_authenticated_user)],
    responses={status.HTTP_401_UNAUTHORIZED: {}},
)
router.include_router(jobs_router)


@router.get(
    "/metadata",
    response_model=MetadataResponse,
    responses={status.HTTP_400_BAD_REQUEST: {"description": "Unable to get metadata."}},
)
async def get_metadata(video_url: Annotated[HttpUrl, Query()]):
    try:
        actual_video_url = video_url.unicode_string()
        video_info = await ytdlp.extract_video_info(url=actual_video_url)
        metadata = ytdlp.parse_video_metadata(video_info)
        if "youtube.com" in actual_video_url:
            video_id = parse_youtube_video_id(actual_video_url)
            grouping = await google.get_video_uploader(video_id=video_id)
        else:
            grouping = video_info.get("uploader")
        return MetadataResponse(grouping=grouping, **metadata)
    except Exception:
        logger.exception(traceback.format_exc())
        raise HTTPException(
            detail="Unable to get metadata.", status_code=status.HTTP_400_BAD_REQUEST
        )


@router.get(
    "/artwork",
    response_model=ResolvedArtworkResponse,
    responses={status.HTTP_400_BAD_REQUEST: {"description": "Unable to get artwork."}},
)
async def get_artwork(artwork_url: Annotated[HttpUrl, Query()]):
    try:
        resolved_artwork_url = await imagedownloader.resolve_artwork(
            artwork=artwork_url.unicode_string()
        )
        return ResolvedArtworkResponse(resolved_artwork_url=resolved_artwork_url)
    except Exception:
        logger.exception(traceback.format_exc())
        raise HTTPException(
            detail="Unable to get artwork.", status_code=status.HTTP_400_BAD_REQUEST
        )


@router.post("/uploads/presign", response_model=PresignUploadResponse)
async def presign_upload(request: PresignUploadRequest):
    if not re.match("^audio/", request.content_type):
        raise HTTPException(
            detail="File is incorrect format.",
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        )
    upload_id = str(uuid.uuid4())
    key = build_temp_upload_key(upload_id=upload_id, filename=request.filename)
    upload_url = await s3.generate_presigned_upload_url(
        filename=key,
        content_type=request.content_type,
    )
    return PresignUploadResponse(
        upload_url=upload_url,
        key=key,
        public_url=s3.resolve_url(filename=key),
    )


@router.post("/tags", response_model=TagsResponse)
async def get_tags(request: TagsRequest):
    await validate_temp_upload_key(upload_key=request.upload_key)
    file_bytes = await s3.download_file(filename=request.upload_key)
    filename = request.upload_key.rsplit("/", 1)[-1]
    tags = await audiotags.AudioTags.read_tags(file=file_bytes, filename=filename)
    return TagsResponse(
        title=tags.title,
        artist=tags.artist,
        album=tags.album,
        grouping=tags.grouping,
        artwork_url=tags.artwork_url,
    )
