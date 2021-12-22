import bcrypt
import re
import uuid

from starlette.authentication import requires
from starlette.middleware import sessions
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response, JSONResponse

from server.api.auth.auth_backend import SessionHandler
from server.api.youtube import google_api
from server.api.youtube.tasks import update_subscriptions_job
from server.config import ENVIRONMENT, SERVER_URL
from server.db import users, database, sessions, google_accounts
from server.utils.enums import AuthScopes
from server.utils.wrappers import endpoint_handler
from server.worker import Worker


async def create_new_account(email: str, password: str):
    if not email or not password:
        raise ValueError('email or Password not supplied.')

    email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

    if not re.match(email_regex, email):
        raise ValueError('Email address is not valid')

    if len(password) < 8:
        raise ValueError('Password length is too short')

    query = users.select().where(users.c.email == email)
    account = await database.fetch_one(query)

    if account:
        raise ValueError(f'Account with email `{email}` exists.')

    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    query = users.insert().values(
        id=str(uuid.uuid4()),
        email=email,
        password=hashed_pw.decode('utf-8'),
        admin=False,
        approved=False
    )
    await database.execute(query)


@requires([AuthScopes.AUTHENTICATED])
@endpoint_handler()
async def check_session(request: Request):
    email = request.user.display_name
    admin = AuthScopes.ADMIN in request.auth.scopes
    return JSONResponse({
        'email': email,
        'admin': admin,
    }, 200)


@endpoint_handler()
async def login(request: Request):
    form = await request.json()

    email = form.get('email')
    password = form.get('password')

    query = users.select().where(users.c.email == email)
    account = await database.fetch_one(query)

    if not account:
        return JSONResponse({'error': 'Account not found.'}, 400)

    if not bcrypt.checkpw(password.encode('utf-8'), account.get('password').encode('utf-8')):
        return JSONResponse({'error': 'email or Password is incorrect.'}, 400)

    if not account.get('approved'):
        return JSONResponse({'error': 'User has not been approved.'}, 401)

    session_id = str(uuid.uuid4())
    query = sessions.insert().values(id=session_id, user_id=account.get('id'))
    await database.execute(query)

    response = JSONResponse({
        'email': email,
        'admin': account.get('admin'),
    })

    TWO_WEEKS_EXPIRATION = 14*24*60*60

    response.set_cookie(
        'session',
        SessionHandler.encrypt({'id': session_id}),
        max_age=TWO_WEEKS_EXPIRATION,
        expires=TWO_WEEKS_EXPIRATION,
        httponly=True,
        secure=ENVIRONMENT == 'production'
    )

    return response


@requires([AuthScopes.AUTHENTICATED])
@endpoint_handler()
@database.transaction()
async def logout(request: Request):
    response = Response(None, 200)
    response.set_cookie('session', max_age=-1, expires=-1)
    return response


@endpoint_handler()
@database.transaction()
async def create_account(request: Request):
    form = await request.json()
    email = form.get('email')
    password = form.get('password')

    try:
        await create_new_account(email, password)
    except ValueError as e:
        return JSONResponse({'error': e.__str__()}, 400)

    return JSONResponse({'email': email, 'admin': False}, 201)


@requires([AuthScopes.ADMIN])
@endpoint_handler()
@database.transaction()
async def admin_create_account(request: Request):
    form = await request.json()
    email = form.get('email')
    password = form.get('password')

    try:
        await create_new_account(email, password)
    except ValueError as e:
        return JSONResponse({'error': e.message}, 400)

    return Response({'email': email, 'admin': False}, 201)


@requires([AuthScopes.AUTHENTICATED])
@endpoint_handler()
@database.transaction()
async def google_oauth2(request: Request):
    if request.query_params.get('error', None):
        return RedirectResponse('/')

    session_id = request.query_params.get('state', None)

    if not session_id:
        return RedirectResponse('/')

    query = SessionHandler.select().where(sessions.c.id == session_id)
    session = await database.fetch_one(query)

    if not session:
        return RedirectResponse('/')

    email = session.get('email')

    query = users.select().where(users.c.email == email)
    user = await database.fetch_one(query)

    if not user:
        return RedirectResponse('/')

    code = request.query_params.get('code')
    tokens = await google_api.get_oauth_tokens(f'{SERVER_URL}/google/oauth2', code)
    email = await google_api.get_user_email(tokens.get('access_token'))

    query = google_accounts.insert().values(
        email=email,
        access_token=tokens.get('access_token'),
        refresh_token=tokens.get('refresh_token'),
        expires=tokens.get('expires_in'),
    )
    await database.execute(query)
    job = await Worker.add_job(update_subscriptions_job, email)
    # ADD update video job
    # job.add_done_callback()
    return RedirectResponse('/ytCollections')
