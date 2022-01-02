import traceback
from asgiref.sync import sync_to_async
from inspect import iscoroutinefunction
from server.database import db


def exception_handler(function):
    async def wrapper(*args, **kwargs):
        nonlocal function
        try:
            if not iscoroutinefunction(function):
                function = sync_to_async(function)
            return await function(*args, **kwargs)
        except:
            print(traceback.format_exc())
            return None
    return wrapper


def worker_task(function):
    async def wrapper(*args, **kwargs):
        if iscoroutinefunction(function):
            await db.connect()
            result = await function(*args, **kwargs)
            await db.disconnect()
            return result
        else:
            func = sync_to_async(function)
            return await func(*args, **kwargs)
    return wrapper
