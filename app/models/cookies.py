from pydantic import BaseModel

from app.models import Response


class CookiesResponse(Response):
    content: str


class UpdateCookies(BaseModel):
    content: str
