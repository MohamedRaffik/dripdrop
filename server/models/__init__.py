import databases
import sqlalchemy
from datetime import datetime
from pydantic import BaseModel, SecretStr
from sqlalchemy.sql.expression import text
from sqlalchemy.ext.declarative import declarative_base
from server.config import config
from typing import Optional

DATABASE_URL = config.database_url
db = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()
Base = declarative_base(metadata=metadata)


class Users(Base):
    __tablename__ = "users"
    email = sqlalchemy.Column(sqlalchemy.String, primary_key=True)
    password = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    admin = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False)
    approved = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False)
    created_at = sqlalchemy.Column(
        sqlalchemy.dialects.postgresql.TIMESTAMP(timezone=True),
        server_default=text("NOW()"),
    )


class User(BaseModel):
    email: str
    password: SecretStr
    admin: bool
    approved: bool
    created_at: datetime


SessionUser = Optional[User]


class AuthenticatedUser(User):
    authenticated: bool


class AdminUser(AuthenticatedUser):
    admin: bool


class Sessions(Base):
    __tablename__ = "sessions"
    id = sqlalchemy.Column(sqlalchemy.String, primary_key=True)
    user_email = sqlalchemy.Column(
        sqlalchemy.ForeignKey(Users.email, onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    created_at = sqlalchemy.Column(
        sqlalchemy.dialects.postgresql.TIMESTAMP(timezone=True),
        server_default=text("NOW()"),
    )


class Session(BaseModel):
    id: str
    user_email: str
    created_at: datetime


class MusicJobs(Base):
    __tablename__ = "music_jobs"
    id = sqlalchemy.Column(sqlalchemy.String, primary_key=True)
    user_email = sqlalchemy.Column(
        sqlalchemy.ForeignKey(Users.email, onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    filename = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    youtube_url = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    artwork_url = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    artist = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    album = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    grouping = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    completed = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False)
    failed = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False)
    created_at = sqlalchemy.Column(
        sqlalchemy.dialects.postgresql.TIMESTAMP(timezone=True),
        server_default=text("NOW()"),
    )


class MusicJob(BaseModel):
    id: str
    user_email: str
    filename: Optional[str] = ""
    youtube_url: Optional[str]
    artwork_url: Optional[str]
    title: str
    artist: str
    album: str
    grouping: Optional[str]
    completed: bool
    failed: bool
    created_at: datetime


class GoogleAccounts(Base):
    __tablename__ = "google_accounts"
    email = sqlalchemy.Column(sqlalchemy.String, primary_key=True)
    user_email = sqlalchemy.Column(
        sqlalchemy.ForeignKey(Users.email, onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    access_token = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    refresh_token = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    expires = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    subscriptions_loading = sqlalchemy.Column(
        sqlalchemy.Boolean, nullable=False, server_default="0"
    )
    created_at = sqlalchemy.Column(
        sqlalchemy.dialects.postgresql.TIMESTAMP(timezone=True),
        server_default=text("NOW()"),
    )
    last_updated = sqlalchemy.Column(
        sqlalchemy.dialects.postgresql.TIMESTAMP(timezone=True),
        server_default=text("NOW()"),
    )


class GoogleAccount(BaseModel):
    email: str
    user_email: str
    access_token: str
    refresh_token: str
    expires: int
    subscriptions_loading: bool
    created_at: datetime
    last_updated: datetime


youtube_channels = sqlalchemy.Table(
    "youtube_channels",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.String, primary_key=True),
    sqlalchemy.Column("title", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("thumbnail", sqlalchemy.String, nullable=True),
    sqlalchemy.Column("upload_playlist_id", sqlalchemy.String, nullable=True),
    sqlalchemy.Column(
        "created_at",
        sqlalchemy.dialects.postgresql.TIMESTAMP(timezone=True),
        server_default=text("NOW()"),
    ),
    sqlalchemy.Column(
        "last_updated",
        sqlalchemy.dialects.postgresql.TIMESTAMP(timezone=True),
        server_default=text("NOW()"),
        server_onupdate=text("NOW()"),
    ),
)


class YoutubeChannel(BaseModel):
    id: str
    title: str
    thumbnail: Optional[str]
    upload_playlist_id: Optional[str]
    created_at: datetime
    last_updated: datetime


youtube_subscriptions = sqlalchemy.Table(
    "youtube_subscriptions",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.String, primary_key=True),
    sqlalchemy.Column(
        "channel_id",
        sqlalchemy.ForeignKey(
            youtube_channels.c.id, onupdate="CASCADE", ondelete="CASCADE"
        ),
        nullable=False,
    ),
    sqlalchemy.Column(
        "email",
        sqlalchemy.ForeignKey(
            GoogleAccounts.email, onupdate="CASCADE", ondelete="CASCADE"
        ),
        nullable=False,
    ),
    sqlalchemy.Column(
        "published_at", sqlalchemy.dialects.postgresql.TIMESTAMP(timezone=True)
    ),
    sqlalchemy.Column(
        "created_at",
        sqlalchemy.dialects.postgresql.TIMESTAMP(timezone=True),
        server_default=text("NOW()"),
    ),
)


class YoutubeSubscription(BaseModel):
    id: str
    channel_id: str
    email: str
    published_at: datetime
    created_at: datetime


youtube_video_categories = sqlalchemy.Table(
    "youtube_video_categories",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String, nullable=False),
    sqlalchemy.Column(
        "created_at",
        sqlalchemy.dialects.postgresql.TIMESTAMP(timezone=True),
        server_default=text("NOW()"),
    ),
)


class YoutubeVideoCategory(BaseModel):
    id: int
    name: str
    created_at: datetime


youtube_videos = sqlalchemy.Table(
    "youtube_videos",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.String, primary_key=True),
    sqlalchemy.Column("title", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("thumbnail", sqlalchemy.String, nullable=False),
    sqlalchemy.Column(
        "channel_id",
        sqlalchemy.ForeignKey(
            youtube_channels.c.id, onupdate="CASCADE", ondelete="CASCADE"
        ),
        nullable=False,
    ),
    sqlalchemy.Column("published_at", sqlalchemy.TIMESTAMP(timezone=True)),
    sqlalchemy.Column(
        "category_id",
        sqlalchemy.ForeignKey(
            youtube_video_categories.c.id, onupdate="CASCADE", ondelete="CASCADE"
        ),
        nullable=False,
    ),
    sqlalchemy.Column(
        "created_at",
        sqlalchemy.dialects.postgresql.TIMESTAMP(timezone=True),
        server_default=text("NOW()"),
    ),
)


class YoutubeVideo(BaseModel):
    id: str
    title: str
    thumbnail: str
    channel_id: str
    published_at: datetime
    category_id: int
    created_at: datetime
