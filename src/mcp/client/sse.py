from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator, Tuple, Any


@asynccontextmanager
async def sse_client(url: str, headers: dict[str, str] | None = None, timeout: int = 10) -> AsyncIterator[Tuple[Any, Any]]:
    """Yield dummy read/write objects for SSE clients."""
    yield (None, None)
