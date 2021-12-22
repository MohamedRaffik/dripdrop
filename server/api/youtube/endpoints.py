from starlette.authentication import requires
from starlette.requests import Request
from starlette.responses import RedirectResponse

from server.api.youtube import google_api
from server.api.auth.auth_backend import SessionHandler
from server.api.youtube.tasks import update_subscriptions_job
from server.config import SERVER_URL
from server.db import database, users, sessions, google_accounts
from server.utils.enums import AuthScopes
from server.utils.wrappers import endpoint_handler
from server.worker import Worker


@requires([AuthScopes.AUTHENTICATED])
def get_email(request: Request):
    user = request.user
