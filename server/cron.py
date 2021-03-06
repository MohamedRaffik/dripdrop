import logging
from typing import Callable
from croniter import croniter
from datetime import datetime, timezone, timedelta
from rq.registry import ScheduledJobRegistry
from server.config import config
from server.redis import redis
from server.rq import queue
from server.tasks.music import cleanup_jobs
from server.tasks.youtube import (
    update_active_channels,
    update_youtube_video_categories,
    update_subscriptions,
    channel_cleanup,
)

scheduled_registry = ScheduledJobRegistry(queue=queue)


def run_crons():
    video_categories_job = queue.enqueue(update_youtube_video_categories, args=(True,))
    active_channels_job = queue.enqueue_call(
        update_active_channels, depends_on=video_categories_job
    )
    update_subscriptions_job = queue.enqueue_call(
        update_subscriptions, depends_on=active_channels_job
    )
    channel_cleanup_job = queue.enqueue_call(
        channel_cleanup, depends_on=update_subscriptions_job
    )
    queue.enqueue_call(cleanup_jobs, depends_on=channel_cleanup_job)


def cron_job(cron_string: str, function: Callable, args=(), kwargs={}):
    est = timezone(timedelta(hours=-5))
    cron = croniter(cron_string, datetime.now(est))
    cron.get_next()
    next_run_time = cron.get_current(ret_type=datetime)
    logging.info(f"Scheduling {function} to run at {next_run_time}")
    job = queue.enqueue_at(
        next_run_time,
        function,
        args=args,
        kwargs=kwargs,
    )
    queue.enqueue_call(
        "server.cron.cron_job",
        args=(cron_string, function),
        kwargs={"args": args, "kwargs": kwargs},
        depends_on=job,
    )


async def cron_start():
    if config.env == "production":
        crons_added = await redis.get("crons_added")
        if not crons_added:
            await redis.set("crons_added", 1)

            for job_id in scheduled_registry.get_job_ids():
                logging.info(f"Removing Job: {job_id}")
                scheduled_registry.remove(job_id, delete_job=True)

            cron_job(
                "0 0 * * *",
                update_youtube_video_categories,
                args=(True,),
            )
            cron_job("0 0 * * *", cleanup_jobs)
            cron_job("0 1 * * *", update_active_channels)
            cron_job("0 3 * * *", update_subscriptions)
            cron_job("0 5 * * sun", channel_cleanup)


async def cron_end():
    if config.env == "production":
        await redis.delete("crons_added")
