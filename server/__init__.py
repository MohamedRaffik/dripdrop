import os
from starlette import middleware
from starlette.applications import Starlette
from starlette.routing import Route, WebSocketRoute, Mount
from starlette.responses import FileResponse
from starlette.requests import Request
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.middleware import Middleware
from server.music_downloader import delete_job, get_grouping, download, process_job, get_artwork, listen_jobs, download_job, get_tags
from server.auth import login, create_account, admin_create_account, check_session, logout, AuthBackend
from server.db import database
from server.config import ENVIRONMENT


async def index(request: Request):
    path = request.path_params.get('path')
    if path == '':
        path = 'index.html'
    filepath = os.path.join(os.path.dirname(__file__), f'../app/build/{path}')
    if os.path.exists(filepath):
        return FileResponse(filepath)
    return FileResponse(os.path.join(os.path.dirname(__file__), f'../app/build/index.html'))

routes = [
    Route('/music/getArtwork', endpoint=get_artwork, methods=['GET']),
    Route('/music/processJob', endpoint=process_job, methods=['GET']),
    Route('/music/grouping', endpoint=get_grouping, methods=['GET']),
    Route('/music/getTags', endpoint=get_tags, methods=['POST']),
    Route('/music/download', endpoint=download, methods=['POST']),
    Route('/music/deleteJob', endpoint=delete_job, methods=['GET']),
    Route('/music/downloadJob', endpoint=download_job, methods=['GET']),
    WebSocketRoute('/music/listenJobs', endpoint=listen_jobs),

    Route('/auth/create', endpoint=create_account, methods=['POST']),
    Route('/auth/admin/create',
          endpoint=admin_create_account, methods=['POST']),
    Route('/auth/checkSession', endpoint=check_session, methods=['GET']),
    Route('/auth/logout', endpoint=logout, methods=['GET']),
    Route('/auth/login', endpoint=login, methods=['POST']),

    Route('/{path:path}', endpoint=index, methods=['GET'])
]

allowed_hosts = ["dripdrop.icu, www.dripdrop.icu"]

if ENVIRONMENT != 'production':
    allowed_hosts.append("localhost")

middleware = [
    # Middleware(SessionMiddleware, secret_key='driprandomdrop123',
    #            https_only=ENVIRONMENT == 'production'),
    Middleware(TrustedHostMiddleware, allowed_hosts=allowed_hosts),
    Middleware(AuthenticationMiddleware, backend=AuthBackend())
]

app = Starlette(routes=routes, middleware=middleware, on_startup=[
    database.connect], on_shutdown=[database.disconnect])
