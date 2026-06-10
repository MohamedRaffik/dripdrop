from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, HttpUrl, field_validator

from app.models import Response


class MetadataResponse(Response):
    grouping: Optional[str] = None
    title: Optional[str] = None
    artist: Optional[str] = None
    album: Optional[str] = None


class ResolvedArtworkResponse(Response):
    resolved_artwork_url: str


class MusicJobUpdateResponse(Response):
    id: str
    status: Literal["STARTED", "COMPLETED"]


class TagsResponse(Response):
    title: Optional[str] = None
    artist: Optional[str] = None
    album: Optional[str] = None
    grouping: Optional[str] = None
    artwork_url: Optional[str] = None


class PresignUploadRequest(BaseModel):
    filename: str
    content_type: str


class PresignUploadResponse(Response):
    job_id: str
    upload_url: str
    key: str
    public_url: str


class CreateMusicJob(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    job_id: Optional[str] = None
    upload_key: Optional[str] = None
    video_url: Optional[HttpUrl] = None
    artwork_url: Optional[str] = None
    title: str
    artist: str
    album: str
    grouping: Optional[str] = None
    upload_to_webdav: Optional[bool] = None

    @field_validator("grouping", mode="before")
    @classmethod
    def empty_str_to_none(cls, value):
        if value == "":
            return None
        return value


class MusicJobResponse(Response):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_email: str
    title: str
    artist: str
    album: str
    grouping: str | None = None
    artwork_url: str | None = None
    artwork_filename: str | None = None
    original_filename: str | None = None
    filename_url: str | None = None
    video_url: str | None = None
    download_filename: str | None = None
    download_url: str | None = None
    completed: datetime | None = None
    failed: datetime | None = None


class MusicJobListResponse(Response):
    jobs: list[MusicJobResponse]
    total_pages: int
