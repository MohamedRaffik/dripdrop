import traceback
from inspect import iscoroutinefunction
from starlette.requests import Request
from starlette.responses import Response


def endpoint_handler():
    def decorator(function):
        async def wrapper(request: Request):
            request.auth
            try:
                if iscoroutinefunction(function):
                    return await function(request)
                else:
                    return function(request)
            except:
                print(traceback.format_exc())
                return Response(None, 400)
        return wrapper
    return decorator
