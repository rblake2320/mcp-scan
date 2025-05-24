from contextlib import asynccontextmanager

class Response:
    def __init__(self, status: int = 200, text: str = "") -> None:
        self.status = status
        self._text = text

    async def text(self) -> str:
        return self._text

class ClientSession:
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass

    @asynccontextmanager
    async def post(self, url, headers=None, data=None):
        yield Response()
