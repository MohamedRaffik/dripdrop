from worker import AsyncioQueue
from server.db import database, music_jobs
from server.utils.enums import RedisChannels

queue = AsyncioQueue(RedisChannels.WORK_CHANNEL.value)


async def restart_jobs():
    query = music_jobs.select(music_jobs.c.id).where(music_jobs.c.completed ==
                                                     False, music_jobs.c.failed == False)
    async for hanging_job in database.iterate(query):
        job_id = hanging_job.get('id')
        await queue.enqueue('server.api.music.tasks.run_job', job_id)
