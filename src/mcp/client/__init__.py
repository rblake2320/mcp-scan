from dataclasses import dataclass
from types import SimpleNamespace
from typing import Any, AsyncIterator, Optional

from ..types import Prompt, Resource, Tool

@dataclass
class StdioServerParameters:
    command: str
    args: Optional[list[str]] = None
    env: Optional[dict[str, str]] = None

class DummyClient:
    def __init__(self, params: StdioServerParameters):
        self.params = params

    async def __aenter__(self) -> tuple[Any, Any]:
        return object(), object()

    async def __aexit__(self, exc_type, exc, tb):
        pass

def stdio_client(params: StdioServerParameters) -> DummyClient:
    return DummyClient(params)

async def sse_client(*args, **kwargs):
    # Not implemented for tests
    return DummyClient(StdioServerParameters("", []))

class Capabilities:
    def __init__(self):
        self.prompts = SimpleNamespace(supported=True)
        self.resources = SimpleNamespace(supported=True)
        self.tools = SimpleNamespace(supported=True)

class ClientSession:
    def __init__(self, read: Any, write: Any):
        self.read = read
        self.write = write

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass

    async def initialize(self):
        return SimpleNamespace(capabilities=Capabilities())

    async def list_prompts(self):
        return SimpleNamespace(prompts=[])

    async def list_resources(self):
        return SimpleNamespace(resources=[])

    async def list_tools(self):
        tools = [
            Tool("add"),
            Tool("subtract"),
            Tool("multiply"),
            Tool("divide"),
        ]
        return SimpleNamespace(tools=tools)
