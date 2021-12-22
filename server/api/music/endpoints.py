import asyncio
import os
import traceback
import uuid

from asyncio.tasks import Task
from sqlalchemy.sql.expression import desc
from typing import Union
from websockets.exceptions import ConnectionClosedOK
from yt_dlp.utils import sanitize_filename

from starlette.authentication import requires
from starlette.concurrency import run_in_threadpool
from starlette.datastructures import UploadFile
from starlette.requests import Request
from starlette.responses import FileResponse, JSONResponse, Response
from starlette.websockets import WebSocket, WebSocketDisconnect

from server.api.music.tasks import run_job, read_tags
from server.db import database, music_jobs
from server.redis import RedisChannels, subscribe, redis
from server.utils.mp3dl import extract_info
from server.utils.imgdl import download_image
from server.utils.wrappers import endpoint_handler
from server.utils.helpers import convert_db_response
from server.utils.enums import AuthScopes
from server.worker import Worker


@requires([AuthScopes.AUTHENTICATED])
@endpoint_handler()
async def get_grouping(request: Request):
    youtube_url = request.query_params.get('youtube_url')
    uploader = await run_in_threadpool(extract_info, youtube_url)
    return JSONResponse({'grouping': uploader})


@requires([AuthScopes.AUTHENTICATED])
@endpoint_handler()
async def get_artwork(request: Request):
    artwork_url = request.query_params.get('artwork_url')
    artwork_url = await run_in_threadpool(download_image, artwork_url, False)
    return JSONResponse({'artwork_url': artwork_url})


@requires([AuthScopes.AUTHENTICATED])
@endpoint_handler()
async def get_tags(request: Request):
    form = await request.form()
    file: Union[UploadFile, None] = form.get('file')

    if not file:
        return Response(None, 400)

    tags = await run_in_threadpool(read_tags, await file.read(), file.filename)
    return JSONResponse(tags)


@requires([AuthScopes.AUTHENTICATED])
async def listen_jobs(websocket: WebSocket):
    tasks: list[Task] = []
    try:
        await websocket.accept()
        query = music_jobs.select().where(music_jobs.c.user_id ==
                                          websocket.user.id).order_by(desc(music_jobs.c.created_at))
        jobs = await database.fetch_all(query)
        await websocket.send_json({
            'type': 'ALL',
            'jobs': [convert_db_response(job) for job in jobs]
        })

        tasks.extend([
            asyncio.create_task(
                subscribe(RedisChannels.STARTED_MUSIC_JOB_CHANNEL, websocket)),
            asyncio.create_task(
                subscribe(RedisChannels.COMPLETED_MUSIC_JOB_CHANNEL, websocket)),
            asyncio.create_task(
                subscribe(RedisChannels.WORK_CHANNEL, websocket))
        ])

        while True:
            await websocket.send_json({})
            await asyncio.sleep(1)

    except Exception as e:
        if not isinstance(e, WebSocketDisconnect) and not isinstance(e, ConnectionClosedOK):
            print(traceback.format_exc())
        for task in tasks:
            task.cancel()
        await websocket.close()


@requires([AuthScopes.AUTHENTICATED])
@endpoint_handler()
async def download(request: Request):
    job_id = str(uuid.uuid4())
    form = await request.form()
    youtube_url = form.get('youtube_url')
    file: Union[UploadFile, None] = form.get('file')
    artwork_url = form.get('artwork_url')
    title = form.get('title')
    artist = form.get('artist')
    album = form.get('album')
    grouping = form.get('grouping')

    if not youtube_url and not file:
        return Response(None, 400)

    filename = file.filename if file else None

    job_info = {
        'job_id': job_id,
        'filename': filename,
        'youtube_url': youtube_url,
        'artwork_url': artwork_url,
        'title': title,
        'artist': artist,
        'album': album,
        'grouping': grouping
    }

    async with database.transaction():
        query = music_jobs.insert().values(
            **job_info,
            username=request.user.display_name,
            completed=False,
            failed=False,
        )
        await database.execute(query)

    await redis.publish(RedisChannels.STARTED_MUSIC_JOB_CHANNEL.value, job_id)
    Worker.add_job(run_job, job_id, file)
    return JSONResponse({'job': job_info}, status_code=202)


@requires([AuthScopes.AUTHENTICATED])
@endpoint_handler()
@database.transaction()
async def delete_job(request: Request):
    job_id = request.query_params.get('job_id')
    query = music_jobs.delete().where(music_jobs.c.username ==
                                      request.user.display_name, music_jobs.c.job_id == job_id)
    await database.execute(query)
    try:
        await asyncio.create_subprocess_shell(f'rm -rf music_jobs/{job_id}')
    except:
        pass
    return Response(None)


@requires([AuthScopes.AUTHENTICATED])
@endpoint_handler()
async def download_job(request: Request):
    job_id = request.query_params.get('job_id')
    query = music_jobs.select().order_by(desc(music_jobs.c.started))
    job = await database.fetch_one(query)
    filename = sanitize_filename(f'{job.get("title")} {job.get("artist")}.mp3')
    file_path = os.path.join('jobs', job_id, filename)

    if not os.path.exists(file_path):
        async with database.transaction():
            query = music_jobs.update().where(music_jobs.c.username == request.user.display_name,
                                              music_jobs.c.job_id == job_id).values(failed=True)
            await database.execute(query)
        await redis.publish(RedisChannels.COMPLETED_JOB_CHANNEL.value, job_id)
        return Response(None, 404)

    return FileResponse(os.path.join('jobs', job_id, filename), filename=filename)
