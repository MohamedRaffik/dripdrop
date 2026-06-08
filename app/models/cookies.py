from pydantic import BaseModel

from app.models import Response


class CookiesResponse(Response):
    cookies: str


class UpdateCookies(BaseModel):
    cookies: str
