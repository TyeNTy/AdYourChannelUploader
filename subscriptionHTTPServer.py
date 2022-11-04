from http.server import HTTPServer
from socketserver import BaseRequestHandler
from typing import Any, Callable
from typing_extensions import Self


class SubscriptionHandlerHTTPServer(HTTPServer):
    def __init__(self: Self, server_address: tuple[str, int], RequestHandlerClass: Callable[[Any, Any, Self], BaseRequestHandler], bind_and_activate: bool = ...) -> None:
        super().__init__(server_address, RequestHandlerClass, bind_and_activate)