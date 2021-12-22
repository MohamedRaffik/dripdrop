import asyncio

from sqlalchemy.sql.expression import text
from typing import Union

from server.api.youtube import google_api
from server.db import (
    database,
    google_accounts,
    youtube_subscriptions,
    youtube_channels,
    youtube_video_category,
    youtube_video_categories,
    youtube_jobs
)
from server.utils.wrappers import exception_handler


async def update_video_categories():
    async def update_category(category):
        category_id = category['id']
        category_title = category['snippet']['title']
        query = youtube_video_categories.select().where(
            youtube_video_categories.c.id == category_id)
        existing_category = await database.fetch_one(query)

        if existing_category and existing_category.get('name') == category_title:
            query = youtube_video_category.delete().where(
                youtube_video_category.c.category_id == category_id)
            await database.execute(query)
            query = youtube_video_categories.update().where(
                youtube_video_categories.c.name == category_title)

    video_categories = await google_api.get_video_categories()
    await asyncio.gather(update_category(category) for category in video_categories)


async def update_subscription(email: str, subscription):
    subscription_id = subscription['id']
    subscription_channel_id = subscription['snippet']['channelId']
    query = youtube_subscriptions.select().where(
        youtube_subscriptions.c.id == subscription['id'])
    existing_subscription = await database.fetch_one(query)

    if existing_subscription:
        query = youtube_video_category.update().values(
            last_updated=text('NOW()')).where(id=subscription_id)
        await database.execute(query)
    else:
        query = youtube_video_category.insert().values(
            id=subscription_id,
            channel_id=subscription_channel_id,
            email=email
        )
        await database.execute(query)
        query = youtube_channels.select().where(
            id=subscription_channel_id)
        existing_channel = await database.fetch_one(query)

        if not existing_channel:
            return subscription_channel_id

    return None


async def update_user_subscriptions(email: str, access_token: str):
    async for subscriptions in google_api.get_user_subscriptions(access_token):
        new_channel_ids = await asyncio.gather(
            update_subscription(email, subscription)
            for subscription in subscriptions
            if subscription['snippet']['resourceId']['kind'] == 'youtube#channel'
        )
        new_channels = await google_api.get_channels_info(filter(new_channel_ids))
        query = youtube_channels.insert()
        values = [
            {
                'id': channel['id'],
                'title': channel['snippet']['title'],
                'upload_playlist_id': channel['contentDetails']['relatedPlaylists']['uploads'],
                'thumbnail': channel['snippet']['thumbnails']['default']['url']
            }
            for channel in new_channels
        ]
        await database.execute_many(query, values)
        yield subscriptions


@exception_handler()
async def update_subscriptions_job(email: Union[str, None]):
    # await update_video_categories()

    if email:
        query = google_accounts.select().where(google_accounts.c.email)
    else:
        query = google_accounts.select()

    async for account in database.iterate(query):
        email = account.get('email')
        query = youtube_jobs.select().where(youtube_jobs.c.email == email)
        job = await database.fetch_one(query)

        if job:
            continue

        query = youtube_jobs.insert().values(email=email)
        await database.execute(query)

        # ADD LOGIC TO DETERMINE TOKEN REFRESH

        # await update_user_subscriptions(account.get('access_token'))

        query = youtube_jobs.delete().where(youtube_jobs.c.email == email)
        await database.execute(query)
