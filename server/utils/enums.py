from enum import Enum


class RedisChannels(Enum):
    WORK_CHANNEL = 'WORK_CHANNEL'
    STARTED_MUSIC_JOB_CHANNEL = 'STARTED_MUSIC_JOB_CHANNEL'
    COMPLETED_MUSIC_JOB_CHANNEL = 'COMPLETED_MUSIC_JOB_CHANNEL'
    COMPLETED_YOUTUBE_SUBSCRIPTION_JOB_CHANNEL = 'COMPLETED_YOUTUBE_SUBSCRIPTION_JOB_CHANNEL'


class AuthScopes(Enum):
    AUTHENTICATED = 'authenticated'
    ADMIN = 'admin'
    API_KEY = 'api_key'


class RequestMethods(Enum):
    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'
    HEAD = 'HEAD'
