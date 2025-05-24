import builtins
from contextlib import asynccontextmanager

class AioFile:
    def __init__(self, f):
        self._f = f

    async def read(self):
        return self._f.read()

    async def write(self, data):
        self._f.write(data)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        self._f.close()

@asynccontextmanager
async def open(file, mode="r"):
    f = builtins.open(file, mode)
    try:
        yield AioFile(f)
    finally:
        f.close()
