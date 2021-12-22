from starlette.routing import Mount, Route

from server.utils.enums import RequestMethods


routes = [
    Mount('/youtube', routes=[])
]
