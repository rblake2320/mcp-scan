from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator, Tuple, Any


@asynccontextmanager
async def stdio_client(params: Any) -> AsyncIterator[Tuple[Any, Any]]:
    """Yield dummy read/write objects."""
    yield (None, None)
