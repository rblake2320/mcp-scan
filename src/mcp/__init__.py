"""Minimal stub of the ``mcp`` package for testing purposes."""

from dataclasses import dataclass
from typing import Any, AsyncIterator, Tuple


class ClientSession:
    """Dummy async context manager used in tests."""

    def __init__(self, read: Any, write: Any) -> None:
        self.read = read
        self.write = write

    async def __aenter__(self) -> "ClientSession":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        pass

    async def initialize(self):
        raise NotImplementedError


@dataclass
class StdioServerParameters:
    command: str
    args: list[str] | None = None
    env: dict[str, str] | None = None


__all__ = ["ClientSession", "StdioServerParameters"]
