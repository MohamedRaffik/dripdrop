from pydantic import BaseModel

from app.models import Response


class YtdlpCookiesResponse(Response):
    cookies: str


class UpdateYtdlpCookies(BaseModel):
    cookies: str
